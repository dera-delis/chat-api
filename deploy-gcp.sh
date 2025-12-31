#!/bin/bash
# Quick deployment script for Google Cloud Platform

set -e

echo "🚀 Deploying Chat API to Google Cloud Platform..."
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Project ID: $PROJECT_ID"
echo ""

# Build and push Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.cloudrun -t gcr.io/$PROJECT_ID/chat-api:latest .

echo "📤 Pushing to Google Container Registry..."
gcloud auth configure-docker --quiet
docker push gcr.io/$PROJECT_ID/chat-api:latest

echo ""
echo "✅ Image pushed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Create Cloud SQL instance: gcloud sql instances create chat-api-db --database-version=POSTGRES_15 --tier=db-f1-micro --region=us-central1"
echo "2. Create Redis instance: gcloud redis instances create chat-api-redis --size=1 --region=us-central1"
echo "3. Deploy to Cloud Run using the commands in GCP_DEPLOYMENT.md"
echo ""
echo "📖 See GCP_DEPLOYMENT.md for complete deployment instructions"

