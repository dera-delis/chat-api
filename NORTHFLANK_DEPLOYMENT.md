# Northflank Deployment Guide

Deploy your Chat API to Northflank - a modern platform that makes deployment simple and fast!

## 🚀 Why Northflank?

- **Simple UI** - Deploy from browser, no CLI needed
- **Built-in PostgreSQL** - One-click database setup
- **Built-in Redis** - Easy to add (or use external like Upstash)
- **GitHub Integration** - Auto-deploy on push
- **Free tier available** - Great for getting started
- **WebSocket support** - Perfect for real-time apps

## 📋 Prerequisites

1. **Northflank account** - Sign up at https://northflank.com
2. **GitHub account** - Your code is on GitHub
3. **That's it!** No SDK required

## 🚀 Step-by-Step Deployment

### Step 1: Sign Up / Login to Northflank

1. Go to [Northflank.com](https://northflank.com)
2. Click **"Sign Up"** or **"Log In"**
3. Sign in with **GitHub** (recommended - connects your repos)

### Step 2: Create New Project

1. Click **"New Project"**
2. Enter project name: `chat-api`
3. Click **"Create Project"**

### Step 3: Create PostgreSQL Service

1. In your project, click **"+ Add Service"**
2. Select **"Database"** > **"PostgreSQL"**
3. Configure:
   - **Service name**: `postgres`
   - **Version**: PostgreSQL 15
   - **Plan**: Choose based on needs (Free tier available)
4. Click **"Create"**

Northflank automatically creates the database and provides connection details.

### Step 4: Set Up Redis

You have two options for Redis:

#### Option A: Use Northflank Redis (If Available)

1. Click **"+ Add Service"** again
2. Select **"Database"** > **"Redis"**
3. Configure:
   - **Service name**: `redis`
   - **Version**: Redis 7
   - **Plan**: Choose based on needs
4. Click **"Create"**

**Note:** If you've reached your addon limit, use Option B below.

#### Option B: Use Upstash Redis (Recommended - Free Tier Available)

1. Go to [Upstash.com](https://upstash.com)
2. Sign up for a free account (or log in)
3. Click **"Create Database"**
4. Configure:
   - **Name**: `chat-api-redis`
   - **Type**: Regional (or Global for better performance)
   - **Region**: Choose closest to your Northflank region
   - **TLS**: Enable (recommended)
5. Click **"Create"**
6. Once created, go to **"Details"** tab
7. Copy the **"REST URL"** or **"Redis URL"**
   - Format: `redis://default:PASSWORD@HOST:PORT`
   - Or TLS: `rediss://default:PASSWORD@HOST:PORT`
8. Save this URL - you'll use it in Step 5

**Upstash Free Tier:**
- 10,000 commands per day
- Perfect for development and small projects
- No credit card required

### Step 5: Create Application Service

1. Click **"+ Add Service"**
2. Select **"Combined"** (or **"Build & Deploy"**)
3. Configure the service:

#### Source Configuration:
- **Source**: Select **"GitHub"**
- **Repository**: Select `dera-delis/chat-api`
- **Branch**: `main`
- **Build Type**: **"Dockerfile"**
- **Dockerfile Path**: `Dockerfile` (or leave default)

#### Service Settings:
- **Service name**: `chat-api`
- **Port**: `8000`
- **Health check path**: `/health` (optional)

#### Environment Variables:
Click **"Environment Variables"** and add:

```
DATABASE_URL = [Will be auto-populated from PostgreSQL service]
REDIS_URL = [See instructions below]
SECRET_KEY = [Generate a random 32+ character string]
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENVIRONMENT = production
PORT = 8000
```

**For DATABASE_URL:**
1. Under **"Linked Services"**, select:
   - `postgres` (PostgreSQL)
2. Northflank automatically provides the connection URL

**For REDIS_URL:**
- **If using Northflank Redis:** Under **"Linked Services"**, also select `redis` - Northflank will auto-populate the URL
- **If using Upstash Redis:** Manually paste the Redis URL you copied from Upstash (from Step 4, Option B)

**To generate SECRET_KEY:**
- Use: https://randomkeygen.com/
- Or in Northflank terminal: `openssl rand -hex 32`

#### Build & Deploy Settings:
- **Build command**: (leave empty, uses Dockerfile)
- **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Dockerfile path**: `Dockerfile`

4. Click **"Create"**

### Step 6: Configure Service Dependencies

1. Go to your `chat-api` service
2. Click **"Settings"** > **"Dependencies"**
3. Ensure:
   - `postgres` is listed and linked
   - `redis` is listed and linked (only if using Northflank Redis)
4. Northflank will wait for linked services before starting your app
5. **Note:** If using Upstash Redis, you don't need to link it as a dependency - just use the URL in environment variables

### Step 7: Run Database Migrations

**Option A: Via Northflank Terminal**

1. Go to your `chat-api` service
2. Click **"Terminal"** tab
3. Run:
   ```bash
   alembic upgrade head
   ```

**Option B: Add to Startup (Temporary)**

1. Go to service **"Settings"**
2. Update **"Start command"** to:
   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
3. After first deployment, change it back to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Step 8: Deploy

1. Northflank automatically starts building when you create the service
2. Go to **"Deployments"** tab to watch progress
3. Wait for build to complete (usually 2-5 minutes)
4. Once deployed, status will show **"Running"**

### Step 9: Get Your Live URL

1. Go to your `chat-api` service
2. Click **"Networking"** tab
3. You'll see your service URL:
   - Format: `https://chat-api-xxxxx.northflank.app`
4. Copy this URL - your API is live!

### Step 10: Test Your Deployment

1. Open: `https://YOUR_URL/health`
   - Should see: `{"status":"healthy"}`
2. Open: `https://YOUR_URL/docs`
   - Should see Swagger API documentation
3. Test endpoints!

## 🔄 Automatic Deployments

Northflank automatically deploys when you push to GitHub!

1. Make changes to your code
2. Push to GitHub: `git push origin main`
3. Northflank detects the push
4. Automatically builds and deploys
5. Done! (Usually takes 2-5 minutes)

## 🔧 Custom Domain (Optional)

1. Go to your service **"Networking"** tab
2. Click **"Add Custom Domain"**
3. Enter your domain
4. Follow Northflank's DNS instructions
5. SSL certificate is automatic

## 🔒 Security Best Practices

### Environment Variables

1. All variables in Northflank are encrypted
2. Database URLs are automatically secured
3. Never commit secrets to GitHub (already in `.gitignore`)

### Service Linking

- Use Northflank's service linking feature
- Automatically provides secure connection strings
- No need to manually copy/paste credentials

## 📊 Monitoring & Logs

### View Logs

1. Click on your service
2. Go to **"Logs"** tab
3. See real-time application logs
4. Filter by deployment, time, or search

### Metrics

1. Northflank dashboard shows:
   - CPU usage
   - Memory usage
   - Request count
   - Network traffic
   - Deployment status

### Alerts

1. Go to **"Settings"** > **"Alerts"**
2. Set up notifications for:
   - Deployment failures
   - High resource usage
   - Service downtime

## 💰 Pricing

Northflank offers:
- **Free tier**: Limited resources, great for testing
- **Pay as you go**: Based on actual usage
- **Team plans**: For production workloads

**Estimated cost for this app:**
- Small instance: ~$10-20/month
- Medium instance: ~$20-40/month

Check current pricing at: https://northflank.com/pricing

## 🔄 Updating Your Deployment

### Automatic (Recommended)

Just push to GitHub - Northflank auto-deploys!

```bash
git add .
git commit -m "Update feature"
git push origin main
```

### Manual Redeploy

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on any deployment
3. Or click **"Deploy"** to trigger new build

### Rollback

1. Go to **"Deployments"** tab
2. Find previous successful deployment
3. Click **"Redeploy"** to rollback

## 🐛 Troubleshooting

### Service Won't Start

1. Check **"Logs"** tab for errors
2. Verify environment variables are set
3. Check `DATABASE_URL` and `REDIS_URL` are linked correctly
4. Ensure services are in "Running" state
5. Check build logs for Docker errors

### Database Connection Errors

1. Verify PostgreSQL service is running (green status)
2. Check service is linked in dependencies
3. Verify `DATABASE_URL` environment variable exists
4. Check logs for connection errors

### Redis Connection Errors

1. **If using Northflank Redis:**
   - Verify Redis service is running
   - Check service is linked in dependencies
   - Verify `REDIS_URL` environment variable exists

2. **If using Upstash Redis:**
   - Verify `REDIS_URL` is correctly set in environment variables
   - Check the URL format: `redis://` or `rediss://` (for TLS)
   - Ensure Upstash database is active (check Upstash dashboard)
   - Verify you haven't exceeded free tier limits (10K commands/day)
   - Check logs for connection errors

### Migration Issues

1. Check logs for Alembic errors
2. Run migrations manually via terminal:
   ```bash
   alembic upgrade head
   ```
3. Or add to startup command temporarily

### Build Failures

1. Check **"Build Logs"** tab
2. Verify Dockerfile is correct
3. Check requirements.txt for issues
4. Ensure all dependencies are listed

### Port Issues

- Northflank uses the port you specify (8000)
- Make sure your Dockerfile/start command uses the correct port
- Check service settings for port configuration

## 📝 Northflank Configuration

### northflank.yaml (Optional)

Create `northflank.yaml` in your project root for advanced config:

```yaml
version: "1"

services:
  chat-api:
    type: combined
    source:
      type: github
      repository: dera-delis/chat-api
      branch: main
    build:
      type: dockerfile
      dockerfile: Dockerfile
    deploy:
      startCommand: uvicorn app.main:app --host 0.0.0.0 --port 8000
      healthCheckPath: /health
    environment:
      - name: SECRET_KEY
        value: your-secret-key-here
      - name: ALGORITHM
        value: HS256
      - name: ACCESS_TOKEN_EXPIRE_MINUTES
        value: "30"
      - name: ENVIRONMENT
        value: production
      - name: PORT
        value: "8000"
    links:
      - postgres
      # - redis  # Uncomment if using Northflank Redis, or use external Redis URL in environment
```

### Dockerfile for Northflank

Your existing `Dockerfile` works perfectly! Just ensure it uses the PORT:

```dockerfile
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## ✅ Deployment Checklist

- [ ] Northflank account created
- [ ] Project created
- [ ] PostgreSQL service created and running
- [ ] Redis service set up (Northflank or Upstash)
- [ ] Application service created
- [ ] Services linked (postgres, and redis if using Northflank Redis)
- [ ] Environment variables configured
- [ ] Service settings configured
- [ ] Database migrations run
- [ ] Service deployed and running
- [ ] Service URL obtained
- [ ] Health endpoint tested
- [ ] API docs accessible

## 🎉 You're Live!

Your Chat API is now deployed on Northflank!

**Service URL**: `https://YOUR_SERVICE.northflank.app`
**API Docs**: `https://YOUR_SERVICE.northflank.app/docs`

## 🔗 Useful Links

- [Northflank Dashboard](https://app.northflank.com)
- [Northflank Docs](https://docs.northflank.com)
- [Northflank Pricing](https://northflank.com/pricing)

## 💡 Pro Tips

1. **Use service linking** - Northflank handles connection strings automatically
2. **Monitor logs** - Check logs regularly for issues
3. **Set up alerts** - Get notified of problems
4. **Use preview deployments** - Test changes before production
5. **Scale easily** - Adjust resources in service settings
6. **Use health checks** - Northflank can monitor your service health

---

**That's it!** Northflank makes deployment simple. Connect GitHub and you're live! 🚀

