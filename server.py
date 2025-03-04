import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime  # Import datetime for manual timestamping

app = Flask(__name__)
CORS(app)

# Directly use database credentials (without environment variables)
DATABASE_URL = "postgresql://rain_db_5lru_user:TegwXbOymxvPsTx3Qo35X7MarOcFZvYM@dpg-cuutpt9opnds73ekk550-a.oregon-postgres.render.com/rain_db"

# Function to establish a database connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return conn

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask API is running!"})

@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        pressure = data.get("pressure")  # New field for BME280
        altitude = data.get("altitude")  # New field for BME280
        ax = data.get("ax")
        ay = data.get("ay")
        az = data.get("az")
        timestamp = datetime.now()  # Get current timestamp

        # Open a new database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert data into the database
        cur.execute(
            "INSERT INTO sensor_data (temperature, humidity, pressure, altitude, ax, ay, az, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (temperature, humidity, pressure, altitude, ax, ay, az, timestamp)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Data saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/data", methods=["GET"])
def get_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Convert rows into JSON
        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "temperature": row[1],
                "humidity": row[2],
                "pressure": row[3],  # New field for BME280
                "altitude": row[4],  # New field for BME280
                "ax": row[5],
                "ay": row[6],
                "az": row[7],
                "timestamp": row[8].isoformat()  # Convert timestamp to string
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
