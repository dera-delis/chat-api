# Northflank Deployment Guide

This guide will help you deploy the Chat API to Northflank.

## Prerequisites

1. A Northflank account (sign up at https://northflank.com)
2. GitHub repository connected to Northflank
3. Your repository: `https://github.com/dera-delis/chat-api`

## Step 1: Connect Repository to Northflank

1. Log in to your Northflank dashboard
2. Click **"New Project"** or select an existing project
3. Click **"Add Service"** → **"From Git"**
4. Connect your GitHub account and select the `chat-api` repository
5. Select the `main` branch

## Step 2: Configure Services

### Main Application Service

1. **Service Name**: `chat-api`
2. **Build Type**: Dockerfile
3. **Dockerfile Path**: `Dockerfile`
4. **Context**: `.` (root directory)
5. **Port**: `8000`

### Environment Variables

Add these environment variables in Northflank:

```
DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<database>
REDIS_URL=redis://<host>:6379/0
SECRET_KEY=<generate-a-strong-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

**Important**: Generate a strong SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Add PostgreSQL Database

1. In your Northflank project, click **"Add Service"** → **"Database"** → **"PostgreSQL"**
2. **Version**: 15
3. **Database Name**: `chat_db`
4. **Username**: `chat_user` (or auto-generated)
5. **Password**: (auto-generated or set your own)
6. Copy the connection string and use it as `DATABASE_URL`

## Step 4: Add Redis Cache

1. Click **"Add Service"** → **"Cache"** → **"Redis"**
2. **Version**: 7
3. Copy the connection URL and use it as `REDIS_URL`

## Step 5: Configure Build & Deploy

### Build Configuration

- **Build Command**: (auto-detected from Dockerfile)
- **Start Command**: Already in Dockerfile
- **Health Check**: `/health`

### Deployment Settings

1. **Auto-deploy**: Enable for `main` branch
2. **Build on push**: Yes
3. **Deploy strategy**: Rolling update

## Step 6: Run Database Migrations

After the first deployment, you need to run migrations:

### Option 1: Via Northflank Console

1. Go to your `chat-api` service
2. Click **"Console"** or **"Terminal"**
3. Run:
```bash
alembic upgrade head
```

### Option 2: Automatic (Recommended)

The Dockerfile now includes migrations in the startup command, so they run automatically on each deployment.

## Step 7: Verify Deployment

1. Check service logs in Northflank dashboard
2. Test health endpoint: `https://your-service-url.northflank.app/health`
3. Test API docs: `https://your-service-url.northflank.app/docs`

## Step 8: Update CORS (If Needed)

If you're deploying a frontend, update CORS in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Update this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection string | `redis://host:6379/0` |
| `SECRET_KEY` | JWT secret key (change in production!) | `your-secret-key-here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `ENVIRONMENT` | Environment name | `production` |

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is correct
- Check database service is running
- Ensure network connectivity between services

### Redis Connection Issues

- Verify `REDIS_URL` is correct
- Check Redis service is running
- Test connection from console

### Migration Issues

- Check logs for migration errors
- Run migrations manually via console
- Verify database permissions

### Build Failures

- Check Dockerfile syntax
- Verify all dependencies in `requirements.txt`
- Review build logs in Northflank

## Monitoring

- **Logs**: View real-time logs in Northflank dashboard
- **Metrics**: Monitor CPU, memory, and request metrics
- **Health Checks**: Automatic health monitoring at `/health`

## Scaling

Northflank supports auto-scaling:
- Configure min/max instances in service settings
- Set up resource limits
- Monitor performance metrics

## Next Steps

1. Set up custom domain (optional)
2. Configure SSL/TLS certificates
3. Set up monitoring and alerts
4. Configure backup schedules for database
5. Set up CI/CD pipeline (if not using auto-deploy)

## Support

- Northflank Docs: https://docs.northflank.com
- Northflank Support: support@northflank.com

