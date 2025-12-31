# Google Cloud Platform - Browser-Based Deployment Guide

This guide walks you through deploying the Chat API to Google Cloud Platform using only the web browser (Google Cloud Console) - no command line required!

## 📋 Prerequisites

1. **Google Cloud Account** - Sign up at https://cloud.google.com
2. **Billing enabled** on your GCP project
3. **Web browser** - That's it! No SDK needed.

## 🚀 Step-by-Step Browser Deployment

### Step 1: Create/Select a Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project dropdown at the top
3. Click **"New Project"** (or select existing)
4. Enter project name: `chat-api` (or your preferred name)
5. Click **"Create"**
6. Wait for project creation, then select it

### Step 2: Enable Required APIs

1. Go to **"APIs & Services" > "Library"** (or search "APIs" in top search bar)
2. Enable these APIs one by one (click "Enable" for each):
   - **Cloud Run API**
   - **Cloud SQL Admin API**
   - **Cloud Memorystore for Redis API**
   - **Cloud Build API**
   - **Container Registry API**

### Step 3: Create Cloud SQL PostgreSQL Database

1. Go to **"SQL"** in the left menu (or search "SQL")
2. Click **"Create Instance"**
3. Choose **"PostgreSQL"**
4. Fill in the form:
   - **Instance ID**: `chat-api-db`
   - **Password**: Set a strong password (save it securely!)
   - **Database version**: PostgreSQL 15
   - **Region**: Choose closest to you (e.g., `us-central1`)
   - **Machine type**: `Shared-core` > `db-f1-micro` (for testing)
5. Click **"Create Instance"** (takes 2-5 minutes)

#### Create Database and User

1. Once instance is ready, click on it
2. Go to **"Databases"** tab
3. Click **"Create Database"**
   - Name: `chat_db`
   - Click **"Create"**
4. Go to **"Users"** tab
5. Click **"Add User Account"**
   - Username: `chat_user`
   - Password: Use the same password you set for the instance
   - Click **"Add"**

### Step 4: Create Cloud Memorystore Redis Instance

1. Go to **"Memorystore"** in the left menu (or search "Memorystore")
2. Click **"Create Instance"**
3. Fill in:
   - **Instance ID**: `chat-api-redis`
   - **Version**: Redis 7.0
   - **Region**: Same as your SQL instance (e.g., `us-central1`)
   - **Tier**: Basic
   - **Capacity**: 1 GB
4. Click **"Create"** (takes 10-15 minutes)

**Note:** Save the Redis IP address shown after creation - you'll need it later!

### Step 5: Build Docker Image with Cloud Build

1. Go to **"Cloud Build" > "Triggers"** (or search "Cloud Build")
2. Click **"Create Trigger"**
3. Or use **"Cloud Build" > "History"** and click **"Run"** > **"Build"**

**Alternative: Use Cloud Shell (Browser-based terminal)**

1. Click the **Cloud Shell icon** (terminal icon) at the top right
2. Wait for Cloud Shell to open
3. Clone your repository:
   ```bash
   git clone https://github.com/dera-delis/chat-api.git
   cd chat-api
   ```
4. Build and push the image:
   ```bash
   # Set your project ID
   export PROJECT_ID=$(gcloud config get-value project)
   
   # Build and push
   gcloud builds submit --tag gcr.io/$PROJECT_ID/chat-api:latest
   ```

**Or use Container Registry directly:**

1. Go to **"Container Registry"** (or search "Container Registry")
2. Click **"Build"** or use Cloud Shell as shown above

### Step 6: Deploy to Cloud Run

1. Go to **"Cloud Run"** in the left menu (or search "Cloud Run")
2. Click **"Create Service"**
3. Fill in the deployment form:

#### Basic Settings:
- **Service name**: `chat-api`
- **Region**: Same as your database (e.g., `us-central1`)
- **Authentication**: Select **"Allow unauthenticated invocations"** (for testing)

#### Container Settings:
- **Container image URL**: Click **"Select"** and choose your image from Container Registry
  - Or enter: `gcr.io/YOUR_PROJECT_ID/chat-api:latest`
- **Port**: `8080`
- **Container port**: `8080`

#### Variables & Secrets:
Click **"Variables & Secrets"** tab and add these environment variables:

```
DATABASE_URL = postgresql://chat_user:YOUR_PASSWORD@/chat_db?host=/cloudsql/YOUR_PROJECT_ID:us-central1:chat-api-db
REDIS_URL = redis://REDIS_IP_ADDRESS:6379/0
SECRET_KEY = [Generate a random 32+ character string]
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENVIRONMENT = production
PORT = 8080
```

**Important:**
- Replace `YOUR_PASSWORD` with your database password
- Replace `YOUR_PROJECT_ID` with your actual project ID
- Replace `REDIS_IP_ADDRESS` with the IP from Step 4
- For `SECRET_KEY`, use a random string generator or: `openssl rand -hex 32` in Cloud Shell

#### Connections:
- **Cloud SQL connections**: Click **"Add Connection"**
  - Select your `chat-api-db` instance
  - Click **"Add"**

#### Advanced Settings (optional):
- **Memory**: 512 MiB
- **CPU**: 1
- **Timeout**: 300 seconds
- **Max instances**: 10

