# Deployment Guide (Northflank + Upstash)

This API is intended to run on Northflank with Redis hosted on Upstash.

## ✅ Requirements
- Northflank service (Docker container)
- Managed Postgres (Northflank or external)
- Upstash Redis instance (external)
- WebSocket support enabled on the Northflank service

## 🧩 Required Environment Variables
Set these in the Northflank service configuration:

```
DATABASE_URL=postgresql://<user>:<pass>@<host>:<port>/<db>
REDIS_URL=rediss://:<password>@<upstash-host>:<upstash-port>
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> For Upstash, use the **rediss://** URL from the Upstash dashboard.

## 🔌 WebSocket Notes
- Ensure the platform allows WebSocket upgrades.
- Health check: `GET /health`
- Docs: `GET /docs`

## 🧱 Docker Image
Northflank can build directly from this repo using the `Dockerfile`.

## ✅ Post-deploy Checks
1. `/health` returns `{ "status": "healthy" }`
2. `/docs` loads correctly
3. WebSocket connect:  
   `wss://<your-domain>/ws/chat/{room_id}?token=<JWT>`

## ⚠️ Production Notes
- Redis is required for presence + Pub/Sub.
- Rate limiting and abuse prevention are planned for production.

