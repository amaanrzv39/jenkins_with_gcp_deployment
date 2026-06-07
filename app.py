import pickle
from venv import logger
import numpy as np
import os
from config import CONFIG_PATH
from src.utils import read_yaml
from src.custom_exception import CustomException
from src.logger import get_logger
from flask import Flask, request, jsonify

app = Flask(__name__)

config = read_yaml(CONFIG_PATH)
loaded_model = pickle.load(open(config["artifact_paths"]["models"] + "/best_lgbm_model.pkl", "rb"))

@app.route('/')
def home():
    return "Welcome to the Hotel Reservation Prediction API! Use the /predict endpoint to get predictions."

@app.route('/predict',methods=['POST'])
def predict():
        data = request.get_json()
        lead_time = int(data["lead_time"])
        no_of_special_request = int(data["no_of_special_request"])
        avg_price_per_room = float(data["avg_price_per_room"])
        arrival_month = int(data["arrival_month"])
        arrival_date = int(data["arrival_date"])

        market_segment_type = int(data["market_segment_type"])
        no_of_week_nights = int(data["no_of_week_nights"])
        no_of_weekend_nights = int(data["no_of_weekend_nights"])

        type_of_meal_plan = int(data["type_of_meal_plan"])
        room_type_reserved = int(data["room_type_reserved"])

        features = np.array([[lead_time,no_of_special_request,avg_price_per_room,arrival_month,arrival_date,market_segment_type,no_of_week_nights,no_of_weekend_nights,type_of_meal_plan,room_type_reserved]])
        prediction = loaded_model.predict(features)

        if prediction[0] == 1:
            return jsonify({"message": "The booking is likely to be completed."})
        else:
            return jsonify({"message": "The booking is likely to be cancelled."})

if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0' , port=port)
