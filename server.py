import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime  # Import datetime for timestamp handling

app = Flask(__name__)
CORS(app)

# Directly using database credentials
DATABASE_URL = "postgresql://rain_db_5lru_user:TegwXbOymxvPsTx3Qo35X7MarOcFZvYM@dpg-cuutpt9opnds73ekk550-a.oregon-postgres.render.com/rain_db_5lru"

# Function to get a database connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask API is running!"})

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        pressure = data.get("pressure")  # ✅ BME280 pressure
        altitude = data.get("altitude")  # ✅ BME280 altitude
        ax = data.get("ax")
        ay = data.get("ay")
        az = data.get("az")
        timestamp = datetime.now()  # ✅ Ensures timestamp is always present

        # Open database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert data into sensor_data table
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
        cur = conn.cursor()

        # Fetch latest 10 sensor readings
        cur.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Convert rows into JSON format
        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "temperature": row[1],
                "humidity": row[2],
                "pressure": row[3],  # ✅ BME280 pressure
                "altitude": row[4],  # ✅ BME280 altitude
                "ax": row[5],
                "ay": row[6],
                "az": row[7],
                "timestamp": row[8].isoformat() if row[8] else None  # ✅ Handles NULL timestamps
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