4. Click **"Create"** (takes 1-2 minutes)

### Step 7: Get Your Service URL

1. Once deployment completes, you'll see your service
2. Click on `chat-api` service
3. Copy the **Service URL** (e.g., `https://chat-api-xxxxx.run.app`)

### Step 8: Run Database Migrations

You need to run Alembic migrations. Use Cloud Shell:

1. Open **Cloud Shell** (terminal icon at top right)
2. Run:
   ```bash
   # Set your project
   export PROJECT_ID=$(gcloud config get-value project)
   
   # Get Cloud SQL connection name
   export CONNECTION_NAME="$PROJECT_ID:us-central1:chat-api-db"
   
   # Download Cloud SQL Proxy
   curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.linux.amd64
   chmod +x cloud-sql-proxy
   
   # Start proxy in background
   ./cloud-sql-proxy $CONNECTION_NAME &
   
   # Wait a moment, then run migrations
   docker run --rm \
     -e DATABASE_URL="postgresql://chat_user:YOUR_PASSWORD@127.0.0.1:5432/chat_db" \
     -v $(pwd):/app \
     gcr.io/$PROJECT_ID/chat-api:latest \
     alembic upgrade head
   ```

**Or use Cloud Run Job (Easier):**

1. Go to **"Cloud Run" > "Jobs"**
2. Click **"Create Job"**
3. Name: `chat-api-migrate`
4. Use same image: `gcr.io/YOUR_PROJECT_ID/chat-api:latest`
5. Add same environment variables as your service
6. Command override: `alembic upgrade head`
7. Add Cloud SQL connection
8. Click **"Create"**
9. Click **"Execute"** to run migrations

### Step 9: Test Your Deployment

1. Open your service URL in browser: `https://YOUR_SERVICE_URL/health`
2. Should see: `{"status":"healthy"}`
3. Open API docs: `https://YOUR_SERVICE_URL/docs`
4. Test endpoints!

## 🔧 Getting Connection Details

### Cloud SQL Connection String Format:
```
postgresql://chat_user:PASSWORD@/chat_db?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
```

To find your connection name:
1. Go to **"SQL"** > Your instance
2. Look for **"Connection name"** (format: `project:region:instance`)

### Redis IP Address:
1. Go to **"Memorystore"** > Your Redis instance
2. Copy the **"Primary Endpoint"** IP address

## 🔒 Security Best Practices (Browser Method)

### Use Secret Manager for Passwords:

1. Go to **"Secret Manager"** (search in console)
2. Click **"Create Secret"**
3. Create secrets:
   - `secret-key` - Your JWT secret
   - `db-password` - Database password
4. Go back to your Cloud Run service
5. Click **"Edit & Deploy New Revision"**
6. Go to **"Variables & Secrets"**
7. Click **"Reference a Secret"**
8. Add:
   - `SECRET_KEY` → Reference `secret-key`
   - `DB_PASSWORD` → Reference `db-password`
9. Update `DATABASE_URL` to use the secret

## 📊 Monitoring Your Deployment

1. Go to **"Cloud Run"** > Your service
2. Click **"Metrics"** tab to see:
   - Request count
   - Latency
   - Error rate
3. Click **"Logs"** tab to see application logs

## 🔄 Updating Your Deployment

1. Make changes to your code
2. Push to GitHub
3. In Cloud Shell:
   ```bash
   git clone https://github.com/dera-delis/chat-api.git
   cd chat-api
   gcloud builds submit --tag gcr.io/$PROJECT_ID/chat-api:latest
   ```
4. Go to **"Cloud Run"** > Your service
5. Click **"Edit & Deploy New Revision"**
6. Update the image tag or use latest
7. Click **"Deploy"**

## 💰 Cost Management

Monitor costs:
1. Go to **"Billing"** in left menu
2. Click **"Reports"** to see spending
3. Set up budget alerts:
   - Go to **"Budgets & Alerts"**
   - Click **"Create Budget"**
   - Set limit (e.g., $50/month)

## 🐛 Troubleshooting

### Service won't start:
- Check **"Logs"** tab in Cloud Run
- Verify environment variables are correct
- Check Cloud SQL connection is added

### Database connection errors:
- Verify connection name format
- Check database user password
- Ensure Cloud SQL connection is added to service

### Redis connection errors:
- Verify Redis IP address
- Check Redis instance is in same region
- May need VPC connector (see Advanced section)

## ✅ Deployment Checklist

- [ ] GCP project created
- [ ] Billing enabled
- [ ] Required APIs enabled
- [ ] Cloud SQL instance created
- [ ] Database and user created
- [ ] Redis instance created (IP saved)
- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed
- [ ] Environment variables set
- [ ] Cloud SQL connection added
- [ ] Migrations run
- [ ] Health endpoint tested
- [ ] API docs accessible

## 🎉 You're Done!

Your Chat API is now live on Google Cloud Platform! 

**Service URL**: `https://YOUR_SERVICE_URL`
**API Docs**: `https://YOUR_SERVICE_URL/docs`

---

**Need Help?** Check the logs in Cloud Run or review the [GCP_DEPLOYMENT.md](./GCP_DEPLOYMENT.md) for command-line alternatives.

