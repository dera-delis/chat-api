# Commit Roadmap Script for Chat API (PowerShell)
# Run this script to create clean, organized commits

Write-Host "Starting commit roadmap for Chat API..." -ForegroundColor Green
Write-Host ""

# 1️⃣ Initialize Project
Write-Host "1. Initializing project..." -ForegroundColor Cyan
git add .gitignore README.md requirements.txt app/__init__.py app/main.py
git commit -m "chore: initialize FastAPI chat API project" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 1 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 1 skipped" -ForegroundColor Yellow }
Write-Host ""

# 2️⃣ Environment & Config Setup
Write-Host "2. Adding environment and config setup..." -ForegroundColor Cyan
git add app/config.py
git commit -m "config: add environment variables and settings" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 2 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 2 skipped" -ForegroundColor Yellow }
Write-Host ""

# 3️⃣ Database Setup
Write-Host "3. Setting up database..." -ForegroundColor Cyan
git add app/database.py app/models/ alembic.ini alembic/env.py alembic/script.py.mako alembic/versions/.gitkeep
git commit -m "db: setup PostgreSQL models and database connection" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 3 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 3 skipped" -ForegroundColor Yellow }
Write-Host ""

# 4️⃣ Authentication (JWT)
Write-Host "4. Implementing authentication..." -ForegroundColor Cyan
git add app/utils/jwt.py app/schemas/auth.py app/routers/auth.py app/utils/__init__.py
git commit -m "auth: implement JWT authentication for users" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 4 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 4 skipped" -ForegroundColor Yellow }
Write-Host ""

# 5️⃣ Chat Rooms API
Write-Host "5. Adding chat rooms API..." -ForegroundColor Cyan
git add app/schemas/room.py app/routers/rooms.py
git commit -m "feat: add chat room CRUD endpoints" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 5 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 5 skipped" -ForegroundColor Yellow }
Write-Host ""

# 6️⃣ WebSocket Real-Time Messaging
Write-Host "6. Implementing WebSocket messaging..." -ForegroundColor Cyan
git add app/websocket/ app/routers/presence.py
git commit -m "feat: implement real-time messaging with WebSockets" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 6 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 6 skipped" -ForegroundColor Yellow }
Write-Host ""

# 7️⃣ Redis Integration
Write-Host "7. Integrating Redis..." -ForegroundColor Cyan
git add app/services/redis.py app/services/presence.py app/services/__init__.py
git commit -m "perf: integrate Redis for pub/sub and message caching" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 7 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 7 skipped" -ForegroundColor Yellow }
Write-Host ""

# 8️⃣ Persist Chat History
Write-Host "8. Adding message persistence..." -ForegroundColor Cyan
git add app/schemas/message.py app/routers/messages.py
git commit -m "feat: save chat messages to database" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 8 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 8 skipped" -ForegroundColor Yellow }
Write-Host ""

# 9️⃣ Authorization & Security
Write-Host "9. Adding security enhancements..." -ForegroundColor Cyan
git add app/schemas/__init__.py app/routers/__init__.py
git commit -m "security: enforce room access control and validation" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 9 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 9 skipped" -ForegroundColor Yellow }
Write-Host ""

# 🔟 Dockerization
Write-Host "10. Dockerizing application..." -ForegroundColor Cyan
git add Dockerfile docker-compose.yml
git commit -m "devops: dockerize chat API with Redis and PostgreSQL" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 10 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 10 skipped" -ForegroundColor Yellow }
Write-Host ""

# 1️⃣1️⃣ Testing
Write-Host "11. Adding tests..." -ForegroundColor Cyan
git add tests/ alembic/versions/62b0588d11e2_initial_migration.py
git commit -m "test: add unit and integration tests for chat API" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 11 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 11 skipped" -ForegroundColor Yellow }
Write-Host ""

# 1️⃣2️⃣ Documentation & Polish
Write-Host "12. Finalizing documentation..." -ForegroundColor Cyan
git add QUICKSTART.md DEPLOYMENT.md PRE_DEPLOYMENT_CHECKLIST.md COMMIT_PLAN.md test_api.py scripts/
git commit -m "docs: finalize README and API documentation" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "✅ Commit 12 complete" -ForegroundColor Green } else { Write-Host "⚠️  Commit 12 skipped" -ForegroundColor Yellow }
Write-Host ""

Write-Host "All commits complete!" -ForegroundColor Green
Write-Host ""
Write-Host "View your commit history:" -ForegroundColor Cyan
git log --oneline

