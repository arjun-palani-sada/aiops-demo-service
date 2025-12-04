# 🎪 AIOps Demo Service - Error Generation for Testing

A Flask-based demo service that generates realistic production errors for testing the AIOps Agent. Deploys to Google Cloud Run and creates various error patterns (permissions, network, database, etc.) for comprehensive agent validation.

## 🎯 What It Does

This service provides:
- ✅ **Multiple error endpoints** (403, 500, 503, timeouts)
- ✅ **Realistic error patterns** matching production scenarios
- ✅ **Cloud Logging integration** for proper log formatting
- ✅ **Traffic generation tools** for creating investigation scenarios
- ✅ **Health checks** to verify deployment

**Perfect for testing your AIOps Agent!** 🤖

---

## 📋 Prerequisites

### Required:
- **Google Cloud Platform account** with active project
- **gcloud CLI** installed and configured
- **Cloud Run API** enabled
- **Cloud Logging API** enabled
- **Artifact Registry API** or **Container Registry API** enabled

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd demo-service

# (Optional) Create virtual environment for traffic generator
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies for traffic generator
pip install requests
```

### 2. Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Setup Application Default Credentials
gcloud auth application-default login

# Verify authentication
gcloud auth list
```

### 3. Deploy to Cloud Run

```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy (takes 2-3 minutes)
./deploy.sh

# Output will show your service URL:
# Service URL: https://aiops-demo-service-xxx.us-central1.run.app
```

**Save this URL - you'll need it for testing!**

### 4. Verify Deployment

```bash
# Get your service URL
export SERVICE_URL=$(gcloud run services describe aiops-demo-service \
  --region=us-central1 \
  --format='value(status.url)')

# Test health endpoint (should return 200)
curl $SERVICE_URL/health

# Should see: {"status": "healthy", "service": "aiops-demo-service"}
```

---

## 🎮 Using the Service

### Available Endpoints

The service provides several endpoints that generate different error patterns:

| Endpoint | Behavior | Status Codes | Use Case |
|----------|----------|--------------|----------|
| `/` or `/health` | Always healthy | 200 | Health checks |
| `/api/process` | 30% random errors | 200, 400, 403, 503, 504 | General errors |
| `/api/slow` | 2-5 second delays | 200 | Performance issues |
| `/api/database` | 50% connection failures | 200, 503 | Database errors |
| `/api/permission` | Always fails | 403 | Permission errors |
| `/api/network` | Network timeouts | 503 | Network issues |
| `/api/memory-leak` | Memory leak simulation | 200 | Resource issues |
| `/api/crash` | Intentional crashes | 500 | Critical failures |
| `/api/cpu-spike` | CPU-intensive work | 200 | Resource exhaustion |

### Error Types Generated

**Permission Errors (403)**
```bash
curl https://your-service.run.app/api/permission
# Returns: {"error": "Permission denied"}
# Logs: "Permission denied: Insufficient privileges"
```

**Network Errors (503)**
```bash
curl https://your-service.run.app/api/network
# Returns: {"error": "Service Unavailable"}
# Logs: "Network error: Connection timeout"
```

**Database Errors (503)**
```bash
curl https://your-service.run.app/api/database
# 50% chance of: {"error": "Database connection failed"}
# Logs: "Database connection pool exhausted"
```

---

## 🎯 Generating Traffic for Testing

### Method 1: Authenticated Traffic Generator (Recommended)

Use when your service requires authentication (organization policy):

```bash
# Set your service URL
export SERVICE_URL=https://your-service-url.run.app

# Generate 5 minutes of mixed traffic
python3 generate_traffic_auth.py $SERVICE_URL 5

# Output shows:
# ✅ /api/process -> 200
# ❌ /api/permission -> 403
# ❌ /api/network -> 503
# ...
```

### Method 2: Focused Error Generation

Generate specific error types for targeted testing:

