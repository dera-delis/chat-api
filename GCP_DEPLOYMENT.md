# Google Cloud Platform Deployment Guide

This guide walks you through deploying the Chat API to Google Cloud Platform using Cloud Run, Cloud SQL, and Cloud Memorystore.

## 🏗️ Architecture on GCP

```
┌─────────────────┐
│   Cloud Run     │  FastAPI Application
│   (Container)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼──────────┐
│Cloud  │ │Cloud         │
│SQL    │ │Memorystore   │
│(PG)   │ │(Redis)       │
└───────┘ └──────────────┘
```

## 📋 Prerequisites

1. **Google Cloud Account** - Sign up at https://cloud.google.com
2. **Google Cloud SDK (gcloud)** - Install from https://cloud.google.com/sdk/docs/install
3. **Docker** - For building container images
4. **Billing enabled** on your GCP project

## 🚀 Step-by-Step Deployment

### Step 1: Initialize GCP Project

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (create one if needed)
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Create Cloud SQL PostgreSQL Instance

```bash
# Create PostgreSQL instance
gcloud sql instances create chat-api-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_SECURE_PASSWORD

# Create database
gcloud sql databases create chat_db --instance=chat-api-db

# Create database user
gcloud sql users create chat_user \
  --instance=chat-api-db \
  --password=YOUR_SECURE_PASSWORD
```

**Note:** Replace `YOUR_SECURE_PASSWORD` with a strong password. Save it securely!

### Step 3: Create Cloud Memorystore Redis Instance

```bash
# Create Redis instance
gcloud redis instances create chat-api-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

**Note:** This may take 10-15 minutes to provision.

### Step 4: Get Connection Details

```bash
# Get Cloud SQL connection name
gcloud sql instances describe chat-api-db --format="value(connectionName)"

# Get Redis IP address
gcloud redis instances describe chat-api-redis --region=us-central1 --format="value(host)"
```

Save these values - you'll need them for environment variables.

### Step 5: Build and Push Docker Image

```bash
# Set project ID
export PROJECT_ID=$(gcloud config get-value project)

# Configure Docker to use gcloud
gcloud auth configure-docker

# Build and tag the image
docker build -t gcr.io/$PROJECT_ID/chat-api:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/chat-api:latest
```

### Step 6: Run Database Migrations

First, we need to run Alembic migrations. You can do this by:

**Option A: Using Cloud SQL Proxy (Recommended for local)**

```bash
# Download Cloud SQL Proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.linux.amd64
chmod +x cloud-sql-proxy

# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe chat-api-db --format="value(connectionName)")

# Run proxy in background
./cloud-sql-proxy $CONNECTION_NAME &

# Set DATABASE_URL to use localhost
export DATABASE_URL="postgresql://chat_user:YOUR_PASSWORD@127.0.0.1:5432/chat_db"

# Run migrations
docker run --rm \
  -e DATABASE_URL="$DATABASE_URL" \
  -v $(pwd):/app \
  gcr.io/$PROJECT_ID/chat-api:latest \
  alembic upgrade head
```

**Option B: Using Cloud Run Job (Alternative)**

Create a one-time Cloud Run job to run migrations (see Step 7 for Cloud Run setup first).

### Step 7: Deploy to Cloud Run

```bash
# Get connection details
CONNECTION_NAME=$(gcloud sql instances describe chat-api-db --format="value(connectionName)")
REDIS_IP=$(gcloud redis instances describe chat-api-redis --region=us-central1 --format="value(host)")

# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Deploy to Cloud Run
gcloud run deploy chat-api \
  --image gcr.io/$PROJECT_ID/chat-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --add-cloudsql-instances $CONNECTION_NAME \
  --set-env-vars "DATABASE_URL=postgresql://chat_user:YOUR_PASSWORD@localhost/chat_db?host=/cloudsql/$CONNECTION_NAME" \
  --set-env-vars "REDIS_URL=redis://$REDIS_IP:6379/0" \
  --set-env-vars "SECRET_KEY=$SECRET_KEY" \
  --set-env-vars "ALGORITHM=HS256" \
  --set-env-vars "ACCESS_TOKEN_EXPIRE_MINUTES=30" \
  --set-env-vars "ENVIRONMENT=production" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10
