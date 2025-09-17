# 🚢 Docker Multi‑Container Project (Volumes + Multiple Networks)

cd docker-multicontainer-project
cp .env.example .env   # edit passwords/ports
docker compose --env-file .env up -d --build

Perfect 🎉 — now your full multi-container stack is up and running:

* **nginx (web proxy)** → [http://localhost:8082](http://localhost:8082)
* **Flask app (behind nginx)** → [http://localhost:8082/](http://localhost:8082/)

  * `/health` → healthcheck
  * `/db` → insert/read rows
  * `/enqueue` → queue background tasks
* **Postgres** (with init SQL) → internal only
* **Redis** → internal only
* **Celery worker** → processes jobs from app
* **pgAdmin** → [http://localhost:8081](http://localhost:8081) (connect to host `db`, port `5432`, creds from `.env`)

✅ All containers are **healthy and running**.

Here’s a compact, copy-paste friendly **command catalog** for your multi-container project.
(Use one command per line—no inline comments—to avoid zsh errors.)

---

# 0) Go to the project

```bash
cd /path/to/docker-multicontainer-project
```

# 1) Launch / Stop / Rebuild

```bash
cp .env.example .env
docker compose --env-file .env up -d --build
docker compose ps
docker compose down
docker compose down -v
docker compose up -d --force-recreate
```

## Makefile shortcuts (if you prefer)

```bash
make up
make down
make wipe
make ps
make logs
```

---

# 2) App through Nginx (HTTP on \$NGINX\_HTTP\_PORT)

```bash
curl http://localhost:8082/
curl http://localhost:8082/health
```

# 3) DB via the App (Postgres)

```bash
curl -X POST http://localhost:8082/db -H 'Content-Type: application/json' -d '{"note":"hello from Atul"}'
curl http://localhost:8082/db
```

# 4) Background jobs (Celery via Redis)

```bash
TASK_ID=$(curl -s -X POST http://localhost:8082/enqueue -H 'Content-Type: application/json' -d '{"x":40,"y":2}' | jq -r .task_id)
curl http://localhost:8082/result/$TASK_ID
```

---

# 5) pgAdmin (UI)

Open in browser:

```
http://localhost:8081/
```

Then add a server with:

* Host: `db`
* Port: `5432`
* User: from `.env` (e.g., `appuser`)
* Password: from `.env`
* Database: from `.env`

### Reset pgAdmin admin user (re-seed from `.env`)

```bash
docker compose rm -s -f pgadmin
docker volume rm docker-multicontainer-project_pgadmin-data
docker compose --env-file .env up -d pgadmin
docker compose logs pgadmin --tail=100
```

---

# 6) Service Logs & Status

```bash
docker compose ps
docker compose logs app --tail=100
docker compose logs nginx --tail=100
docker compose logs db --tail=100
docker compose logs redis --tail=100
docker compose logs worker --tail=100
docker compose logs pgadmin --tail=100
```

---

# 7) Exec into Containers

```bash
docker exec -it web sh
docker compose exec app sh
docker compose exec db sh
docker compose exec cache sh
docker compose exec worker sh
docker compose exec pgadmin sh
```

---

# 8) Health & Connectivity (Inside containers)

```bash
docker exec -it web sh -lc 'wget -qO- http://localhost/health || curl -s http://localhost/health'
docker exec -it web sh -lc 'wget -qO- http://app:5000/health || curl -s http://app:5000/health'
docker compose exec app sh -lc 'curl -s http://localhost:5000/health'
```

---

# 9) Redis Quick Test (from app)

```bash
docker compose exec app sh -lc 'python - << "PY"
import os, redis
r = redis.Redis.from_url(os.getenv("REDIS_URL","redis://redis:6379/0"))
print("PING:", r.ping())
print("INCR hits:", r.incr("hits"))
PY'
```

---

# 10) Postgres Shell (psql)

```bash
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB
```

Inside psql:

```sql
\dt
SELECT * FROM visits ORDER BY id DESC LIMIT 10;
\q
```

---

# 11) Nginx Config Check & Reload

```bash
docker exec -it web sh -lc 'ls -l /etc/nginx/conf.d'
docker exec -it web sh -lc 'nginx -t'
docker compose restart nginx
```

---

# 12) Scaling Workers

```bash
docker compose up -d --scale worker=3
docker compose ps
```

---

# 13) Freeing Ports / Changing Ports

```bash
sudo lsof -nP -iTCP:8080 -sTCP:LISTEN
sudo lsof -nP -iTCP:8081 -sTCP:LISTEN
sudo lsof -nP -iTCP:8082 -sTCP:LISTEN
```

If needed, edit `.env` and then:

```bash
docker compose up -d
```

---

# 14) Inspect Effective Compose Config

```bash
docker compose config
docker compose config | grep -A1 PGADMIN_PORT
```

---

# 15) Networks & Volumes

```bash
docker network ls
docker network inspect docker-multicontainer-project_back-net
docker volume ls
docker volume inspect docker-multicontainer-project_db-data
```

---

# 16) Backup / Restore Volumes (example: pgAdmin)

```bash
VOL=docker-multicontainer-project_pgadmin-data
docker run --rm -v $VOL:/data -v "$PWD":/backup alpine sh -lc 'tar czf /backup/pgadmin-data-backup.tgz -C /data .'
ls -lh pgadmin-data-backup.tgz
```

Restore:

```bash
VOL=docker-multicontainer-project_pgadmin-data
docker run --rm -v $VOL:/data -v "$PWD":/backup alpine sh -lc 'rm -rf /data/* && tar xzf /backup/pgadmin-data-backup.tgz -C /data'
```

---

# 17) Common Fixes

```bash
docker compose restart nginx
docker compose up -d --force-recreate app nginx
docker exec -it web sh -lc 'tail -n 100 /var/log/nginx/error.log'
docker compose logs app --tail=200
```

---

If you want, I can ship an updated ZIP that includes:

* pgAdmin `9.8`,
* the corrected `curl` healthcheck for `app`,
* and the `version:` line removed from `docker-compose.yml`.



**Stack:** Nginx (reverse proxy), Flask (Gunicorn) app, Celery worker, PostgreSQL, Redis, pgAdmin  
**Networks:** `front-net` (edge), `back-net` (private)  
**Volumes:** DB/Redis/pgAdmin persistent data + Nginx logs + bind‑mounted app code

## Quickstart
```bash
cp .env.example .env   # edit secrets/ports
docker compose --env-file .env up -d --build
# or: make up
```

### Test
- App via Nginx: `http://localhost:${NGINX_HTTP_PORT:-8080}/`
- Health: `http://localhost:${NGINX_HTTP_PORT:-8080}/health`
- Insert row:
```bash
curl -X POST http://localhost:${NGINX_HTTP_PORT:-8080}/db -H 'Content-Type: application/json' -d '{"note":"from curl"}'
```
- Read rows: `http://localhost:${NGINX_HTTP_PORT:-8080}/db`
- Enqueue task:
```bash
curl -X POST http://localhost:${NGINX_HTTP_PORT:-8080}/enqueue -H 'Content-Type: application/json' -d '{"x":40,"y":2}'
```
- Check result: `http://localhost:${NGINX_HTTP_PORT:-8080}/result/<TASK_ID>`

### pgAdmin
- `http://localhost:${PGADMIN_PORT:-8081}`
- Add server: Host `db`, Port `5432`, credentials from `.env`

# 🚢 Docker Multi‑Container Project (Volumes + Multiple Networks)

A production‑style template with:

* **Containers**: `nginx` (reverse proxy), `app` (Flask + Gunicorn), `worker` (Celery), `db` (PostgreSQL), `redis` (cache/queue), `pgadmin` (DB UI)
* **Networks**: `front-net` (edge), `back-net` (private)
* **Volumes**: persistent data for Postgres/Redis/pgAdmin + bind‑mount for app code + nginx logs
* **Goodies**: healthchecks, .env config, Makefile, init SQL, graceful start order

---

## 🗂️ Repository Structure

```text
docker-multicontainer/
├─ docker-compose.yml
├─ .env.example
├─ Makefile
├─ README.md
├─ infra/
│  ├─ nginx/
│  │  └─ conf.d/
│  │     └─ default.conf
│  └─ db/
│     └─ init/
│        └─ 001_init.sql
├─ services/
│  ├─ app/
│  │  ├─ Dockerfile
│  │  ├─ requirements.txt
│  │  ├─ wsgi.py
│  │  └─ app.py
│  └─ worker/
│     └─ (uses app image)
└─ .gitignore
```

> You can copy‑paste files below into this structure (or change paths consistently).

---

## 🧰 `.env.example`

```env
# ── App
FLASK_ENV=production
SECRET_KEY=change-me
APP_PORT=5000

# ── Postgres
POSTGRES_DB=appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppassword

# ── Redis
REDIS_HOST=redis
REDIS_PORT=6379

# ── pgAdmin
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin1234
PGADMIN_PORT=8081

# ── Nginx
NGINX_HTTP_PORT=8080
```

Duplicate to `.env` and update secrets for real use.

---

## 🐳 `docker-compose.yml`

```yaml
version: "3.9"

x-healthcheck-defaults: &health
  interval: 10s
  timeout: 3s
  retries: 5
  start_period: 15s

services:
  nginx:
    image: nginx:alpine
    container_name: web
    depends_on:
      app:
        condition: service_healthy
    ports:
      - "${NGINX_HTTP_PORT:-8080}:80"
    volumes:
      - ./infra/nginx/conf.d:/etc/nginx/conf.d:ro
      - nginx-logs:/var/log/nginx
    networks:
      - front-net
      - back-net
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost/health || exit 1"]
      <<: *health

  app:
    build: ./services/app
    container_name: app
    environment:
      FLASK_ENV: ${FLASK_ENV}
      SECRET_KEY: ${SECRET_KEY}
      DB_URL: postgresql+psycopg://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@db:5432/$${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
      APP_PORT: ${APP_PORT}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./services/app:/app:cached
    expose:
      - "5000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - back-net
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:5000/health"]
      <<: *health

  worker:
    build: ./services/app
    container_name: worker
    command: ["bash", "-lc", "celery -A app.celery worker --loglevel=INFO"]
    environment:
      FLASK_ENV: ${FLASK_ENV}
      SECRET_KEY: ${SECRET_KEY}
      DB_URL: postgresql+psycopg://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@db:5432/$${POSTGRES_DB}
      REDIS_URL: redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - back-net

  db:
    image: postgres:16-alpine
    container_name: db
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./infra/db/init:/docker-entrypoint-initdb.d:ro
    networks:
      - back-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      <<: *health

  redis:
    image: redis:7-alpine
    container_name: cache
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis-data:/data
    networks:
      - back-net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      <<: *health

  pgadmin:
    image: dpage/pgadmin4:8.13
    container_name: pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_DEFAULT_EMAIL}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_DEFAULT_PASSWORD}
    ports:
      - "${PGADMIN_PORT:-8081}:80"
    volumes:
      - pgadmin-data:/var/lib/pgadmin
    depends_on:
      db:
        condition: service_healthy
    networks:
      - front-net
      - back-net

volumes:
  db-data:
  redis-data:
  pgadmin-data:
  nginx-logs:

networks:
  front-net:
    driver: bridge
  back-net:
    driver: bridge
```

> **Why multi‑network?** `front-net` exposes only `nginx` and `pgadmin` to the host, while `back-net` isolates internal services (`app`, `db`, `redis`, `worker`). `nginx` bridges both to proxy public traffic into the app.

---

## 🌐 Nginx reverse proxy — `infra/nginx/conf.d/default.conf`

```nginx
upstream app_upstream {
    server app:5000;
    keepalive 32;
}

server {
    listen 80;
    server_name _;

    location /health {
        return 200 'ok';
        add_header Content-Type text/plain;
    }

    location /static/ {
        alias /app/static/; # served from app container if mounted
    }

    location / {
        proxy_pass http://app_upstream;
        proxy_http_version 1.1;
        proxy_set_header Connection "keep-alive";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🗄️ DB init — `infra/db/init/001_init.sql`

```sql
CREATE TABLE IF NOT EXISTS visits (
  id SERIAL PRIMARY KEY,
  ts TIMESTAMP NOT NULL DEFAULT NOW(),
  note TEXT
);
```

---

## 🐍 App image — `services/app/Dockerfile`

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000
CMD ["bash", "-lc", "gunicorn --bind 0.0.0.0:5000 wsgi:app"]
```

### `services/app/requirements.txt`

```text
flask==3.0.3
gunicorn==22.0.0
psycopg[binary]==3.2.1
redis==5.0.7
celery==5.4.0
```

### `services/app/wsgi.py`

```python
from app import app
# Gunicorn entrypoint
```

### `services/app/app.py`

```python
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
```

---

## 🧪 Makefile (quality‑of‑life)

```makefile
SHELL := /bin/bash
ENV ?= .env

help:
	@grep -E '^[a-zA-Z_-]+:.*?## ' Makefile | sort | awk -F':|##' '{printf "\033[36m%-20s\033[0m %s\n", $$1, $$3}'

up: ## Start stack in background
	docker compose --env-file $(ENV) up -d --build
	docker compose ps
	docker compose logs -f --tail=50

down: ## Stop and remove containers (keeps volumes)
	docker compose down

wipe: ## Nuke everything (INCLUDING VOLUMES)
	docker compose down -v --remove-orphans

db:
	docker compose exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

ps: ## List containers
	docker compose ps

logs: ## Tail logs
	docker compose logs -f --tail=100
```

---

## 🪵 `.gitignore`

```gitignore
.env
__pycache__/
*.pyc
*.pyo
*.pyd
*.log
.eggs/
.pytest_cache/
.mypy_cache/
.venv/
.idea/
.vscode/

# Docker
**/.pytest_cache
**/__pycache__
**/*.pyc
```

---

## ▶️ Run It

1. **Copy** this repo layout and files.

2. Duplicate `.env.example` → `.env` and edit secrets/ports.

3. Launch:

```bash
make up
# or
docker compose --env-file .env up -d --build
```

4. Test endpoints:

* App via **Nginx**: `http://localhost:${NGINX_HTTP_PORT:-8080}/` → increments Redis `hits`
* Health: `http://localhost:${NGINX_HTTP_PORT:-8080}/health`
* Insert row:

  ```bash
  curl -X POST http://localhost:${NGINX_HTTP_PORT:-8080}/db \
    -H 'Content-Type: application/json' -d '{"note":"from curl"}'
  ```
* Read rows: `http://localhost:${NGINX_HTTP_PORT:-8080}/db`
* Queue task:

  ```bash
  curl -X POST http://localhost:${NGINX_HTTP_PORT:-8080}/enqueue -H 'Content-Type: application/json' -d '{"x":40,"y":2}'
  ```
* Check result: `http://localhost:${NGINX_HTTP_PORT:-8080}/result/<TASK_ID>`

5. Open **pgAdmin**: `http://localhost:${PGADMIN_PORT:-8081}`

   * Create a new server:

     * Host: `db`
     * Port: `5432`
     * User/Pass: from `.env`

6. Tear down:

```bash
make down        # keep volumes
make wipe        # remove volumes too
```

---

## 🔒 Security & Prod Notes

* Replace default secrets in `.env`.
* Consider **Docker secrets** for DB/passwords in production.
* Restrict pgAdmin to VPN or remove from `front-net`.
* Add **rate limits** & TLS termination at Nginx (or run behind a cloud LB).
* Add backups for `db-data` and `redis-data` volumes.

---

## 🧪 Troubleshooting

* **Port already in use** → change `NGINX_HTTP_PORT` / `PGADMIN_PORT`.
* **Cannot connect to DB** → check `db` health; ensure pgAdmin connects to `db` host on `back-net`.
* **Gunicorn not serving** → view `docker compose logs app`.
* **Nginx 502** → `app` health, or upstream name `app:5000`. Ensure `nginx` is on `back-net` too.

---

## ✅ What This Demonstrates

* Multi‑container orchestration with **compose**
* **Multiple networks** for edge vs private separation
* **Persistent volumes** for stateful services
* Reverse proxy, background workers, cache, and database
* Clean local DX via Makefile & healthchecks

Happy shipping! ☁️🐳

a complete, production-style Docker project (multi-container + volumes + multi-network) into the canvas for you—ready to copy as a repo. It includes:

nginx reverse proxy, Flask app (Gunicorn), Celery worker, Postgres, Redis, pgAdmin

front-net and back-net separation

persistent volumes, healthchecks, .env, Makefile, init SQL, and step-by-step run/test commands
