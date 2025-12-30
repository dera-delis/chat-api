# Git Setup & Commit Guide

## Step 1: Configure Git (Required First Time)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Or for this repository only:
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Step 2: Follow the Commit Roadmap

Run these commands in order to create clean, organized commits:

### 1️⃣ Initialize Project
```bash
git reset  # Unstage everything first
git add .gitignore README.md requirements.txt app/__init__.py app/main.py
git commit -m "chore: initialize FastAPI chat API project"
```

### 2️⃣ Environment & Config Setup
```bash
git add app/config.py
git commit -m "config: add environment variables and settings"
```

### 3️⃣ Database Setup
```bash
git add app/database.py app/models/ alembic.ini alembic/env.py alembic/script.py.mako alembic/versions/.gitkeep
git commit -m "db: setup PostgreSQL models and database connection"
```

### 4️⃣ Authentication (JWT)
```bash
git add app/utils/jwt.py app/schemas/auth.py app/routers/auth.py app/utils/__init__.py
git commit -m "auth: implement JWT authentication for users"
```

### 5️⃣ Chat Rooms API
```bash
git add app/schemas/room.py app/routers/rooms.py
git commit -m "feat: add chat room CRUD endpoints"
```

### 6️⃣ WebSocket Real-Time Messaging
```bash
git add app/websocket/ app/routers/presence.py
git commit -m "feat: implement real-time messaging with WebSockets"
```

### 7️⃣ Redis Integration
```bash
git add app/services/redis.py app/services/presence.py app/services/__init__.py
git commit -m "perf: integrate Redis for pub/sub and message caching"
```

### 8️⃣ Persist Chat History
```bash
git add app/schemas/message.py app/routers/messages.py
git commit -m "feat: save chat messages to database"
```

### 9️⃣ Authorization & Security
```bash
git add app/schemas/__init__.py app/routers/__init__.py
git commit -m "security: enforce room access control and validation"
```

### 🔟 Dockerization
```bash
git add Dockerfile docker-compose.yml
git commit -m "devops: dockerize chat API with Redis and PostgreSQL"
```

### 1️⃣1️⃣ Testing
```bash
git add tests/ alembic/versions/62b0588d11e2_initial_migration.py
git commit -m "test: add unit and integration tests for chat API"
```

### 1️⃣2️⃣ Documentation & Polish
```bash
git add QUICKSTART.md DEPLOYMENT.md PRE_DEPLOYMENT_CHECKLIST.md COMMIT_PLAN.md test_api.py scripts/ commit_roadmap.ps1 commit_roadmap.sh
git commit -m "docs: finalize README and API documentation"
```

## Step 3: Verify Commits

```bash
git log --oneline
```

You should see 12 commits following the roadmap.

## Step 4: Push to GitHub

```bash
# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/chat-api.git

# Push to GitHub
git push -u origin master
```

## Alternative: Single Script (PowerShell)

After configuring git, you can run:
```powershell
.\commit_roadmap.ps1
```

But you'll need to configure git first!

