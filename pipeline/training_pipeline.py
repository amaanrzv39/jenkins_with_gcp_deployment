from src.data_ingestion import DataIngestion
from src.data_preprocessing import DataProcessor
from src.model_training import ModelTraining
from src.utils import read_yaml
from config import CONFIG_PATH


if __name__=="__main__":
    ### 1. Data Ingestion

    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()

    ### 2. Data Processing

    processor = DataProcessor(read_yaml(CONFIG_PATH))
    processor.run()

    ### 3. Model Training

    trainer = ModelTraining(read_yaml(CONFIG_PATH))
    trainer.run()