**Permission Errors Only:**
```bash
# Generate 50 permission errors
for i in {1..50}; do
  python3 -c "
import requests, subprocess
token = subprocess.check_output(['gcloud', 'auth', 'print-identity-token'], text=True).strip()
requests.get('$SERVICE_URL/api/permission', headers={'Authorization': f'Bearer {token}'})
print('.', end='', flush=True)
"
done
echo ""
```

**Database Errors:**
```bash
# Generate 30 database errors
for i in {1..30}; do
  python3 -c "
import requests, subprocess
token = subprocess.check_output(['gcloud', 'auth', 'print-identity-token'], text=True).strip()
requests.get('$SERVICE_URL/api/database', headers={'Authorization': f'Bearer {token}'})
"
done
```

**Mixed Traffic:**
```bash
# Generate diverse error patterns
python3 generate_traffic_auth.py $SERVICE_URL 3
```

---

## 🧪 Complete Testing Workflow

### End-to-End Test (15 minutes)

```bash
# 1. Deploy the service (3 min)
./deploy.sh

# 2. Generate traffic (5 min)
export SERVICE_URL=https://your-service.run.app
python3 generate_traffic_auth.py $SERVICE_URL 5

# 3. Wait for logs to propagate (2 min)
sleep 120

# 4. Verify logs exist
gcloud logging read "resource.labels.service_name=aiops-demo-service" --limit=10

# 5. Test with AIOps Agent (in separate repo)
cd ../aiops-agent-final
python3 test_aiops_agent.py aiops-demo-service
```

### Expected Results

After running the workflow above, the AIOps Agent should detect:

```
Root Cause: Permission or authorization errors detected in 45/50 logs
Confidence: 90%
Duration: 6.5s

Recommended Actions:
1. Verify IAM permissions
2. Check service account configuration
3. Review audit logs
```

---

## 🎪 Traffic Generation Patterns

### Pattern 1: Permission Issues
```bash
# Creates: 403 errors for IAM testing
python3 generate_focused_errors.py $SERVICE_URL permission 50
```

**Use with AIOps Agent:**
```bash
# Agent should detect: "Permission errors" with 90%+ confidence
```

### Pattern 2: Network Issues
```bash
# Creates: 503 network errors
python3 generate_focused_errors.py $SERVICE_URL network 40
```

**Use with AIOps Agent:**
```bash
# Agent should detect: "Network connectivity issues" with 85%+ confidence
```

### Pattern 3: Mixed Issues (Realistic)
```bash
# Creates: Various errors like production
python3 generate_traffic_auth.py $SERVICE_URL 5
```

**Use with AIOps Agent:**
```bash
# Agent should identify dominant pattern (usually highest error count)
```

---

## 📊 Monitoring Your Service

### View Logs

```bash
# Recent logs
gcloud logging read "resource.labels.service_name=aiops-demo-service" \
  --limit=20 \
  --format=json

# Specific error type
gcloud logging read \
  'resource.labels.service_name=aiops-demo-service AND severity>=WARNING' \
  --limit=10

# Logs in specific time range
gcloud logging read \
  'resource.labels.service_name=aiops-demo-service 
   AND timestamp>="2025-12-04T10:00:00Z"' \
  --limit=10
```

### View Metrics

```bash
# Service metrics in Cloud Console
gcloud monitoring dashboards create \
  --config-from-file=dashboard-config.json

# Or view in console:
# https://console.cloud.google.com/run/detail/us-central1/aiops-demo-service
```

### Check Service Health

```bash
# Health check
curl $SERVICE_URL/health

# Service info
gcloud run services describe aiops-demo-service --region=us-central1

# Recent requests
gcloud logging read "resource.type=cloud_run_revision 
  AND resource.labels.service_name=aiops-demo-service" \
  --limit=5
```

---

## 🛠️ Troubleshooting

### Service Returns 403 (Forbidden)

**Problem**: Organization policy blocks unauthenticated requests.

**Solution**: Use the authenticated traffic generator:
```bash
python3 generate_traffic_auth.py $SERVICE_URL 5
```

### No Logs Appearing

**Problem**: Logs take 2-3 minutes to propagate.