```

**Important:** Replace `YOUR_PASSWORD` with the actual database password you set in Step 2.

### Step 8: Run Migrations via Cloud Run

After deployment, run migrations:

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe chat-api --region=us-central1 --format="value(status.url)")

# Create a migration job (one-time)
gcloud run jobs create chat-api-migrate \
  --image gcr.io/$PROJECT_ID/chat-api:latest \
  --region us-central1 \
  --add-cloudsql-instances $CONNECTION_NAME \
  --set-env-vars "DATABASE_URL=postgresql://chat_user:YOUR_PASSWORD@localhost/chat_db?host=/cloudsql/$CONNECTION_NAME" \
  --set-env-vars "REDIS_URL=redis://$REDIS_IP:6379/0" \
  --set-env-vars "SECRET_KEY=$SECRET_KEY" \
  --memory 512Mi \
  --cpu 1

# Execute the migration job
gcloud run jobs execute chat-api-migrate --region us-central1
```

Or run migrations manually by connecting to the Cloud Run instance.

### Step 9: Update Dockerfile for Cloud Run

We need to ensure the Dockerfile doesn't run migrations automatically (Cloud Run handles this differently):

```dockerfile
# The current Dockerfile should work, but we'll modify the command
# In docker-compose, we run: alembic upgrade head && uvicorn...
# For Cloud Run, we'll just run uvicorn (migrations run separately)
```

Create a `Dockerfile.cloudrun`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application (Cloud Run uses PORT env var)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

### Step 10: Verify Deployment

```bash
# Get service URL
gcloud run services describe chat-api --region=us-central1 --format="value(status.url)"

# Test health endpoint
curl https://YOUR_SERVICE_URL/health

# Test API docs
open https://YOUR_SERVICE_URL/docs
```

## 🔧 Configuration Files

### Environment Variables for Cloud Run

Create a `.env.gcp` file (don't commit this):

```bash
# Database (Cloud SQL)
DATABASE_URL=postgresql://chat_user:PASSWORD@localhost/chat_db?host=/cloudsql/PROJECT:REGION:INSTANCE

# Redis (Cloud Memorystore)
REDIS_URL=redis://REDIS_IP:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
ENVIRONMENT=production
PORT=8080
```

## 🔒 Security Best Practices

1. **Use Secret Manager** for sensitive values:
```bash
# Create secrets
echo -n "your-secret-key" | gcloud secrets create secret-key --data-file=-
echo -n "db-password" | gcloud secrets create db-password --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding secret-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

2. **Update Cloud Run to use secrets**:
```bash
gcloud run services update chat-api \
  --update-secrets SECRET_KEY=secret-key:latest,DB_PASSWORD=db-password:latest
```

3. **Enable VPC connector** for Redis (if needed):
```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create chat-api-connector \
  --region=us-central1 \
  --subnet=default \
  --subnet-project=YOUR_PROJECT_ID \
  --min-instances=2 \
  --max-instances=3
```

## 📊 Monitoring & Logging

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=chat-api" --limit 50

# View metrics in Cloud Console
# Navigate to: Cloud Run > chat-api > Metrics
```

## 💰 Cost Estimation

- **Cloud Run**: ~$0.40 per million requests (free tier: 2M requests/month)
- **Cloud SQL (db-f1-micro)**: ~$7.67/month
- **Cloud Memorystore (1GB)**: ~$30/month
- **Total**: ~$38-50/month (after free tier)

## 🔄 Updating the Deployment

```bash
# Rebuild and push new image
docker build -t gcr.io/$PROJECT_ID/chat-api:latest .
docker push gcr.io/$PROJECT_ID/chat-api:latest

# Update Cloud Run service
gcloud run services update chat-api \
  --image gcr.io/$PROJECT_ID/chat-api:latest \
  --region us-central1
```

## 🐛 Troubleshooting

### Connection Issues

```bash
# Check Cloud SQL connection
gcloud sql instances describe chat-api-db

# Check Redis connection
gcloud redis instances describe chat-api-redis --region=us-central1

# View Cloud Run logs
gcloud run services logs read chat-api --region=us-central1
```

### Migration Issues

```bash
# Connect to database directly
gcloud sql connect chat-api-db --user=chat_user

# Check migration status
# Inside the database:
SELECT * FROM alembic_version;
```

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [Cloud Memorystore Documentation](https://cloud.google.com/memorystore/docs/redis)

## ✅ Deployment Checklist

- [ ] GCP project created and billing enabled
- [ ] Required APIs enabled
- [ ] Cloud SQL instance created
- [ ] Database and user created
- [ ] Cloud Memorystore Redis instance created
- [ ] Docker image built and pushed
- [ ] Cloud Run service deployed
- [ ] Database migrations run
- [ ] Environment variables configured
- [ ] Health endpoint tested
- [ ] API documentation accessible

---

**Ready to deploy?** Follow the steps above, and your Chat API will be live on Google Cloud Platform! 🚀

