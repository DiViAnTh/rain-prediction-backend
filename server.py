import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ✅ Database Credentials (Directly used)
DATABASE_URL = "postgresql://rain_db_5lru_user:TegwXbOymxvPsTx3Qo35X7MarOcFZvYM@dpg-cuutpt9opnds73ekk550-a.oregon-postgres.render.com/rain_db_5lru"

# ✅ Function to Get Database Connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "📡 IoT Weather Analytics API is Running!",
        "endpoints": {
            "/upload": "POST sensor data",
            "/data": "GET latest 10 sensor records",
            "/latest_data": "GET most recent sensor reading",
            "/daily_summary": "GET daily avg & peak temperature/humidity",
            "/last_7_days": "GET analytics for the last 7 days"
        }
    })

# ✅ **1️⃣ Upload Sensor Data**
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

        cur.execute("""
            INSERT INTO sensor_data (temperature, humidity, ax, ay, az, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (temperature, humidity, ax, ay, az, timestamp))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "✅ Data saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **2️⃣ Get Latest 10 Records**
@app.route("/data", methods=["GET"])
def get_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, temperature, humidity, ax, ay, az, timestamp
            FROM sensor_data ORDER BY timestamp DESC LIMIT 10
        """)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        data = [{
            "id": row[0], "temperature": row[1], "humidity": row[2],
            "ax": row[3], "ay": row[4], "az": row[5],
            "timestamp": row[6].isoformat() if row[6] else None
        } for row in rows]

        return jsonify({"latest_readings": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **3️⃣ Get Most Recent Sensor Reading**
@app.route("/latest_data", methods=["GET"])
def latest_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM sensor_data 
            ORDER BY timestamp DESC 
            LIMIT 1;
        """)

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            data = {
                "id": row[0],
                "temperature": row[1],
                "humidity": row[2],
                "ax": row[3],
                "ay": row[4],
                "az": row[5],
                "timestamp": row[6].isoformat() if row[6] else None
            }
            return jsonify(data)
        else:
            return jsonify({"message": "No data available"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **4️⃣ Get Daily Average & Peak Temp/Humidity**
@app.route("/daily_summary", methods=["GET"])
def daily_summary():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT DATE(timestamp) AS date,
                   ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
                   MAX(temperature) AS peak_temp,
                   MIN(temperature) AS min_temp,
                   ROUND(AVG(humidity)::numeric, 2) AS avg_humidity,
                   MAX(humidity) AS peak_humidity,
                   MIN(humidity) AS min_humidity
            FROM sensor_data
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 10;
        """)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        summary = [{
            "date": str(row[0]), "avg_temperature": row[1], "peak_temperature": row[2],
            "min_temperature": row[3], "avg_humidity": row[4],
            "peak_humidity": row[5], "min_humidity": row[6]
        } for row in rows]

        return jsonify({"daily_summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **5️⃣ Get Last 7 Days Analytics**
@app.route("/last_7_days", methods=["GET"])
def last_7_days():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT DATE(timestamp) AS date,
                   ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
                   MAX(temperature) AS peak_temp,
                   MIN(temperature) AS min_temp,
                   ROUND(AVG(humidity)::numeric, 2) AS avg_humidity,
                   MAX(humidity) AS peak_humidity,
                   MIN(humidity) AS min_humidity
            FROM sensor_data
            WHERE timestamp >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC;
        """)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        analytics = [{
            "date": str(row[0]), "avg_temperature": row[1], "peak_temperature": row[2],
            "min_temperature": row[3], "avg_humidity": row[4],
            "peak_humidity": row[5], "min_humidity": row[6]
        } for row in rows]

        return jsonify({"last_7_days_analytics": analytics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **Run the Flask App**
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
