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
        "message": "IoT Weather Analytics API is Running!",
        "endpoints": {
            "/upload1": "POST sensor data (Node 1)",
            "/upload2": "POST sensor data (Node 2)",
            "/data1": "GET latest 10 records (Node 1)",
            "/data2": "GET latest 10 records (Node 2)",
            "/latest_data1": "GET most recent reading (Node 1)",
            "/latest_data2": "GET most recent reading (Node 2)",
            "/daily_summary1": "GET daily avg & peak values (Node 1)",
            "/daily_summary2": "GET daily avg & peak values (Node 2)",
            "/last_7_days1": "GET last 7 days analytics (Node 1)",
            "/last_7_days2": "GET last 7 days analytics (Node 2)"
        }
    })

# ✅ **1️⃣ Upload Sensor Data (Node 1)**
@app.route("/upload1", methods=["POST"])
def upload1():
    return upload_sensor_data("sensor_data1")

# ✅ **2️⃣ Upload Sensor Data (Node 2)**
@app.route("/upload2", methods=["POST"])
def upload2():
    return upload_sensor_data("sensor_data2")

# ✅ Generic Function to Upload Sensor Data
def upload_sensor_data(table_name):
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

        cur.execute(f"""
            INSERT INTO {table_name} (temperature, humidity, ax, ay, az, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (temperature, humidity, ax, ay, az, timestamp))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"status": f"✅ Data saved successfully in {table_name}"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **3️⃣ Get Latest 10 Records (Node 1 & 2)**
@app.route("/data1", methods=["GET"])
def get_data1():
    return get_latest_data("sensor_data1")

@app.route("/data2", methods=["GET"])
def get_data2():
    return get_latest_data("sensor_data2")

# ✅ Generic Function to Get Latest 10 Records
def get_latest_data(table_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(f"""
            SELECT id, temperature, humidity, ax, ay, az, timestamp
            FROM {table_name} ORDER BY timestamp DESC LIMIT 10
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = [{
            "id": row[0], "temperature": row[1], "humidity": row[2],
            "ax": row[3], "ay": row[4], "az": row[5],
            "timestamp": row[6].isoformat() if row[6] else None
        } for row in rows]

        return jsonify({f"latest_readings_{table_name}": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **4️⃣ Get Most Recent Sensor Reading (Node 1 & 2)**
@app.route("/latest_data1", methods=["GET"])
def latest_data1():
    return get_most_recent_data("sensor_data1")

@app.route("/latest_data2", methods=["GET"])
def latest_data2():
    return get_most_recent_data("sensor_data2")

# ✅ Generic Function to Get Most Recent Reading
def get_most_recent_data(table_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(f"""
            SELECT * FROM {table_name} 
            ORDER BY timestamp DESC 
            LIMIT 1;
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            data = {
                "id": row[0], "temperature": row[1], "humidity": row[2],
                "ax": row[3], "ay": row[4], "az": row[5],
                "timestamp": row[6].isoformat() if row[6] else None
            }
            return jsonify(data)
        else:
            return jsonify({"message": f"No data available in {table_name}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **5️⃣ Get Daily Summary (Node 1 & 2)**
@app.route("/daily_summary1", methods=["GET"])
def daily_summary1():
    return get_daily_summary("sensor_data1")

@app.route("/daily_summary2", methods=["GET"])
def daily_summary2():
    return get_daily_summary("sensor_data2")

# ✅ Generic Function to Get Daily Summary
def get_daily_summary(table_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(f"""
            SELECT DATE(timestamp) AS date,
                   ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
                   MAX(temperature) AS peak_temp,
                   MIN(temperature) AS min_temp,
                   ROUND(AVG(humidity)::numeric, 2) AS avg_humidity,
                   MAX(humidity) AS peak_humidity,
                   MIN(humidity) AS min_humidity
            FROM {table_name}
            GROUP BY DATE(timestamp)
            ORDER BY date DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        summary = [{
            "date": str(row[0]), "avg_temperature": row[1], "peak_temperature": row[2],
            "min_temperature": row[3], "avg_humidity": row[4],
            "peak_humidity": row[5], "min_humidity": row[6]
        } for row in rows]

        return jsonify({f"daily_summary_{table_name}": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ **6️⃣ Get Last 7 Days Analytics (Node 1 & 2)**
@app.route("/last_7_days1", methods=["GET"])
def last_7_days1():
    return get_last_7_days("sensor_data1")

@app.route("/last_7_days2", methods=["GET"])
def last_7_days2():
    return get_last_7_days("sensor_data2")

# ✅ Generic Function to Get Last 7 Days Analytics
def get_last_7_days(table_name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(f"""
            SELECT DATE(timestamp) AS date,
                   ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
                   MAX(temperature) AS peak_temp,
                   MIN(temperature) AS min_temp,
                   ROUND(AVG(humidity)::numeric, 2) AS avg_humidity,
                   MAX(humidity) AS peak_humidity,
                   MIN(humidity) AS min_humidity
            FROM {table_name}
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

        return jsonify({f"last_7_days_analytics_{table_name}": analytics})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
