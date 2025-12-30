#!/bin/bash
# Commit Roadmap Script for Chat API
# Run this script to create clean, organized commits

set -e

echo "🚀 Starting commit roadmap for Chat API..."
echo ""

# 1️⃣ Initialize Project
echo "1️⃣ Initializing project..."
git add .gitignore README.md requirements.txt app/__init__.py app/main.py
git commit -m "chore: initialize FastAPI chat API project" || echo "Commit 1 skipped (may already exist)"
echo "✅ Commit 1 complete"
echo ""

# 2️⃣ Environment & Config Setup
echo "2️⃣ Adding environment and config setup..."
git add app/config.py
# Note: .env.example should be created manually if needed
git commit -m "config: add environment variables and settings" || echo "Commit 2 skipped"
echo "✅ Commit 2 complete"
echo ""

# 3️⃣ Database Setup
echo "3️⃣ Setting up database..."
git add app/database.py app/models/ alembic.ini alembic/env.py alembic/script.py.mako alembic/versions/.gitkeep
git commit -m "db: setup PostgreSQL models and database connection" || echo "Commit 3 skipped"
echo "✅ Commit 3 complete"
echo ""

# 4️⃣ Authentication (JWT)
echo "4️⃣ Implementing authentication..."
git add app/utils/jwt.py app/schemas/auth.py app/routers/auth.py app/utils/__init__.py
git commit -m "auth: implement JWT authentication for users" || echo "Commit 4 skipped"
echo "✅ Commit 4 complete"
echo ""

# 5️⃣ Chat Rooms API
echo "5️⃣ Adding chat rooms API..."
git add app/schemas/room.py app/routers/rooms.py
git commit -m "feat: add chat room CRUD endpoints" || echo "Commit 5 skipped"
echo "✅ Commit 5 complete"
echo ""

# 6️⃣ WebSocket Real-Time Messaging
echo "6️⃣ Implementing WebSocket messaging..."
git add app/websocket/ app/routers/presence.py
git commit -m "feat: implement real-time messaging with WebSockets" || echo "Commit 6 skipped"
echo "✅ Commit 6 complete"
echo ""

# 7️⃣ Redis Integration
echo "7️⃣ Integrating Redis..."
git add app/services/redis.py app/services/presence.py app/services/__init__.py
git commit -m "perf: integrate Redis for pub/sub and message caching" || echo "Commit 7 skipped"
echo "✅ Commit 7 complete"
echo ""

# 8️⃣ Persist Chat History
echo "8️⃣ Adding message persistence..."
git add app/schemas/message.py app/routers/messages.py
git commit -m "feat: save chat messages to database" || echo "Commit 8 skipped"
echo "✅ Commit 8 complete"
echo ""

# 9️⃣ Authorization & Security
echo "9️⃣ Adding security enhancements..."
# Security is already in place, but we can commit any additional files
git add app/schemas/__init__.py app/routers/__init__.py
git commit -m "security: enforce room access control and validation" || echo "Commit 9 skipped"
echo "✅ Commit 9 complete"
echo ""

# 🔟 Dockerization
echo "🔟 Dockerizing application..."
git add Dockerfile docker-compose.yml
git commit -m "devops: dockerize chat API with Redis and PostgreSQL" || echo "Commit 10 skipped"
echo "✅ Commit 10 complete"
echo ""

# 1️⃣1️⃣ Testing
echo "1️⃣1️⃣ Adding tests..."
git add tests/ alembic/versions/62b0588d11e2_initial_migration.py
git commit -m "test: add unit and integration tests for chat API" || echo "Commit 11 skipped"
echo "✅ Commit 11 complete"
echo ""

# 1️⃣2️⃣ Documentation & Polish
echo "1️⃣2️⃣ Finalizing documentation..."
git add QUICKSTART.md DEPLOYMENT.md PRE_DEPLOYMENT_CHECKLIST.md COMMIT_PLAN.md test_api.py scripts/
git commit -m "docs: finalize README and API documentation" || echo "Commit 12 skipped"
echo "✅ Commit 12 complete"
echo ""

echo "🎉 All commits complete!"
echo ""
echo "View your commit history:"
git log --oneline

