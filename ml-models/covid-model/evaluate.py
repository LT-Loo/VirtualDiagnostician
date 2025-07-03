import torch, json, cv2, csv, numpy as np
from pathlib import Path
from torch.utils.data import DataLoader
from covidmodel import covidModel, patientDataset   

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Running evaluation on", DEVICE)

CKPT_PATH   = "../../trained-models/covid-model.pth"  
TEST_ROOT   = "../../test-data/set-4-test"            
BATCH_SIZE  = 8
CSV_OUT     = "../../test-result/set4_predictions.csv"

def main():
    print("Testing...")
    testDataset = patientDataset(rootDir = TEST_ROOT)
    testLoader = DataLoader(testDataset, batch_size = BATCH_SIZE,
                            shuffle = False, num_workers = 0)

    model = covidModel().to(DEVICE)
    model.load_state_dict(torch.load(CKPT_PATH, map_location=DEVICE))
    model.eval()                    

    criterion = torch.nn.CrossEntropyLoss()

    total_loss = 0
    correct    = 0
    total      = 0

    patient_logits = {}

    with torch.no_grad():
        for videos, clinical, pids, patientIDs in testLoader:
            videos, clinical = videos.to(DEVICE), clinical.to(DEVICE)
            logits = model(videos, clinical)
            # print(logits)

            for pid, logit in zip(patientIDs, logits.cpu()):
                patient_logits.setdefault(pid, []).append(logit)

    with open(CSV_OUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["patient_id", "covid_status"])

        for pid in sorted(patient_logits.keys()):
            log_list = patient_logits[pid]
            avg_logit = torch.stack(log_list).mean(0) 
            pred_idx  = avg_logit.argmax().item()
            status    = "Positive" if pred_idx == 1 else "Negative"
            writer.writerow([pid, status])

    print(f"✅ CSV written to {CSV_OUT} ({len(patient_logits)} patients)")

if __name__ == "__main__":
    main()