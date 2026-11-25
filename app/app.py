import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db"),
        database=os.environ.get("DB_NAME", "appdb"),
        user=os.environ.get("DB_USER", "appuser"),
        password=os.environ.get("DB_PASSWORD", "secretpass")
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deployments (
            id SERIAL PRIMARY KEY,
            service_name VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/deployments", methods=["GET"])
def get_deployments():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, service_name, status, created_at FROM deployments ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {"id": r[0], "service_name": r[1], "status": r[2], "created_at": str(r[3])}
        for r in rows
    ])

@app.route("/deployments", methods=["POST"])
def add_deployment():
    init_db()
    data = request.get_json() or {}
    service_name = data.get("service_name", "web-service")
    status = data.get("status", "deployed")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO deployments (service_name, status) VALUES (%s, %s) RETURNING id;",
        (service_name, status)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "service_name": service_name, "status": status}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
