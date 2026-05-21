import sys
import yaml
import os
from src.custom_exception import CustomException

def read_yaml(file_path:str) -> dict:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML file not found at path: {file_path}")
        
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise CustomException(f"Error reading YAML file: {e}", sys)