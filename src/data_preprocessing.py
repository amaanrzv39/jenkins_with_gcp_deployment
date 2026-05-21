import os
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler
from src.utils import read_yaml
from src.custom_exception import CustomException
from src.logger import get_logger
from config import CONFIG_PATH


logger = get_logger(__name__)

class DataProcessor:

    def __init__(self, config):
        self.config = config
        self.train_path = self.config["artifact_paths"]["raw_data"] + "/train_data.csv"
        self.processed_data_path = self.config["artifact_paths"]["processed_data"]
        self.model_save_path = self.config["artifact_paths"]["models"]
        if not os.path.exists(self.processed_data_path):
            os.makedirs(self.processed_data_path)
        

    def preprocess_data(self, df):
        try:
            logger.info("Starting Data Processing step")
            logger.info("Dropping the columns")
            df.drop(columns=['Booking_ID'] , inplace=True)
            df.drop_duplicates(inplace=True)

            cat_cols = df.select_dtypes(include='object').columns

            logger.info("Applying Label Encoding")

            mappings = {}
            encoders = {}

            for col in cat_cols:       
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                # store encoder
                encoders[col] = le
                # store mappings
                mappings[col] = dict(
                    zip(le.classes_, le.transform(le.classes_))
                )

            logger.info("Label Mappings are : ")
            for col,mapping in mappings.items():
                logger.info(f"{col} : {mapping}")

            logger.info("Saving the encoders and mappings for future use")
            # Save encoders and mappings for future use
            with open(os.path.join(self.processed_data_path, "encoders.pkl"), "wb") as f:
                pickle.dump(encoders, f)
            with open(os.path.join(self.processed_data_path, "mappings.pkl"), "wb") as f:
                pickle.dump(mappings, f)
            return df
        
        except Exception as e:
            logger.error(f"Error during preprocess step {e}")
            raise CustomException("Error while preprocess data", e)
        

    def balance_data(self,df):
        try:
            logger.info("Handling Imbalanced Data")
            X = df.drop(columns='booking_status')
            y = df["booking_status"]

            smote = SMOTE(random_state=42)
            X_resampled , y_resampled = smote.fit_resample(X,y)

            balanced_df = pd.DataFrame(X_resampled , columns=X.columns)
            balanced_df["booking_status"] = y_resampled

            logger.info("Data balanced sucesffuly")
            return balanced_df
        
        except Exception as e:
            logger.error(f"Error during balancing data step {e}")
            raise CustomException("Error while balancing data", e)
        

    def feature_selection(self,df):
        try:
            logger.info("Starting Feature selection step")

            X = df.drop(columns='booking_status')
            y = df["booking_status"]

            model =  RandomForestClassifier(random_state=42)
            model.fit(X,y)

            feature_importance = model.feature_importances_
            feature_importance_df = pd.DataFrame({'feature':X.columns, 'importance':feature_importance})
            top_features_importance_df = feature_importance_df.sort_values(by="importance" , ascending=False)
            num_features_to_select = self.config["data_preprocessing"]["num_features"]
            top_10_features = top_features_importance_df["feature"].head(num_features_to_select).values

            logger.info(f"Features selected : {top_10_features}")

            top_10_df = df[top_10_features.tolist() + ["booking_status"]]

            logger.info("Feature slection completed sucesfully")

            return top_10_df
        
        except Exception as e:
            logger.error(f"Error during feature selection step {e}")
            raise CustomException("Error while feature selection", e)
    
    def save_data(self,df , file_path):
        try:
            logger.info("Saving our data in processed folder")

            df.to_csv(file_path, index=False)

            logger.info(f"Data saved sucesfuly to {file_path}")

        except Exception as e:
            logger.error(f"Error during saving data step {e}")
            raise CustomException("Error while saving data", e)

    def run(self):
        try:
            logger.info("Loading data from RAW directory")

            data = pd.read_csv(self.train_path)
            data = self.preprocess_data(data)
            data = self.balance_data(data)
            data = self.feature_selection(data)

            self.save_data(data, self.processed_data_path + "/train_data.csv")

            logger.info("Data processing completed sucesfully")    
        except Exception as e:
            logger.error(f"Error during preprocessing pipeline {e}")
            raise CustomException("Error while data preprocessing pipeline", e)
              
    
    
if __name__=="__main__":
    processor = DataProcessor(read_yaml(CONFIG_PATH))
    processor.run()       