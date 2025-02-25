from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# PostgreSQL Connection
conn = psycopg2.connect(
    dbname="rain_db",
    user="your_user",
    password="your_password",
    host="your-db-host",
    port="5432"
)
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
