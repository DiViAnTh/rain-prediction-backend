import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime  

app = Flask(__name__)
CORS(app)

DATABASE_URL = "postgresql://rain_db_5lru_user:TegwXbOymxvPsTx3Qo35X7MarOcFZvYM@dpg-cuutpt9opnds73ekk550-a.oregon-postgres.render.com/rain_db_5lru"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

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

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sensor_data (temperature, humidity, ax, ay, az, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",
            (temperature, humidity, ax, ay, az, timestamp)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Data saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
