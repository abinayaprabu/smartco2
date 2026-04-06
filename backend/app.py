from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

# Load trained model
model = pickle.load(open("model.pkl", "rb"))

@app.route("/")
def home():
    return "Smart CO2 Prediction API Running"


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        # Read input values
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        occupancy = float(data["occupancy"])
        light = float(data["light"])

        # Optional basic validation (prevents unrealistic values)
        if temperature < 0 or humidity < 0 or light < 0:
            return jsonify({"error": "Invalid input values"}), 400

        # IMPORTANT: Feature order must match training
        # ['Temperature','Humidity','Occupancy','Light']
        input_data = np.array([[temperature, humidity, occupancy, light]])

        prediction = model.predict(input_data)
        co2_value = round(float(prediction[0]), 2)

        # Air Quality Classification + Range + Color
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
    # Sample test input
    input_data = np.array([[23, 40, 1, 300]])
    prediction = model.predict(input_data)
    return str(round(float(prediction[0]), 2))


if __name__ == "__main__":
    app.run(debug=True)