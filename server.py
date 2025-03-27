import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from tensorflow.keras.models import load_model
import joblib

app = Flask(__name__)
CORS(app)

DATABASE_URL = "postgresql://rain_db_5lru_jn0r_user:2snapd3uhL2qpKAkc1FKKXZwV6GkECpV@dpg-cvim5gidbo4c73cm3fm0-a.singapore-postgres.render.com/rain_db_5lru_jn0r"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# ✅ Load models for Node 1
lstm_model_1 = load_model("lstm_model_1.h5")
iso_forest_model_1 = joblib.load("isolation_forest_1.pkl")

# ✅ Load models for Node 2
lstm_model_2 = load_model("lstm_model_2.h5")
iso_forest_model_2 = joblib.load("isolation_forest_2.pkl")

# ✅ Load Rain Prediction Model
rain_model = joblib.load("rain_prediction.pkl")
rain_model2 = joblib.load("rain_prediction2.pkl")

# ✅ Function to Predict Anomaly using Isolation Forest (Node 1)
def predict_anomaly_node1(features):
    return iso_forest_model_1.predict([features])[0] == -1

# ✅ Function to Predict Anomaly using Isolation Forest (Node 2)
def predict_anomaly_node2(features):
    return iso_forest_model_2.predict([features])[0] == -1

# ✅ Predict Future Temperature using LSTM
@app.route("/predict_temperature", methods=["GET"])
def predict_temperature():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 🔹 Fetch last 10 temperature readings
        cur.execute("SELECT temperature FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if len(rows) < 10:
            return jsonify({"error": "Not enough data for prediction"}), 400

        # 🔹 Prepare data for LSTM
        scaler = MinMaxScaler()
        temperature_data = np.array(rows).reshape(-1, 1)
        temperature_data = scaler.fit_transform(temperature_data)
        temperature_data = np.expand_dims(temperature_data, axis=0)  # Reshape for LSTM input

        # 🔹 Make prediction
        predicted_temp = lstm_model.predict(temperature_data)
        predicted_temp = scaler.inverse_transform(predicted_temp.reshape(-1, 1))[0][0]

        return jsonify({"predicted_temperature": predicted_temp})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/predict_temperature2", methods=["GET"])
def predict_temperature2():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 🔹 Fetch last 10 temperature readings from Node 2
        cur.execute("SELECT temperature FROM sensor_data2 ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if len(rows) < 10:
            return jsonify({"error": "Not enough data for prediction"}), 400

        # 🔹 Prepare data for LSTM
        scaler = MinMaxScaler()
        temperature_data = np.array(rows).reshape(-1, 1)
        temperature_data = scaler.fit_transform(temperature_data)
        temperature_data = np.expand_dims(temperature_data, axis=0)  # Reshape for LSTM input

        # 🔹 Make prediction
        predicted_temp = lstm_model_2.predict(temperature_data)
        predicted_temp = scaler.inverse_transform(predicted_temp.reshape(-1, 1))[0][0]

        return jsonify({"predicted_temperature": predicted_temp})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def predict_rain(table_name, model):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT temperature, humidity, ax, ay, az FROM {table_name} ORDER BY timestamp DESC LIMIT 1")
        latest_data = cur.fetchone()
        cur.close()
        conn.close()

        if latest_data:
            features = [[latest_data[0], latest_data[1], latest_data[2], latest_data[3], latest_data[4]]]
            prediction = model.predict(features)[0]
            return "Rain Expected" if prediction == 1 else "No Rain"
        return "No data available"
    except Exception as e:
        return str(e)

def get_latest_data(table_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return jsonify({"latest_data": row})
        return jsonify({"message": "No data found"})
    except Exception as e:
        return jsonify({"error": str(e)})

def get_daily_summary(table_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT DATE(timestamp), ROUND(AVG(temperature)::numeric, 2), MAX(temperature), MIN(temperature),
                   ROUND(AVG(humidity)::numeric, 2), MAX(humidity), MIN(humidity)
            FROM {table_name}
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
            LIMIT 10;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"daily_summary": rows})
    except Exception as e:
        return jsonify({"error": str(e)})

def get_last_7_days(table_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"""
            SELECT DATE(timestamp), COUNT(*), ROUND(AVG(temperature)::numeric, 2),
                   ROUND(AVG(humidity)::numeric, 2)
            FROM {table_name}
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"last_7_days": rows})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/latest_data", methods=["GET"])
def latest_data():
    return get_latest_data("sensor_data")

@app.route("/latest_data2", methods=["GET"])
def latest_data2():
    return get_latest_data("sensor_data2")

@app.route("/daily_summary", methods=["GET"])
def daily_summary():
    return get_daily_summary("sensor_data")

@app.route("/daily_summary2", methods=["GET"])
def daily_summary2():
    return get_daily_summary("sensor_data2")

@app.route("/last_7_days", methods=["GET"])
def last_7_days():
    return get_last_7_days("sensor_data")

@app.route("/last_7_days2", methods=["GET"])
def last_7_days2():
    return get_last_7_days("sensor_data2")

@app.route("/predict_rain", methods=["GET"])
def get_rain_prediction():
    return jsonify({"prediction": predict_rain("sensor_data", rain_model)})

@app.route("/predict_rain2", methods=["GET"])
def get_rain_prediction2():
    return jsonify({"prediction": predict_rain("sensor_data2", rain_model2)})

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "📡 IoT Weather Analytics API is Running!",
        "endpoints": {
            "/upload": "POST Node 1 sensor data",
            "/upload2": "POST Node 2 sensor data",
            "/data": "GET latest 10 sensor records (Node 1)",
            "/data2": "GET latest 10 sensor records (Node 2)",
            "/latest_data": "GET most recent sensor reading (Node 1)",
            "/latest_data2": "GET most recent sensor reading (Node 2)",
            "/daily_summary": "GET daily avg & peak temperature/humidity (Node 1)",
            "/daily_summary2": "GET daily avg & peak temperature/humidity (Node 2)",
            "/last_7_days": "GET analytics for the last 7 days (Node 1)",
            "/last_7_days2": "GET analytics for the last 7 days (Node 2)"
        }
    })

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        ax = data.get("ax")
        ay = data.get("ay")
        az = data.get("az")
        timestamp = datetime.now()

        # 🔍 Detect anomaly using Isolation Forest
        anomaly = predict_anomaly_node1([temperature, humidity, ax, ay, az])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensor_data (temperature, humidity, ax, ay, az, timestamp, anomaly)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (temperature, humidity, ax, ay, az, timestamp, anomaly))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "✅ Node 1 data saved successfully", "anomaly_detected": anomaly}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload2", methods=["POST"])
def upload2():
    try:
        data = request.json
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        ax = data.get("ax")
        ay = data.get("ay")
        az = data.get("az")
        timestamp = datetime.now()

        # 🔍 Detect anomaly using Isolation Forest for Node 2
        anomaly = predict_anomaly_node2([temperature, humidity, ax, ay, az])

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sensor_data2 (temperature, humidity, ax, ay, az, timestamp, anomaly)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (temperature, humidity, ax, ay, az, timestamp, anomaly))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "✅ Node 2 data saved successfully", "anomaly_detected": anomaly}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
