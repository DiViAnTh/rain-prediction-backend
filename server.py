import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load database credentials
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Make sure it's configured in Render.")

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        pressure = data.get("pressure")  # ✅ New
        altitude = data.get("altitude")  # ✅ New
        ax = data.get("ax")
        ay = data.get("ay")
        az = data.get("az")
        timestamp = datetime.now()

        if None in (temperature, humidity, pressure, altitude, ax, ay, az):
            return jsonify({"error": "Missing data fields"}), 400

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sensor_data (temperature, humidity, pressure, altitude, ax, ay, az, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (temperature, humidity, pressure, altitude, ax, ay, az, timestamp)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Data saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/data", methods=["GET"])
def get_data():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = [
            {
                "id": row[0],
                "temperature": row[1],
                "humidity": row[2],
                "pressure": row[3],  # ✅ Updated
                "altitude": row[4],  # ✅ Updated
                "ax": row[5],
                "ay": row[6],
                "az": row[7],
                "timestamp": row[8].isoformat(),
            }
            for row in rows
        ]

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
