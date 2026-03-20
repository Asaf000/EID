from flask import Flask, redirect, request, send_from_directory
import mysql.connector
import os
from datetime import datetime

app = Flask(__name__)

# 🔥 DB CONFIG FROM RAILWAY ENV
db_config = {
    "host": os.environ.get("MYSQLHOST"),
    "user": os.environ.get("MYSQLUSER"),
    "password": os.environ.get("MYSQLPASSWORD"),
    "database": os.environ.get("MYSQLDATABASE"),
    "port": int(os.environ.get("MYSQLPORT", 3306))
}

# 🔥 CONNECT FUNCTION
def get_connection():
    return mysql.connector.connect(**db_config)

# 🔥 INIT DB (CREATE TABLE)
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(50),
            time DATETIME
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# call init
init_db()

# 🔥 SAVE IP
def save_ip(ip):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO visitors (ip, time) VALUES (%s, %s)",
            (ip, datetime.now())
        )

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB Error:", e)

# 🔥 HOME ROUTE
@app.route("/")
def home():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    save_ip(ip)
    return redirect("/eid")

# 🔥 SERVE HTML
@app.route("/eid")
def eid():
    return send_from_directory(".", "eid.html")

# 🔥 STATIC FILES
@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)

# 🔥 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
