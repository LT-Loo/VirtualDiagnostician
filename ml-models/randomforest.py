from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from google.cloud import storage
from google.oauth2 import service_account
import json
import pandas as pd
import os
import joblib
import time

class randomForestModel:

    def __init__(self):
        self.model = RandomForestClassifier(class_weight = "balanced", verbose = 1)
        self.df = pd.DataFrame()
    
    # Extract and preprocess data
    def preprocess_data(self, folder):
        data = []

        print("Processing record data...")
        for patientFolder in os.listdir(folder):
            patientPath = os.path.join(folder, patientFolder)
            for filename in os.listdir(patientPath):
                if not filename.endswith("history.json"):
                    filepath = os.path.join(patientPath, filename)
                    with open(filepath, "r") as f:
                        data.append(json.load(f))

        self.df = pd.DataFrame(data)

    def getInputAndTarget(self, df):
        x = df.drop(columns = ["Diabetes_Diagnosis", "Record_ID"])
        y = df["Diabetes_Diagnosis"]

        x = pd.get_dummies(x)
        y = y.map({"Non-Diabetic": 0, "Diabetic": 1})

        return x, y        

    # Train model
    def train(self):
        x, y = self.getInputAndTarget(self.df)

        print("Training model...")
        self.model.fit(x, y)
        print("Done training model.")

    # Predict test data
    def predict(self, test):
        x, y = self.getInputAndTarget(test)

        print("Testing model...")
        start = time.time()
        predict = self.model.predict(x)
        end = time.time()
        duration = end - start

        print("Testing Result: ")
        print("Accuracy: ", accuracy_score(y, predict), f"; Time Used: {duration:.3f} seconds.")

    # Save trained model
    def saveModel(self, filename):
        joblib.dump(self.model, filename)

    # Load trained model
    def getModel(self, filename):
        self.model = joblib.load(filename)

    # Model parameters tuning
    def tuning(self):
        params = {
            'n_estimators': [100, 200, 300],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2']
        }

        grid = GridSearchCV(RandomForestClassifier(), params, cv = 5)
        grid.fit(self.x_train, self.y_train)
        
        print("Best Params: ", grid.best_params_)
        best_model = grid.best_estimator_

        predict = best_model.predict(self.x_test)

        print("Testing Result: ")
        print("Accuracy: ", accuracy_score(self.y_test, predict))



# Main Program
def main():
    try:
        # == Download data files ==
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

        folder = "../data/Set-1"
        model = randomForestModel()
        model.preprocess_data(folder)
        model.train()
        model.saveModel("trained-models/diabetes-model.pkl")
        # model.predict()


        
    except Exception as e:
        print("Error: " + str(e))
        


if __name__ == "__main__":
    main()