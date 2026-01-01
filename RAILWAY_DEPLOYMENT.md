# Railway Deployment Guide

Deploy your Chat API to Railway - the simplest way to get your app live! Railway handles PostgreSQL, Redis, and deployments automatically.

## 🚂 Why Railway?

- **Zero configuration** - Just connect GitHub and deploy
- **Built-in PostgreSQL** - No setup needed
- **Built-in Redis** - One-click add
- **Automatic deployments** - Push to GitHub = auto deploy
- **Free tier available** - $5 credit monthly
- **Simple pricing** - Pay only for what you use

## 📋 Prerequisites

1. **Railway account** - Sign up at https://railway.app
2. **GitHub account** - Your code is already on GitHub
3. **That's it!** No SDK, no complex setup

## 🚀 Step-by-Step Deployment

### Step 1: Sign Up / Login to Railway

1. Go to [Railway.app](https://railway.app)
2. Click **"Login"** or **"Start a New Project"**
3. Sign in with **GitHub** (recommended - connects your repos automatically)

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select your `chat-api` repository
4. Click **"Deploy Now"**

Railway will automatically detect it's a Python app and start building!

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** > **"Add PostgreSQL"**
3. Railway automatically creates the database
4. Click on the PostgreSQL service
5. Go to **"Variables"** tab
6. Copy the **`DATABASE_URL`** - you'll need this!

### Step 4: Add Redis

1. Click **"+ New"** again
2. Select **"Database"** > **"Add Redis"**
3. Railway creates Redis automatically
4. Click on the Redis service
5. Go to **"Variables"** tab
6. Copy the **`REDIS_URL`** - you'll need this!

### Step 5: Configure Environment Variables

1. Click on your **main service** (the chat-api app)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these variables:

```
DATABASE_URL = [Paste from PostgreSQL service]
REDIS_URL = [Paste from Redis service]
SECRET_KEY = [Generate a random 32+ character string]
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENVIRONMENT = production
PORT = 8000
```

**To generate SECRET_KEY:**
- Use an online generator: https://randomkeygen.com/
- Or in Railway's built-in terminal: `openssl rand -hex 32`

### Step 6: Configure Service Settings

1. Still in your main service, go to **"Settings"** tab
2. Set:
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Healthcheck Path**: `/health` (optional but recommended)
3. Railway auto-detects port from `$PORT` env var

### Step 7: Run Database Migrations

1. Click on your main service
2. Go to **"Deployments"** tab
3. Click on the latest deployment
4. Click **"View Logs"** to see if it's running

**To run migrations, use Railway's built-in terminal:**

1. Click on your main service
2. Click **"Deployments"** tab
3. Click **"View Logs"**
4. Or use the **"Terminal"** tab (if available)
5. Run:
   ```bash
   alembic upgrade head
   ```

**Alternative: Add migration to startup (temporary)**

You can modify the start command temporarily:
```
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Then change it back after first deployment.

### Step 8: Get Your Live URL

1. Go to your main service
2. Click **"Settings"** tab
3. Under **"Domains"**, Railway provides a URL like:
   - `https://chat-api-production.up.railway.app`
4. Copy this URL - your API is live!

### Step 9: Test Your Deployment

1. Open: `https://YOUR_URL/health`
   - Should see: `{"status":"healthy"}`
2. Open: `https://YOUR_URL/docs`
   - Should see Swagger API documentation
3. Test endpoints!

## 🔄 Automatic Deployments

Railway automatically deploys when you push to GitHub!

1. Make changes to your code
2. Push to GitHub: `git push origin main`
3. Railway detects the push
4. Automatically builds and deploys
5. Done! (Usually takes 2-3 minutes)

## 🔧 Custom Domain (Optional)

1. Go to your service **"Settings"**
2. Under **"Domains"**, click **"Generate Domain"** or **"Custom Domain"**
3. For custom domain:
   - Add your domain
   - Follow Railway's DNS instructions
   - Wait for SSL certificate (automatic)

## 🔒 Security Best Practices

### Use Railway's Private Variables

Railway automatically marks database URLs as private. For `SECRET_KEY`:
1. Make sure it's added in **"Variables"** tab
2. Railway keeps it secure
3. Never commit secrets to GitHub (already in `.gitignore`)

### Environment-Specific Settings

Railway supports different environments:
- **Production** - Your live deployment
- **Preview** - Automatic preview deployments for PRs (optional)

## 📊 Monitoring & Logs

### View Logs

1. Click on your service
2. Go to **"Deployments"** tab
3. Click on a deployment
4. Click **"View Logs"**
5. See real-time application logs

### Metrics

1. Railway dashboard shows:
   - CPU usage
   - Memory usage
   - Request count
   - Deployment status

## 💰 Pricing

Railway's pricing is simple:
- **Free tier**: $5 credit monthly
- **Pay as you go**: ~$0.000463/GB RAM per hour
- **Database**: Included in usage
- **Bandwidth**: First 100GB free, then $0.10/GB

**Estimated cost for this app:**
- Small instance (512MB RAM): ~$5-10/month
- Medium instance (1GB RAM): ~$10-15/month

## 🔄 Updating Your Deployment

### Automatic (Recommended)

Just push to GitHub - Railway auto-deploys!

```bash
git add .
git commit -m "Update feature"
git push origin main
```

### Manual Redeploy

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on any deployment
3. Or click **"Deploy"** to trigger new build

## 🐛 Troubleshooting

### Service Won't Start

1. Check **"Logs"** tab for errors
2. Verify environment variables are set
3. Check `DATABASE_URL` and `REDIS_URL` are correct
4. Ensure `PORT` variable is set (Railway sets this automatically)

### Database Connection Errors

1. Verify `DATABASE_URL` is copied correctly from PostgreSQL service
2. Check PostgreSQL service is running (green status)
3. Ensure migrations have run

### Redis Connection Errors

1. Verify `REDIS_URL` is copied correctly from Redis service
2. Check Redis service is running
3. Check the URL format: `redis://default:PASSWORD@HOST:PORT`

### Migration Issues

1. Check logs for Alembic errors
2. Run migrations manually via terminal:
   ```bash
   alembic upgrade head
   ```
3. Or add to startup command temporarily

### Port Issues

Railway automatically sets `$PORT` - make sure your Dockerfile/start command uses it:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 📝 Railway-Specific Configuration

### railway.json (Optional)

Create `railway.json` in your project root for advanced config:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Dockerfile for Railway

Your existing `Dockerfile` should work, but ensure it uses `$PORT`:

```dockerfile
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## ✅ Deployment Checklist

- [ ] Railway account created
- [ ] Project created from GitHub repo
- [ ] PostgreSQL database added
- [ ] Redis instance added
- [ ] Environment variables configured
- [ ] Service settings configured
- [ ] Database migrations run
- [ ] Service URL obtained
- [ ] Health endpoint tested
- [ ] API docs accessible

## 🎉 You're Live!

Your Chat API is now deployed on Railway!

**Service URL**: `https://YOUR_PROJECT.up.railway.app`
**API Docs**: `https://YOUR_PROJECT.up.railway.app/docs`

## 🔗 Useful Links

- [Railway Dashboard](https://railway.app/dashboard)
- [Railway Docs](https://docs.railway.app)
- [Railway Pricing](https://railway.app/pricing)

## 💡 Pro Tips

1. **Use Railway's GitHub integration** - Automatic deployments on every push
2. **Monitor usage** - Check your dashboard regularly
3. **Set up alerts** - Railway can notify you of issues
4. **Use preview deployments** - Test PRs before merging
5. **Scale easily** - Adjust resources in settings if needed

---

**That's it!** Railway makes deployment incredibly simple. Just connect GitHub and you're live! 🚀

