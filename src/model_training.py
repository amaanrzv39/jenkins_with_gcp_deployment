import os
import pickle
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score
import lightgbm as lgb
from src.logger import get_logger
from src.custom_exception import CustomException
from src.utils import read_yaml
from config.model_config import LIGHTGM_PARAMS, RANDOM_SEARCH_PARAMS
from config import CONFIG_PATH
import mlflow


logger = get_logger(__name__)


class ModelTraining:

    def __init__(self, config):
        self.config = config
        self.train_path = config["artifact_paths"]["processed_data"] + "/train_data.csv"
        self.test_path = config["artifact_paths"]["raw_data"] + "/test_data.csv"
        self.model_save_path = config["artifact_paths"]["models"]
        self.params_dist = LIGHTGM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS
        os.makedirs(self.model_save_path, exist_ok=True)


    def load_train_data(self):
        try:
            logger.info(f"Loading data from {self.train_path}")
            data = pd.read_csv(self.train_path)
            X = data.drop(columns=["booking_status"])
            y = data["booking_status"]
            logger.info("Data loading completed successfully")
            return X, y
        except Exception as e:
            logger.error(f"Error while loading data {e}")
            raise CustomException("Failed to load data" ,  e)
        

    def load_test_data(self, X_train):
        try:
            logger.info(f"Loading data from {self.test_path}")
            data = pd.read_csv(self.test_path)
            data = data.drop(columns=['Booking_ID'])
            data = self.apply_transformation(data)
            X = data.drop(columns=["booking_status"])
            y = data["booking_status"]
            # Ensure the test data has the same columns as training data
            X = X[X_train.columns]
            logger.info("Data loading completed successfully")
            return X, y
        except Exception as e:
            logger.error(f"Error while loading data {e}")
            raise CustomException("Failed to load data" ,  e)

    def apply_transformation(self, df):
        try:
            import pickle
            import numpy as np

            logger.info("Applying transformation to the data")
            encoders = pickle.load(open(os.path.join(self.config["artifact_paths"]["processed_data"], "encoders.pkl"), "rb"))
            mappings = pickle.load(open(os.path.join(self.config["artifact_paths"]["processed_data"], "mappings.pkl"), "rb"))

            cat_cols = df.select_dtypes(include='object').columns
            for col in cat_cols:
                le = encoders[col]
                # replace unseen values
                df[col] = df[col].apply(
                    lambda x: x if x in le.classes_ else 'Unknown'
                )
                # add Unknown if not already present
                if 'Unknown' not in le.classes_:
                    le.classes_ = np.append(le.classes_, 'Unknown')
                df[col] = le.transform(df[col])

            logger.info("Transformation applied successfully")
            return df
        except Exception as e:
            logger.error(f"Error while applying transformation {e}")
            raise CustomException("Failed to apply transformation" ,  e)
        

    def train_model(self, X_train, y_train):
        try:
            logger.info("Intializing our model")

            lgbm_model = lgb.LGBMClassifier(random_state=self.random_search_params["random_state"])

            logger.info("Starting our Hyperparamter tuning")

            random_search = RandomizedSearchCV(
                estimator=lgbm_model,
                param_distributions=self.params_dist,
                n_iter = self.random_search_params["n_iter"],
                cv = self.random_search_params["cv"],
                n_jobs=self.random_search_params["n_jobs"],
                verbose=self.random_search_params["verbose"],
                random_state=self.random_search_params["random_state"],
                scoring=self.random_search_params["scoring"]
            )

            logger.info("Starting our Hyperparamter tuning")

            random_search.fit(X_train,y_train)

            logger.info("Hyperparamter tuning completed")

            best_params = random_search.best_params_
            best_lgbm_model = random_search.best_estimator_

            logger.info(f"Best paramters are : {best_params}")

            return best_lgbm_model
        except Exception as e:
            logger.error(f"Error while training model {e}")
            raise CustomException("Failed to train model" ,  e)
    

    def evaluate_model(self , model , X_test , y_test):
        try:
            logger.info("Evaluating our model")

            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test,y_pred)
            precision = precision_score(y_test,y_pred)
            recall = recall_score(y_test,y_pred)
            f1 = f1_score(y_test,y_pred)

            logger.info(f"Accuracy Score : {accuracy}")
            logger.info(f"Precision Score : {precision}")
            logger.info(f"Recall Score : {recall}")
            logger.info(f"F1 Score : {f1}")

            return {
                "accuracy" : accuracy,
                "precison" : precision,
                "recall" : recall,
                "f1" : f1
            }
        except Exception as e:
            logger.error(f"Error while evaluating model {e}")
            raise CustomException("Failed to evaluate model" ,  e)
        
    
    def run(self):
        try:
            with mlflow.start_run():
                logger.info("Starting our Model Training pipeline")
                logger.info("Starting our MLFLOW experimentation")
                logger.info("Logging the training and testing datset to MLFLOW")
                mlflow.log_artifact(self.train_path , artifact_path="datasets")
                mlflow.log_artifact(self.test_path , artifact_path="datasets")
                X_train, y_train =self.load_train_data()
                X_test, y_test = self.load_test_data(X_train)
                best_lgbm_model = self.train_model(X_train,y_train)
                metrics = self.evaluate_model(best_lgbm_model ,X_test , y_test)
                pickle.dump(best_lgbm_model, open(os.path.join(self.model_save_path, "best_lgbm_model.pkl"), "wb"))
                logger.info("Logging the model into MLFLOW")
                mlflow.log_artifact(self.model_save_path)

                logger.info("Logging Params and metrics to MLFLOW")
                mlflow.log_params(best_lgbm_model.get_params())
                mlflow.log_metrics(metrics)

                logger.info("Model Training sucesfullly completed")
        except Exception as e:
            logger.error(f"Error in model training pipeline {e}")
            raise CustomException("Failed during model training pipeline" ,  e)
        
if __name__=="__main__":
    trainer = ModelTraining(read_yaml(CONFIG_PATH))
    trainer.run()
        

    

            
