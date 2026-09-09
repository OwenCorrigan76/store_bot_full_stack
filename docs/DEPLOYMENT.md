# Deployment Guide

This document covers deploying the Guitar Store Chatbot to production.

## Option 1: Docker (Recommended)

### Create Dockerfile for Backend

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Create Docker Compose (Full Stack)

```yaml
# docker-compose.yml
version: "3.8"

services:
  vllm:
    image: vllm/vllm-openai:latest
    ports:
      - "8000:8000"
    environment:
      - MODEL_NAME=meta-llama/Llama-2-7b-hf
      - GPU_MEMORY_UTILIZATION=0.9
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface

  backend:
    build: ./backend
    ports:
      - "8001:8001"
    depends_on:
      - vllm
    environment:
      - VLLM_BASE_URL=http://vllm:8000
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

networks:
  default:
    name: guitar-store-net
```

### Build and Run

```bash
# Build all containers
docker-compose build

# Start the stack
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Option 2: Cloud Deployment

### AWS (EC2 + G4 GPU Instance)

```bash
# 1. Launch EC2 instance (g4dn.xlarge or larger)
# 2. Install Docker & NVIDIA Container Runtime
# 3. Clone repository
# 4. Run docker-compose up

# Set up domain & SSL with Route53 + CloudFront
```

### Google Cloud (Compute Engine)

```bash
# Create GPU instance
gcloud compute instances create guitar-chatbot \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --machine-type=g4-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --zone=us-central1-a

# SSH into instance and run docker-compose
```

### Modal (Serverless GPU)

```python
# deploy.py
import modal

app = modal.App("guitar-chatbot")

image = (
    modal.Image.debian_slim()
    .pip_install_from_requirements("backend/requirements.txt")
    .pip_install("vllm")
)

@app.function(image=image, gpu="A10")
def run_vllm():
    import subprocess
    subprocess.run([
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", "meta-llama/Llama-2-7b-hf",
        "--port", "8000"
    ])

@app.function(image=image)
def run_backend():
    import subprocess
    subprocess.run([
        "uvicorn", "main:app",
        "--host", "0.0.0.0", "--port", "8001"
    ])
```

### Hugging Face Spaces

```bash
# 1. Create a Space at huggingface.co/spaces
# 2. Select "Docker" as runtime
# 3. Push repository to HF
# 4. Space automatically deploys with GPU
```

## Option 3: Kubernetes (Enterprise)

### Create Kubernetes Manifests

```yaml
# k8s/vllm-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm
  template:
    metadata:
      labels:
        app: vllm
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1
        env:
        - name: MODEL_NAME
          value: "meta-llama/Llama-2-7b-hf"

---
apiVersion: v1
kind: Service
metadata:
  name: vllm-service
spec:
  selector:
    app: vllm
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: guitar-store/backend:latest
        ports:
        - containerPort: 8001
        env:
        - name: VLLM_BASE_URL
          value: "http://vllm-service:8000"
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
  - port: 8001
    targetPort: 8001
  type: LoadBalancer
```

### Deploy

```bash
# Apply manifests
kubectl apply -f k8s/

# Monitor deployments
kubectl get deployments
kubectl logs -f deployment/backend-server
```

## Performance Tuning

### vLLM Optimization

```bash
# Use smaller context window for faster inference
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-hf \
  --gpu-memory-utilization 0.9 \
  --max-model-len 2048 \
  --enable-prefix-caching \
  --max-num-batched-tokens 4096

# Enable quantization for smaller memory footprint
# --dtype float16  (half precision)
# --dtype bfloat16 (brain float)
```

### Backend Load Balancing

```python
# Use multiple backend replicas
# Put behind load balancer (nginx, haproxy, cloud LB)

# Implement caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query: str):
    return ProductService.search(query)
```

## Monitoring in Production

### Prometheus Metrics

```python
# Add to backend/main.py
from prometheus_client import Counter, Histogram

# Track requests
request_count = Counter(
    'chat_requests_total',
    'Total chat requests'
)

# Track latency
request_latency = Histogram(
    'chat_request_duration_seconds',
    'Chat request latency'
)

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    request_count.inc()
    start = time.time()
    response = await call_next(request)
    request_latency.observe(time.time() - start)
    return response
```

### Logging

```python
# Use ELK Stack or similar
import logging
from pythonjsonlogger import jsonlogger

# All logs as JSON for easy parsing
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
```

### Error Tracking

```python
# Use Sentry for error monitoring
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/...",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1
)
```

## Security Checklist

- [ ] **Enable HTTPS/TLS** - All traffic encrypted
- [ ] **API Authentication** - Use API keys or JWT
- [ ] **Rate Limiting** - Prevent abuse (100 req/min per user)
- [ ] **Input Validation** - Sanitize all user inputs
- [ ] **CORS Configuration** - Only allow your frontend domain
- [ ] **Environment Variables** - Store secrets safely
- [ ] **Dependency Scanning** - Regular security updates
- [ ] **Logging & Monitoring** - Track all requests
- [ ] **Backups** - Regular database backups
- [ ] **DDoS Protection** - Use CloudFlare or similar

## Scaling Strategy

### Phase 1: Development
- Single machine with GPU
- All services in docker-compose
- Local SQLite or in-memory database

### Phase 2: MVP Production
- 1x GPU instance (vLLM)
- 2-3x backend replicas (behind load balancer)
- PostgreSQL database
- CloudFront for frontend CDN
- Basic monitoring (CloudWatch/Datadog)

### Phase 3: Scale
- Multiple vLLM instances (model serving with replicas)
- Auto-scaling backend (Kubernetes or Fargate)
- Read replicas for database
- Advanced caching (Redis)
- Full observability stack (Prometheus, Grafana, ELK)

### Phase 4: Global
- Multi-region deployment
- Edge caching (CloudFlare Workers)
- Regional vLLM servers
- Cross-region database replication
- A/B testing infrastructure

## Cost Estimation (Monthly)

### AWS

| Component | Instance | Cost |
|-----------|----------|------|
| GPU (vLLM) | g4dn.xlarge | $600 |
| Backend | t3.large x 3 | $150 |
| Database | RDS t3.small | $50 |
| Storage | S3 (100GB) | $25 |
| Data Transfer | ~1TB/month | $100 |
| **Total** | | **~$925** |

### Google Cloud

| Component | SKU | Cost |
|-----------|-----|------|
| GPU | 1x T4 | $350 |
| Compute | n1-standard-2 x 3 | $200 |
| CloudSQL | PostgreSQL | $40 |
| Storage | Persistent Disks | $25 |
| Networking | | $50 |
| **Total** | | **~$665** |

### Modal (Serverless)

| Component | Pricing | Cost |
|-----------|---------|------|
| GPU Hours | $0.35/hour | $250 |
| Network | $0.05/GB | $50 |
| Storage | $0.01/GB/month | $10 |
| **Total** | | **~$310** |

## Backup & Disaster Recovery

```bash
# Regular database backups
0 2 * * * pg_dump guitar_db | gzip > backups/guitar_db_$(date +%Y%m%d).sql.gz

# Store backups in S3
aws s3 sync ./backups s3://guitar-bot-backups/

# Test restoration monthly
pg_restore -d test_db backups/guitar_db_*.sql.gz
```

## Rollback Strategy

```bash
# Keep previous Docker image tags
docker build -t guitar-backend:v1.0.0 .
docker build -t guitar-backend:v1.0.1 .

# Quick rollback if needed
docker-compose stop backend
docker-compose run -d --name backend guitar-backend:v1.0.0

# Use Blue-Green deployment
# Run new version in parallel, switch traffic when ready
```
