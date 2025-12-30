# Commit Plan for Chat API

Follow these commits in order to create a clean git history:

## 1️⃣ Initialize Project
```bash
git add .gitignore README.md requirements.txt app/__init__.py app/main.py
git commit -m "chore: initialize FastAPI chat API project"
```

## 2️⃣ Environment & Config Setup
```bash
git add app/config.py .env.example
git commit -m "config: add environment variables and settings"
```

## 3️⃣ Database Setup
```bash
git add app/database.py app/models/ alembic.ini alembic/env.py alembic/script.py.mako
git commit -m "db: setup PostgreSQL models and database connection"
```

## 4️⃣ Authentication (JWT)
```bash
git add app/utils/jwt.py app/schemas/auth.py app/routers/auth.py
git commit -m "auth: implement JWT authentication for users"
```

## 5️⃣ Chat Rooms API
```bash
git add app/schemas/room.py app/routers/rooms.py
git commit -m "feat: add chat room CRUD endpoints"
```

## 6️⃣ WebSocket Real-Time Messaging
```bash
git add app/websocket/ app/routers/presence.py
git commit -m "feat: implement real-time messaging with WebSockets"
```

## 7️⃣ Redis Integration
```bash
git add app/services/redis.py app/services/presence.py
git commit -m "perf: integrate Redis for pub/sub and message caching"
```

## 8️⃣ Persist Chat History
```bash
git add app/schemas/message.py app/routers/messages.py
git commit -m "feat: save chat messages to database"
```

## 9️⃣ Authorization & Security
```bash
# Already included in previous commits, but you can add any additional security files
git add app/utils/__init__.py
git commit -m "security: enforce room access control and validation"
```

## 🔟 Dockerization
```bash
git add Dockerfile docker-compose.yml
git commit -m "devops: dockerize chat API with Redis and PostgreSQL"
```

## 1️⃣1️⃣ Testing
```bash
git add tests/ alembic/versions/
git commit -m "test: add unit and integration tests for chat API"
```

## 1️⃣2️⃣ Documentation & Polish
```bash
git add QUICKSTART.md DEPLOYMENT.md PRE_DEPLOYMENT_CHECKLIST.md COMMIT_PLAN.md test_api.py scripts/
git commit -m "docs: finalize README and API documentation"
```

---

## Quick Script (Run all at once)

```bash
# 1. Initialize
git add .gitignore README.md requirements.txt app/__init__.py app/main.py
git commit -m "chore: initialize FastAPI chat API project"

# 2. Config
git add app/config.py
git commit -m "config: add environment variables and settings"

# 3. Database
git add app/database.py app/models/ alembic.ini alembic/env.py alembic/script.py.mako
git commit -m "db: setup PostgreSQL models and database connection"

# 4. Auth
git add app/utils/jwt.py app/schemas/auth.py app/routers/auth.py
git commit -m "auth: implement JWT authentication for users"

# 5. Rooms
git add app/schemas/room.py app/routers/rooms.py
git commit -m "feat: add chat room CRUD endpoints"

# 6. WebSocket
git add app/websocket/ app/routers/presence.py
git commit -m "feat: implement real-time messaging with WebSockets"

# 7. Redis
git add app/services/
git commit -m "perf: integrate Redis for pub/sub and message caching"

# 8. Messages
git add app/schemas/message.py app/routers/messages.py
git commit -m "feat: save chat messages to database"

# 9. Security (utils already added, but commit separately)
git commit --allow-empty -m "security: enforce room access control and validation"

# 10. Docker
git add Dockerfile docker-compose.yml
git commit -m "devops: dockerize chat API with Redis and PostgreSQL"

# 11. Tests
git add tests/ alembic/versions/
git commit -m "test: add unit and integration tests for chat API"

# 12. Docs
git add QUICKSTART.md DEPLOYMENT.md PRE_DEPLOYMENT_CHECKLIST.md COMMIT_PLAN.md test_api.py scripts/ .gitignore
git commit -m "docs: finalize README and API documentation"
```

