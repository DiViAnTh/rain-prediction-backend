import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace with your Render database credentials
DATABASE_URL = "postgresql://rain_db_5lru_user:TegwXbOymxvPsTx3Qo35X7MarOcFZvYM@dpg-cuutpt9opnds73ekk550-a/rain_db_5lru"

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route("/upload", methods=["POST"])
def upload():
    data = request.json
    temperature = data["temperature"]
    humidity = data["humidity"]
    ax = data["ax"]
    ay = data["ay"]
    az = data["az"]

    cur.execute("INSERT INTO sensor_data (temperature, humidity, ax, ay, az) VALUES (%s, %s, %s, %s, %s)",
                (temperature, humidity, ax, ay, az))
    conn.commit()

    return jsonify({"message": "Data saved"}), 200

@app.route("/data", methods=["GET"])
def get_data():
    cur.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
    rows = cur.fetchall()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
