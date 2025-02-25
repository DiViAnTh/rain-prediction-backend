import os
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows cross-origin requests

# 🔹 Load database credentials from Render environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://your_user:your_password@your-db-host:5432/your_database")

# 🔹 Connect to PostgreSQL database
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cur = conn.cursor()
    print("✅ Database connection successful!")
except Exception as e:
    print("❌ Database connection failed!", e)

# 🔹 API Root (Check if API is running)
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask API is running!"})

# 🔹 Upload Sensor Data
@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.json
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        ax = data.get("ax")
        ay = data.get("ay")
        az = data.get("az")

        # Insert data into the database
        cur.execute(
            "INSERT INTO sensor_data (temperature, humidity, ax, ay, az) VALUES (%s, %s, %s, %s, %s)",
            (temperature, humidity, ax, ay, az)
        )
        conn.commit()

        return jsonify({"message": "Data saved"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Retrieve Recent Sensor Data
@app.route("/data", methods=["GET"])
def get_data():
    try:
        cur.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()

        # Convert rows into a JSON-friendly format
        data = []
        for row in rows:
            data.append({
                "id": row[0],
                "temperature": row[1],
                "humidity": row[2],
                "ax": row[3],
                "ay": row[4],
                "az": row[5],
                "timestamp": row[6]
            })

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Close database connection when the app stops
@app.teardown_appcontext
def close_connection(exception):
    cur.close()
    conn.close()

# 🔹 Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
