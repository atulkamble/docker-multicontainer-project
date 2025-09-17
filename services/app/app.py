import os
from flask import Flask, jsonify, request
import redis
import psycopg
from celery import Celery

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

DB_URL = os.getenv("DB_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Celery
celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

@celery.task
def add(x, y):
    return x + y

# Redis client
r = redis.Redis.from_url(REDIS_URL)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def index():
    # Count hits in Redis
    hits = r.incr("hits")
    return jsonify(message="Hello from Flask behind Nginx!", hits=int(hits))

@app.post("/db")
def write_db():
    note = request.json.get("note", "hello")
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO visits(note) VALUES (%s) RETURNING id, ts", (note,))
            row = cur.fetchone()
    return {"inserted": {"id": row[0], "ts": row[1].isoformat()}}

@app.get("/db")
def read_db():
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, ts, note FROM visits ORDER BY id DESC LIMIT 10")
            rows = cur.fetchall()
    return {"rows": [{"id": r[0], "ts": r[1].isoformat(), "note": r[2]} for r in rows]}

@app.post("/enqueue")
def enqueue():
    data = request.get_json(silent=True) or {}
    x = int(data.get("x", 1))
    y = int(data.get("y", 2))
    task = add.delay(x, y)
    return {"task_id": task.id}

@app.get("/result/<task_id>")
def result(task_id: str):
    res = add.AsyncResult(task_id)
    if res.state == "PENDING":
        return {"state": res.state}, 202
    if res.state == "SUCCESS":
        return {"state": res.state, "result": res.result}
    return {"state": res.state}
