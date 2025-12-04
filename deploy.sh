#!/bin/bash

# Deploy Demo Service to Cloud Run
# This script deploys the demo service and configures it for testing

set -e

PROJECT_ID=${1:-$(gcloud config get-value project)}
SERVICE_NAME="aiops-demo-service"
REGION="us-central1"

echo "=================================================="
echo "Deploying AIOps Demo Service"
echo "=================================================="
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Build and deploy
echo "📦 Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --project $PROJECT_ID

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project $PROJECT_ID \
  --format='value(status.url)')

echo ""
echo "=================================================="
echo "✅ Deployment Complete!"
echo "=================================================="
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "Test endpoints:"
echo "  Health:      $SERVICE_URL/health"
echo "  Process:     $SERVICE_URL/api/process"
echo "  Slow:        $SERVICE_URL/api/slow"
echo "  Errors:      $SERVICE_URL/api/database"
echo "  Permission:  $SERVICE_URL/api/permission"
echo ""
echo "Generate test traffic:"
echo "  curl $SERVICE_URL/api/process"
echo "  curl $SERVICE_URL/api/slow"
echo "  curl $SERVICE_URL/api/database"
echo ""
echo "Wait 2-3 minutes for logs to appear, then test your AIOps Agent:"
echo "  python test_agent.py"
echo ""
