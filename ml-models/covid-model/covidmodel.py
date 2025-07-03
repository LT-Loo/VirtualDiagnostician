import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from torch.utils.data import Dataset, DataLoader, random_split
import os, cv2, json
import numpy as np
from pathlib import Path
from tqdm import tqdm

PATIENT_INFO_KEYS = ["age", "sex_F", "weight", "height", "bmi"]           

VITAL_SIGN_KEYS   = [                                                      
    "respiratory_rate", "pulse", "body_temperature",
    "systolic_bp", "diastolic_bp", "oxygen_saturation_without_ox"
]

SYMPTOM_KEYS      = [                                                      
    "Wheezing", "Vomitting", "Sore_throat", "Skin_rash", "Running_nose",
    "Other", "Nausea", "Muscle_pain", "Lymphadenopathy", "Joint_pain",
    "Headache", "Fever", "Fatigue", "Earache", "Dyspnea", "Diarrhea",
    "Decreased_consciousness", "Coughing", "Confusion", "Chest_pain",
    "AnosmiaHyposmia", "AgeusiaDysgeusia", "Abdominal_pain"
]

COMORBIDITY_KEYS  = [                                                  
    "Stroke", "Renal_disease", "None_of_the_above", "Neurological_condition",
    "Malignancy", "Liver_disease", "Hypertonia",
    "History_of_drug_or_alcohol_abuse", "Diabetes_Mellitus",
    "Chronic_cardiovascular_disease", "Autoimmune_disease",
    "Adipositas_BMI_30", "AIDSHIV"
]

LAB_FINDING_KEYS  = [                                                      
    "CRP", "LDH", "leucocytes", "lymphocytes", "absolute_lymphocytes",
    "hemoglobin", "thrombocytes", "pH", "pO2", "pCO2", "HCO3"
]

OUTCOME_KEYS      = [                                                     
    "length_of_stay_total", "length_of_stay_ICU", "length_of_stay_general_ward",
    "duration_oxygen_therapy",
    "outcome_status_d0", "outcome_status_d1", "outcome_status_d3",
    "outcome_status_d5", "outcome_status_d7", "outcome_status_d30"
]


