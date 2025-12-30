# Deployment Checklist

## Pre-Deployment Checklist

### ✅ Code Quality
- [x] All tests passing
- [x] No hardcoded secrets in code
- [x] Environment variables properly configured
- [x] Database migrations ready

### ✅ Security
- [x] `.env` file in `.gitignore`
- [x] `.env.example` provided (create from template)
- [x] SECRET_KEY should be changed in production
- [x] CORS configured (currently allows all - update for production)

### ✅ Dependencies
- [x] All dependencies in `requirements.txt`
- [x] No unused dependencies
- [x] Version pins for stability

### ✅ Docker
- [x] Dockerfile optimized
- [x] docker-compose.yml configured
- [x] Health checks configured
- [x] Volumes for data persistence

## Deployment Steps

### 1. GitHub Setup

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Real-time chat API"

# Add remote
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Environment Configuration

**IMPORTANT:** Before deploying, create a `.env` file:

```bash
cp .env.example .env
```

Then edit `.env` and change:
- `SECRET_KEY` - Use a strong random string (at least 32 characters)
- `DATABASE_URL` - Update for your production database
- `REDIS_URL` - Update for your production Redis
- `ENVIRONMENT` - Set to `production`

### 3. Production Deployment

#### Option A: Docker Compose (Recommended for VPS)

```bash
# Clone repository
git clone <your-repo-url>
cd chat-api

# Create .env file
cp .env.example .env
# Edit .env with production values

# Start services
docker-compose up -d

# Run migrations (if not auto-run)
docker-compose exec app alembic upgrade head
```

#### Option B: Cloud Platform (Heroku, Railway, Render, etc.)

1. **Set Environment Variables** in your platform's dashboard:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `SECRET_KEY`
   - `ALGORITHM=HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES=30`
   - `ENVIRONMENT=production`

2. **Deploy** using platform-specific commands

3. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

### 4. Post-Deployment

- [ ] Verify health endpoint: `GET /health`
- [ ] Test authentication: `POST /auth/signup` and `POST /auth/login`
- [ ] Test WebSocket connection
- [ ] Monitor logs: `docker-compose logs -f app`
- [ ] Set up database backups
- [ ] Configure CORS for your frontend domain

## Production Considerations

### Security
1. **Change SECRET_KEY** - Generate a strong random key:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **Update CORS** - In `app/main.py`, replace:
   ```python
   allow_origins=["*"]  # Remove this
   ```
   With:
   ```python
   allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"]
   ```

3. **Use HTTPS** - Always use HTTPS in production

4. **Database Security**:
   - Use strong database passwords
   - Restrict database access to application servers only
   - Enable SSL for database connections

### Performance
1. **Redis Connection Pooling** - Already configured
2. **Database Connection Pooling** - SQLAlchemy handles this
3. **WebSocket Scaling** - Redis Pub/Sub enables horizontal scaling

### Monitoring
- Set up logging aggregation
- Monitor API response times
- Track WebSocket connection counts
- Monitor Redis and PostgreSQL performance

## Troubleshooting

### Database Connection Issues
```bash
# Check database is running
docker-compose ps postgres

# Check connection
docker-compose exec app python -c "from app.database import engine; engine.connect()"
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Migration Issues
```bash
# Check current migration
docker-compose exec app alembic current

# Rollback if needed
docker-compose exec app alembic downgrade -1
```

## Notes

- The `test_api.py` file is for local testing and can be kept or removed
- Migration files in `alembic/versions/` should be committed to git
- Never commit `.env` files with real secrets