**Solutions**:
```bash
# 1. Wait longer
sleep 180

# 2. Verify logging is enabled
gcloud logging read "resource.labels.service_name=aiops-demo-service" --limit=1

# 3. Check if service is receiving requests
gcloud run services describe aiops-demo-service --region=us-central1
```

### Deployment Fails

**Problem**: Missing APIs or permissions.

**Solutions**:
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable logging.googleapis.com

# Check IAM permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

### Service Crashes

**Problem**: Container fails to start.

**Solutions**:
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# View recent errors
gcloud run services logs read aiops-demo-service \
  --region=us-central1 \
  --limit=50
```

---

## 🏗️ Project Structure

```
demo-service/
├── app.py                        # Flask application
├── Dockerfile                    # Container definition
├── requirements.txt              # Python dependencies
├── deploy.sh                     # Deployment script
├── generate_traffic_auth.py      # Authenticated traffic generator
├── generate_traffic.py           # Simple traffic generator
├── test_agent.py                 # AIOps Agent test script
├── README.md                     # This file
└── TESTING_GUIDE.md             # Detailed testing scenarios
```

---

## 🎯 Configuration

### Environment Variables (in deploy.sh)

```bash
# Service configuration
SERVICE_NAME=aiops-demo-service
REGION=us-central1
MEMORY=512Mi
CPU=1
MIN_INSTANCES=0
MAX_INSTANCES=10
```

### Service Customization

Edit `app.py` to customize error behavior:

```python
# Adjust error rates
ERROR_RATE = 0.3  # 30% of requests fail

# Add new endpoints
@app.route('/api/custom-error')
def custom_error():
    app.logger.error("Custom error occurred")
    return jsonify({"error": "Custom error"}), 500
```

---

## 🔧 Advanced Usage

### Custom Error Patterns

Create custom traffic patterns for specific testing:

```python
# custom_traffic.py
import requests
import subprocess

def generate_pattern(url, pattern_type, count):
    """Generate specific error patterns"""
    token = subprocess.check_output(
        ['gcloud', 'auth', 'print-identity-token'],
        text=True
    ).strip()
    
    headers = {'Authorization': f'Bearer {token}'}
    
    if pattern_type == "cascading":
        # Simulate cascading failures
        requests.get(f"{url}/api/database", headers=headers)
        requests.get(f"{url}/api/network", headers=headers)
        requests.get(f"{url}/api/permission", headers=headers)
    
    elif pattern_type == "spike":
        # Simulate traffic spike
        for _ in range(count):
            requests.get(f"{url}/api/process", headers=headers)

# Usage
generate_pattern(SERVICE_URL, "cascading", 10)
```

### Integration Testing

```bash
# Test different scenarios
./run_test_suite.sh

# Contents of run_test_suite.sh:
# 1. Deploy service
# 2. Test each endpoint
# 3. Generate traffic
# 4. Run AIOps Agent
# 5. Validate results
# 6. Cleanup
```

---

## 🧹 Cleanup

### Delete the Service

```bash
# Delete Cloud Run service
gcloud run services delete aiops-demo-service \
  --region=us-central1 \
  --quiet

# Delete container image (optional)
gcloud container images delete \
  gcr.io/YOUR_PROJECT_ID/aiops-demo-service \
  --quiet

# Verify deletion
gcloud run services list
```

### Delete Logs (Optional)

```bash
# Delete all logs for the service
gcloud logging logs delete \
  projects/YOUR_PROJECT_ID/logs/run.googleapis.com%2Fstderr

gcloud logging logs delete \
  projects/YOUR_PROJECT_ID/logs/run.googleapis.com%2Frequests
```

---

## 💰 Cost Estimation

**Cloud Run Pricing** (us-central1):
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second
- Requests: $0.40 per million requests
- Free tier: 2 million requests/month

**Typical testing costs**:
- 1 hour of testing: **~$0.02**
- 100 investigations: **~$0.01**
- Full day of demos: **~$0.50**

**Keep costs minimal**: Delete service when not in use!

---

## 📞 Support

- **Main Project**: AIOps Agent [Repository](https://github.com/arjun-palani-sada/aiops-agent.git)

