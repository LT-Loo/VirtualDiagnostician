from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from google.cloud import storage
from google.oauth2 import service_account
import json
import pandas as pd
import os

class randomForestModel:
    def __init__(self):
        self.model = RandomForestClassifier()
        self.df = pd.DataFrame()
    
    def preprocess_data(self, folder):
        data = []

        print("Processing record data...")
        for patientFolder in os.listdir(folder):
            patientPath = os.path.join(folder, patientFolder)
            # print(patientPath)
            for filename in os.listdir(patientPath):
                if not filename.endswith("history.json"):
                    filepath = os.path.join(patientPath, filename)
                    with open(filepath, "r") as f:
                        # print("Reading from file " + filename)
                        data.append(json.load(f))

        self.df = pd.DataFrame(data)
        # print(self.df)

    def trainAndPredict(self):
        x = self.df.drop(columns = ["Diabetes_Diagnosis", "Record_ID"])
        y = self.df["Diabetes_Diagnosis"]

        x = pd.get_dummies(x)
        y = y.map({"Non-Diabetic": 0, "Diabetic": 1})

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)

        print("Training model...")
        self.model.fit(x_train, y_train)

        print("Testing model...")
        predict = self.model.predict(x_test)

        print("Testing Result: ")
        print("Accuracy: ", accuracy_score(y_test, predict))
        print("Report: \n", classification_report(y_test, predict, target_names = ["Non-Diabetic", "Diabetic"]))



# Main Program
def main():
    try:
        # keyFile = "../credentials/BytesAndBolts-Team9.json"
        # bucketName = "bytes-and-bolts"
        
        # credentials = service_account.Credentials.from_service_account_file(keyFile)
        # record = storage.Client(credentials = credentials)
        # bucket = record.bucket(bucketName)

        # items = bucket.list_blobs()
        # for item in items:
        #     if not item.name.endswith('/'):
        #         localPath = os.path.join("data", item.name)
        #         os.makedirs(os.path.dirname(localPath), exist_ok = True)
        #         item.download_to_filename(localPath)
        
        folder = "data/Set-1"
        model = randomForestModel()
        model.preprocess_data(folder)
        model.trainAndPredict()


        
    except Exception as e:
        print("Error: " + str(e))
        


if __name__ == "__main__":
    main()