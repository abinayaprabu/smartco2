from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Load trained model
model = pickle.load(open("model.pkl", "rb"))

# ================= TWILIO CONFIG =================
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone = os.getenv("TWILIO_PHONE")
user_phone = os.getenv("USER_PHONE")

client = Client(account_sid, auth_token)

# ================= ROUTES =================

@app.route("/")
def home():
    return "Smart CO2 Prediction API Running"


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        # Input values
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        occupancy = float(data["occupancy"])
        light = float(data["light"])

        # Validation
        if temperature < 0 or humidity < 0 or light < 0:
            return jsonify({"error": "Invalid input values"}), 400

        # Model prediction
        input_data = np.array([[temperature, humidity, occupancy, light]])
        prediction = model.predict(input_data)
        co2_value = round(float(prediction[0]), 2)

        # ================= CLASSIFICATION =================
        if co2_value < 800:
            status = "Good"
            range_text = "0 – 800 ppm"
            color = "green"
        elif co2_value < 1500:
            status = "Moderate"
            range_text = "800 – 1500 ppm"
            color = "orange"
        else:
            status = "Poor"
            range_text = "1500+ ppm"
            color = "red"

        # ================= 🚨 SMS ALERT =================
        
        try:
           if co2_value >= 1500:
              print("🚨 HIGH ALERT TRIGGERED")

              message = client.messages.create(
              body=f"🚨 Dangerous CO₂ Level: {co2_value} ppm!",
              from_=twilio_phone,
              to=user_phone
             )
              print("SMS Sent (High):", message.sid)

           elif co2_value >= 800:
             print("⚠️ MODERATE ALERT TRIGGERED")

             message = client.messages.create(
             body=f"⚠️ Moderate CO₂ Level: {co2_value} ppm",
             from_=twilio_phone,
             to=user_phone
             )
             print("SMS Sent (Moderate):", message.sid)

        except Exception as sms_error:
           print("❌ SMS Failed:", sms_error)

        # ================= RESPONSE =================
        return jsonify({
            "predicted_co2": co2_value,
            "air_quality": status,
            "range": range_text,
            "color": color
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test")
def test():
    input_data = np.array([[23, 40, 1, 300]])
    prediction = model.predict(input_data)
    return str(round(float(prediction[0]), 2))


if __name__ == "__main__":
    app.run(debug=True)