class patientDataset(Dataset):
    def __init__(self, rootDir, frameCount = 16, resize = (112, 112), ext = "*.mp4"):
        super().__init__()
        self.datafile = Path(rootDir)
        self.frameCount = frameCount
        self.resize = resize
        
        # Get videos
        self.scans = []
        for patientfile in sorted(self.datafile.glob("*/**/*_record")):            
            for videopath in sorted(patientfile.rglob(ext)):
                # print(videopath)
                patientID = videopath.stem.split("_")[-2]
                # print(patientID)
                side = "L" if "_L" in str(videopath) else "R"
                self.scans.append((patientID, videopath, side))

        # Colour transform: BGR -> RGB -> Grayscale
        self.toTensor = transforms.Compose([
            transforms.ToPILImage(), transforms.Resize(resize),
            transforms.Grayscale(num_output_channels = 3),
            transforms.ToTensor(), transforms.Normalize(mean = [0.5], std = [0.5])
        ])

    def __len__(self): return len(self.scans)
    
    def __getitem__(self, index):
        patientID, videoPath, side = self.scans[index]

        videoTensor = self.readVideo(videoPath)
        clinicRecord = self.readClinical(patientID)
        label = self.readLabel(patientID)
        # label = 0

        meta = dict(patientID = patientID, videoPath = str(videoPath), lungSide = side)

        return videoTensor, clinicRecord, label, patientID
    
    def readVideo(self, videoPath):
        # Read and convert video
        cap = cv2.VideoCapture(str(videoPath))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Split videos into 16 frames evenly
        index = np.linspace(0, total - 1, self.frameCount).astype(int)
        frames = []

        for i in range(total):
            ret, frame = cap.read()
            if not ret: break
            if i in index:
                frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(self.toTensor(frameRGB))

        cap.release()

        # Duplicate last frame if video shorter than expected
        while len(frames) < self.frameCount:
            frames.append(frames[-1].clone())
        
        video = torch.stack(frames) # [T, 1, H, W]

        return video
    
    def readClinical(self, patientID):
        # Flatten nested JSON into numeric vector
        jsonPath = self.datafile / ("patient_" + patientID) / ("patient_" + patientID + "_record") / "clinical_data.json"
        data = json.load(open(jsonPath))

        flat = []

        def safeFloat(val):
            if isinstance(val, (int, float)): return float(val)
            elif isinstance(val, str):
                try: return float(val)
                except ValueError: return 0.0
            elif val is None: return 0.0
            return 0.0

        info = data["patient_info"]
        flat.extend([
            safeFloat(info.get("age")),
            1.0 if info.get("sex") == "F" else 0.0,
            safeFloat(info.get("weight")),
            safeFloat(info.get("height")),
            safeFloat(info.get("bmi"))
        ])
        
        # for section in ["vital_signs", "symptoms", "comorbidities", "lab_findings"]:
        #     values = data.get(section, {})
        #     for val in values.values(): flat.append(safeFloat(val))

        for section, keys in [
                ("vital_signs",   VITAL_SIGN_KEYS),
                ("symptoms",      SYMPTOM_KEYS),
                ("comorbidities", COMORBIDITY_KEYS),
                ("lab_findings",  LAB_FINDING_KEYS),
                ("outcomes",      OUTCOME_KEYS),
            ]:
                values = data.get(section, {})
                for k in keys:
                    flat.append(safeFloat(values.get(k)))

        # outcomes = data.get("outcomes", {})
        # for key, val in outcomes.items():
        #     flat.append(safeFloat(val))

        return torch.tensor(flat, dtype = torch.float32)
    
    def readLabel(self, patientID):
        labelPath = self.datafile / ("patient_" + patientID) / ("patient_" + patientID + "_record") / "covid_classification.json"
        # if os.path.exists(labelPath):
        # data = json.load(open(labelPath))
        # result = data["Covid_test_result"].strip().lower()

        # return 1 if result == "positive" else 0
        return 0
        
        # else: return 0
    


class covidModel(nn.Module):
    def __init__(self, cnnOutDim = 512, rnnHiddenDim = 128, clinicalDim = 4, numClasses = 2):
        super().__init__()

        # Load pretrained ResNet18 and remove final FC layer (to achieve binary classification)
        resnet = models.resnet18(pretrained = True)
        self.cnn = nn.Sequential(*list(resnet.children())[:-1])

        # LSTM to learn temporal patterns across frames
        self.rnn = nn.LSTM(input_size = cnnOutDim, hidden_size = rnnHiddenDim, batch_first = True)

        # Fully connecter layer for final classification
        self.model = nn.Sequential(
            nn.Linear(196, 64), # Input: LSTM + Clinical data
            nn.ReLU(), # Activation Function: Allows NN to learn non-linear decision boundaries (curves, edges, textures etc)
            nn.Linear(64, numClasses) # Output: 0 or 1
        )

    def forward(self, video, clinicalRecord):
        B, T, C, H, W = video.shape # Shape breakdown

        video = video.contiguous().reshape(B * T, C, H, W) # Process frames individually through CNN
        features = self.cnn(video) # Extract 512D spatial feature map per frame from CNN
        features = features.contiguous().reshape(B, T, -1) # Reshape feature map into a sequence of feature vectors for LTSM

        # Pass vectors through LTSM
        # hn captures the summary of motion in ultrasound clip
        _, (hn, _) = self.rnn(features) 
        rnnOut = hn.squeeze(0)

        # Combine LTSM output with clinical data to give temporal visual features and patient info
        combined = torch.cat((rnnOut, clinicalRecord), dim = 1)
        # print("Combined input shape:", combined.shape)

        return self.model(combined) # Pass through fc layer




