import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from google.cloud import storage
from config import CONFIG_PATH
from src.utils import read_yaml
from src.custom_exception import CustomException
from src.logger import get_logger


logger = get_logger(__name__)

class DataIngestion:

    def __init__(self, config: dict):
        self.config = config
        self.bucket_name = self.config['data_ingestion']['bucket_name']
        self.file_name = self.config['data_ingestion']['file_name']
        self.train_size = self.config['data_ingestion']['train_size']
        self.save_data_path = self.config['artifact_paths']['raw_data']

        os.makedirs(self.save_data_path, exist_ok=True)

        logger.info("DataIngestion class initialized with configuration.")

    def download_data(self):
        try:
            logger.info(f"Starting data download from bucket: {self.bucket_name}, file: {self.file_name}")
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.file_name)
            blob.download_to_filename(os.path.join(self.save_data_path, "data.csv"))
            logger.info("Data download completed successfully.")
        except Exception as e:
            logger.error(f"Error occurred while downloading data: {e}")
            raise CustomException(f"Error occurred while downloading data: {e}", sys)
        
    def split_data(self):
        try:
            logger.info("Starting data splitting process.")
            data_path = os.path.join(self.save_data_path, "data.csv")
            df = pd.read_csv(data_path)
            train_df, test_df = train_test_split(df, train_size=self.train_size, random_state=42)
            train_df.to_csv(os.path.join(self.save_data_path, "train_data.csv"), index=False)
            test_df.to_csv(os.path.join(self.save_data_path, "test_data.csv"), index=False)
            logger.info("Data splitting completed successfully.")
        except Exception as e:
            logger.error(f"Error occurred while splitting data: {e}")
            raise CustomException(f"Error occurred while splitting data: {e}", sys)

    def run(self):
        try:
            logger.info("Starting data ingestion pipeline.")
            self.download_data()
            self.split_data()
            logger.info("Data ingestion process pipeline run successfully.")
        except Exception as e:
            logger.error(f"Error occurred during data ingestion process: {e}")
            raise CustomException(f"Error occurred during data ingestion process: {e}", sys)
        
if __name__ == "__main__":
    obj = DataIngestion(read_yaml(CONFIG_PATH))
    obj.run()