import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ✅ Database Credentials
DATABASE_URL = "postgresql://rain_db_5lru_user:TegwXbOymxvPsTx3Qo35X7MarOcFZvYM@dpg-cuutpt9opnds73ekk550-a.oregon-postgres.render.com/rain_db_5lru"

# ✅ Function to Get Database Connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

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

# ✅ **1️⃣ Upload Sensor Data (Node 1)**
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

        return jsonify({"status": "✅ Node 1 data saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **2️⃣ Upload Sensor Data (Node 2)**
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

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO sensor_data2 (temperature, humidity, ax, ay, az, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (temperature, humidity, ax, ay, az, timestamp))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": "✅ Node 2 data saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **3️⃣ Get Latest 10 Records (Node 1)**
@app.route("/data", methods=["GET"])
def get_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = [{
            "id": row[0], "temperature": row[1], "humidity": row[2],
            "ax": row[3], "ay": row[4], "az": row[5], 
            "timestamp": row[6].isoformat() if row[6] else None
        } for row in rows]

        return jsonify({"latest_readings_node1": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **4️⃣ Get Latest 10 Records (Node 2)**
@app.route("/data2", methods=["GET"])
def get_data2():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM sensor_data2 ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = [{
            "id": row[0], "temperature": row[1], "humidity": row[2],
            "ax": row[3], "ay": row[4], "az": row[5], 
            "timestamp": row[6].isoformat() if row[6] else None
        } for row in rows]

        return jsonify({"latest_readings_node2": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **5️⃣ Get Daily Summary (Node 1)**
@app.route("/daily_summary", methods=["GET"])
def daily_summary():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT DATE(timestamp), ROUND(AVG(temperature)::numeric, 2), MAX(temperature), MIN(temperature), 
                   ROUND(AVG(humidity)::numeric, 2), MAX(humidity), MIN(humidity)
            FROM sensor_data
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
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

        return jsonify({"daily_summary_node1": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **6️⃣ Get Daily Summary (Node 2)**
@app.route("/daily_summary2", methods=["GET"])
def daily_summary2():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT DATE(timestamp), ROUND(AVG(temperature)::numeric, 2), MAX(temperature), MIN(temperature), 
                   ROUND(AVG(humidity)::numeric, 2), MAX(humidity), MIN(humidity)
            FROM sensor_data2
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp) DESC
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

        return jsonify({"daily_summary_node2": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **Run the Flask App**
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
