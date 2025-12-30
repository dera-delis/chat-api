# Quick Commit Script - Run after git config
# Make sure to run: git config user.name and git config user.email first!

Write-Host "Creating organized commits..." -ForegroundColor Green

# Reset any staged files
git reset

# 1. Initialize
Write-Host "`n1. Initializing project..." -ForegroundColor Cyan
git add .gitignore README.md requirements.txt app/__init__.py app/main.py
git commit -m "chore: initialize FastAPI chat API project"

# 2. Config
Write-Host "2. Adding config..." -ForegroundColor Cyan
git add app/config.py
git commit -m "config: add environment variables and settings"

# 3. Database
Write-Host "3. Setting up database..." -ForegroundColor Cyan
git add app/database.py app/models/ alembic.ini alembic/env.py alembic/script.py.mako alembic/versions/.gitkeep
git commit -m "db: setup PostgreSQL models and database connection"

# 4. Auth
Write-Host "4. Adding authentication..." -ForegroundColor Cyan
git add app/utils/jwt.py app/schemas/auth.py app/routers/auth.py app/utils/__init__.py
git commit -m "auth: implement JWT authentication for users"

# 5. Rooms
Write-Host "5. Adding rooms API..." -ForegroundColor Cyan
git add app/schemas/room.py app/routers/rooms.py
git commit -m "feat: add chat room CRUD endpoints"

# 6. WebSocket
Write-Host "6. Adding WebSocket..." -ForegroundColor Cyan
git add app/websocket/ app/routers/presence.py
git commit -m "feat: implement real-time messaging with WebSockets"

# 7. Redis
Write-Host "7. Integrating Redis..." -ForegroundColor Cyan
git add app/services/redis.py app/services/presence.py app/services/__init__.py
git commit -m "perf: integrate Redis for pub/sub and message caching"

# 8. Messages
Write-Host "8. Adding message persistence..." -ForegroundColor Cyan
git add app/schemas/message.py app/routers/messages.py
git commit -m "feat: save chat messages to database"

# 9. Security
Write-Host "9. Adding security..." -ForegroundColor Cyan
git add app/schemas/__init__.py app/routers/__init__.py
git commit -m "security: enforce room access control and validation"

# 10. Docker
Write-Host "10. Dockerizing..." -ForegroundColor Cyan
git add Dockerfile docker-compose.yml
git commit -m "devops: dockerize chat API with Redis and PostgreSQL"

# 11. Tests
Write-Host "11. Adding tests..." -ForegroundColor Cyan
git add tests/ alembic/versions/62b0588d11e2_initial_migration.py
git commit -m "test: add unit and integration tests for chat API"

# 12. Docs
Write-Host "12. Finalizing docs..." -ForegroundColor Cyan
git add QUICKSTART.md DEPLOYMENT.md PRE_DEPLOYMENT_CHECKLIST.md COMMIT_PLAN.md test_api.py scripts/ commit_roadmap.ps1 commit_roadmap.sh GIT_SETUP.md QUICK_COMMIT.ps1
git commit -m "docs: finalize README and API documentation"

Write-Host "`nAll commits complete! View history:" -ForegroundColor Green
git log --oneline