# Main Program
def main():
    try:
        # Check GPU
        DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Using Device: ", DEVICE)

        folder = "../../data/Set-4"
        # testfolder = "../../test-data/set-4-test"

        dataset = patientDataset(rootDir = folder)
        # testDataset = patientDataset(rootDir = testfolder)

        setSize = len(dataset)
        trainSize = int(setSize * 0.8)
        testSize = setSize - trainSize

        trainSet, testSet = random_split(dataset, [trainSize, testSize])
        trainLoader = DataLoader(trainSet, batch_size = 8, shuffle = True, num_workers = 4)
        testLoader = DataLoader(testSet, batch_size = 8, shuffle = False, num_workers = 2)

        model = covidModel().to(DEVICE)

        criterion = nn.CrossEntropyLoss() # Measure prediction accuracy
        optimiser = optim.Adam(model.parameters(), lr = 1e-4) # Update model's weights to reduce loss, lr = learning rate

        # Training Loop
        epochs = 5
        bestAccuracy = 0.0 

        for ep in range(epochs):
            model.train()  # Activate training mode
            totalLoss = 0 # Cumulative training loss
            correct = 0 # For accuracy calculation
            total = 0 # For accuracy calculation

            pbar = tqdm(trainLoader, desc=f"Epoch {ep + 1}/{epochs} [train]")

            # For each batch in training data
            for videos, clinicals, labels in trainLoader:
                # Move data to GPU
                videos, clinicals, labels = videos.to(DEVICE), clinicals.to(DEVICE), labels.to(DEVICE)

                optimiser.zero_grad() # Clear gradients from previous backward pass to prevent messing up training due to gradients accumulation
                outputs = model(videos, clinicals) # Forward pass (Male predictions)
                loss = criterion(outputs, labels) # Calculate loss
                loss.backward() # Backpropagation (How to adjust weights)
                optimiser.step() # Update weights

                totalLoss += loss.item() # Get loss value
                _, predicted = outputs.max(1) # Get predicted class
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item() # Compares predictions with labels

                pbar.set_postfix(loss=f"{loss.item():.4f}")
                # print(f"Loss = {loss.item():.4f}")

            averageTrainLoss = totalLoss / total
            trainAccuracy = 100 * correct / total

            # Validation
            model.eval()
            valLoss = 0
            valCorrect = 0
            valTotal = 0

            # Model testing - Turn off gradient tracking to save memory and time
            with torch.no_grad():

                pbar = tqdm(testLoader, desc=f"Epoch {ep + 1}/{epochs} [train]")

                for videos, clinicals, labels in testLoader:

                    videos, clinicals, labels = videos.to(DEVICE), clinicals.to(DEVICE), labels.to(DEVICE)

                    outputs = model(videos, clinicals)
                    loss = criterion(outputs, labels)

                    valLoss += loss.item()
                    _, predicted = outputs.max(1)
                    valTotal += labels.size(0)
                    valCorrect += predicted.eq(labels).sum().item()

                    pbar.set_postfix(loss=f"{loss.item():.4f}")
                    # print(f"Loss = {loss.item():.4f}")

            averageTestLoss = valLoss / valTotal
            valAccuracy = 100 * valCorrect / valTotal

            print(f"\n Epoch {ep}/{epochs} Summary:")
            print(f"   Train   ─ loss: {averageTrainLoss:.4f} | acc: {trainAccuracy:.2f}%")
            print(f"   Test    ─ loss: {averageTestLoss:.4f} | acc: {valAccuracy:.2f}%\n")

            if valAccuracy > bestAccuracy:
                bestAccuracy = valAccuracy
                torch.save(model.state_dict(), "../../trained-models/covid-model.pth")
                print(f"   New best model saved (test acc {bestAccuracy:.2f}%)\n")
        
    except Exception as e:
        print("Error: " + str(e))
        


if __name__ == "__main__":
    main()