from tensorflow.keras import layers, models, losses
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import os
import numpy as np
import joblib

class cnnModel:
    def __init__(self):
        self.model = models.Sequential()
        self.images = []
        self.labels = []
        self.le = LabelEncoder()
        
    def preprocess_data(self, folder):

        print("Processing record data...")
        for patientFolder in os.listdir(folder):
            patientPath = os.path.join(folder, patientFolder) + "/" + patientFolder + "_data"
            for filename in os.listdir(patientPath):
                path = os.path.join(patientPath, filename)
                # print(path)
                if filename.endswith(".jpg"):
                    # print(filename)
                    img = load_img(path)
                    # print(img_to_array(path))
                    self.images.append(img_to_array(img))
                elif filename.endswith(".json"):
                    # print(filename)
                    with open(path, "r") as f:
                        # print("Reading from file " + filename)
                        self.labels.append(f.read().strip())
        print("Done processing data.")

        # self.df = pd.DataFrame(data)
        # print(images)
        # print(labels)

    def train(self):
        x = np.array(self.images) / 255.0 # Standardised data
        y = self.le.fit_transform(self.labels)

        print("Splitting data...")
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2)

        print("Creating model...")
        self.model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
            layers.MaxPooling2D(2, 2),

            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D(2, 2),

            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D(2, 2),

            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dense(len(self.le.classes_), activation='softmax')
        ])

        self.model.compile(
            optimizer = 'adam',
            loss = losses.SparseCategoricalCrossentropy(from_logits = True),
            metrics = ['accuracy']
        )

        print("Training model...")
        self.model.fit(x_train, y_train, epochs = 5, validation_data = (x_test, y_test))
        print("Done training model.")

    def saveModel(self):
        print("Saving model...")
        self.model.save("skin_disease_model")
        joblib.dump(self.le, "skin_diseases_le.pkl")
        print("Model saved.")


# Main Program
def main():
    try:
        folder = "data/Set-2"

        model = cnnModel()
        model.preprocess_data(folder)
        model.train()
        # model.saveModel()
        # model.tuning()
        # model.train()
        # model.saveModel("diabetes_model.pkl")


        
    except Exception as e:
        print("Error: " + str(e))
        


if __name__ == "__main__":
    main()