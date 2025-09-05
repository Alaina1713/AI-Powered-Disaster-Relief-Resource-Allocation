# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, csv, os, statistics
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "disaster.db")
DATA_DIR = os.path.join(BASE, "data")

app = Flask(__name__, static_folder=None)
CORS(app)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS regions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT UNIQUE, population INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS disasters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT, date TEXT, severity_score REAL, casualties INTEGER, displaced INTEGER)""")
    conn.commit()
    # seed regions
    cur.execute("SELECT COUNT(*) as c FROM regions")
    if cur.fetchone()["c"] == 0:
        cur.executemany("INSERT OR IGNORE INTO regions(name,population) VALUES (?,?)",
                        [("Riverside",6000),("Harborview",4500),("Greenfield",3000)])
        conn.commit()
    # seed disasters from CSV if empty
    cur.execute("SELECT COUNT(*) as c FROM disasters")
    if cur.fetchone()["c"] == 0 and os.path.exists(os.path.join(DATA_DIR,"sample_disasters.csv")):
        with open(os.path.join(DATA_DIR,"sample_disasters.csv"), newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = []
            for r in reader:
                rows.append((r.get("region"), r.get("date"), float(r.get("severity_score") or 0), int(r.get("casualties") or 0), int(r.get("displaced") or 0)))
            cur.executemany("INSERT INTO disasters(region,date,severity_score,casualties,displaced) VALUES (?,?,?,?,?)", rows)
            conn.commit()
    conn.close()

@app.route("/api/health")
def health():
    return jsonify({"status":"ok","time":datetime.utcnow().isoformat()})

@app.route("/api/disaster/regions", methods=["GET"])
def regions():
    conn = get_conn()
    cur = conn.execute("SELECT name,population FROM regions ORDER BY name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

def predict_needs(region_name):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT population FROM regions WHERE name=?", (region_name,))
    row = cur.fetchone()
    pop = row["population"] if row else 1000
    cur.execute("SELECT severity_score FROM disasters WHERE region=? ORDER BY date DESC LIMIT 10", (region_name,))
    vals = [r["severity_score"] for r in cur.fetchall()]
    severity = statistics.mean(vals) if vals else 4.0
    # heuristic scaling
    food = int(pop * 0.25 * (severity/5.0))
    medical = int(pop * 0.06 * (severity/5.0))
    shelter = int(pop * 0.04 * (severity/5.0))
    confidence = round(min(0.95, 0.5 + (severity/10.0)), 2)
    conn.close()
    return {"region": region_name, "food": food, "medical": medical, "shelter": shelter, "confidence": confidence, "model": "heuristic-v1"}

@app.route("/api/disaster/predict", methods=["GET"])
def api_predict():
    region = request.args.get("region")
    if not region:
        return jsonify({"error":"region param required"}), 400
    return jsonify(predict_needs(region))

@app.route("/api/disaster/upload", methods=["POST"])
def upload_disaster():
    file = request.files.get("file")
    if not file:
        return jsonify({"error":"file required"}), 400
    text = file.stream.read().decode('utf-8').splitlines()
    reader = csv.DictReader(text)
    conn = get_conn()
    cur = conn.cursor()
    inserted = 0
    for r in reader:
        cur.execute("INSERT INTO disasters(region,date,severity_score,casualties,displaced) VALUES (?,?,?,?,?)",
                    (r.get("region"), r.get("date"), float(r.get("severity_score") or 0), int(r.get("casualties") or 0), int(r.get("displaced") or 0)))
        inserted += 1
    conn.commit()
    conn.close()
    return jsonify({"inserted": inserted})

@app.route("/sample/<path:filename>")
def sample(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        return send_from_directory(DATA_DIR, filename)
    return jsonify({"error":"not found"}), 404

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)
