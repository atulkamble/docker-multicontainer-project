# 🚢 Docker Multi‑Container Project (Volumes + Multiple Networks)

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
