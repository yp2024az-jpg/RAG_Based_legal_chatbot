# Deployment Guide

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Google Cloud Run](#google-cloud-run)
3. [AWS](#aws)
4. [Heroku](#heroku)
5. [Kubernetes](#kubernetes)
6. [Production Checklist](#production-checklist)

## Docker Deployment

### Local Docker

```bash
# Build image
docker build -t legal-advisor:latest .

# Run container
docker run -p 8501:8501 -p 5000:5000 \
  -e GOOGLE_API_KEY=your_key \
  legal-advisor:latest
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f api
docker-compose logs -f streamlit

# Rebuild specific service
docker-compose up -d --build api
```

## Google Cloud Run

### Prerequisites
- Google Cloud Account
- `gcloud` CLI installed
- Docker installed

### Deployment Steps

```bash
# 1. Authenticate
gcloud auth login

# 2. Set project
gcloud config set project YOUR_PROJECT_ID

# 3. Create artifact registry
gcloud artifacts repositories create legal-advisor \
  --repository-format=docker \
  --location=us-central1

# 4. Configure Docker auth
gcloud auth configure-docker us-central1-docker.pkg.dev

# 5. Build and push image
docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT/legal-advisor/app:latest .
docker push us-central1-docker.pkg.dev/YOUR_PROJECT/legal-advisor/app:latest

# 6. Deploy to Cloud Run
gcloud run deploy legal-advisor \
  --image us-central1-docker.pkg.dev/YOUR_PROJECT/legal-advisor/app:latest \
  --platform managed \
  --region us-central1 \
  --port 8501 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --set-env-vars GOOGLE_API_KEY=your_key,LLM_MODEL=gemini-pro

# 7. View deployment
gcloud run services describe legal-advisor --region us-central1
```

### Environment Variables
```bash
gcloud run services update legal-advisor \
  --set-env-vars GOOGLE_API_KEY=your_key \
  --region us-central1
```

## AWS

### Using ECS

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name legal-advisor

# 2. Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# 3. Build and tag image
docker build -t legal-advisor:latest .
docker tag legal-advisor:latest \
  YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/legal-advisor:latest

# 4. Push to ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/legal-advisor:latest

# 5. Create ECS task definition (see ecs-task-definition.json)
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json

# 6. Create ECS service
aws ecs create-service \
  --cluster my-cluster \
  --service-name legal-advisor \
  --task-definition legal-advisor:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Using EC2

```bash
# 1. SSH into EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# 2. Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# 3. Clone repository
git clone https://github.com/yourusername/rag-legal-advisor.git
cd rag-legal-advisor

# 4. Create .env file
cp .env.example .env
# Edit .env with your configuration

# 5. Run with Docker Compose
docker-compose up -d

# 6. Check status
docker-compose ps
```

## Heroku

```bash
# 1. Install Heroku CLI
# Download from https://devcenter.heroku.com/articles/heroku-cli

# 2. Login
heroku login

# 3. Create app
heroku create legal-advisor

# 4. Add buildpacks
heroku buildpacks:add heroku/python

# 5. Set environment variables
heroku config:set GOOGLE_API_KEY=your_key
heroku config:set LLM_MODEL=gemini-pro

# 6. Deploy
git push heroku main

# 7. View logs
heroku logs --tail

# 8. Scale dynos (optional)
heroku ps:scale web=2
```

## Kubernetes

### Prerequisites
- kubectl installed
- Kubernetes cluster (GKE, EKS, AKS, or local)

### Deployment

```bash
# 1. Create namespace
kubectl create namespace legal-advisor

# 2. Create ConfigMap
kubectl create configmap legal-advisor-config \
  --from-file=config/config.yaml \
  -n legal-advisor

# 3. Create Secret
kubectl create secret generic legal-advisor-secret \
  --from-env-file=.env \
  -n legal-advisor

# 4. Create Docker registry secret
kubectl create secret docker-registry regcred \
  --docker-server=docker.io \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  -n legal-advisor

# 5. Apply deployment
kubectl apply -f k8s/deployment.yaml -n legal-advisor

# 6. Apply service
kubectl apply -f k8s/service.yaml -n legal-advisor

# 7. Check status
kubectl get pods -n legal-advisor
kubectl get svc -n legal-advisor

# 8. Port forward (local testing)
kubectl port-forward svc/legal-advisor 8501:8501 -n legal-advisor
```

### Kubernetes Manifest Example (k8s/deployment.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legal-advisor
  namespace: legal-advisor
spec:
  replicas: 2
  selector:
    matchLabels:
      app: legal-advisor
  template:
    metadata:
      labels:
        app: legal-advisor
    spec:
      containers:
      - name: legal-advisor
        image: your-registry/legal-advisor:latest
        ports:
        - containerPort: 8501
        - containerPort: 5000
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: legal-advisor-secret
              key: GOOGLE_API_KEY
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Production Checklist

Before deploying to production:

### Security
- [ ] All API keys removed from code (use environment variables)
- [ ] .env file added to .gitignore
- [ ] HTTPS/TLS enabled
- [ ] CORS properly configured
- [ ] Rate limiting implemented
- [ ] Input validation implemented

### Performance
- [ ] FAISS index pre-built and loaded
- [ ] Database connections pooled
- [ ] Caching strategy implemented
- [ ] Load balancing configured
- [ ] CDN setup for static assets

### Monitoring & Logging
- [ ] Centralized logging (ELK, Datadog, etc.)
- [ ] Application monitoring (APM) enabled
- [ ] Error tracking (Sentry, etc.)
- [ ] Performance metrics tracked
- [ ] Alerts configured

### Testing
- [ ] Unit tests (18/18 passing ✓)
- [ ] Integration tests passed
- [ ] Load testing completed
- [ ] Security testing done
- [ ] Accessibility tested

### Documentation
- [ ] API documentation complete
- [ ] Setup guide ready
- [ ] Runbook prepared
- [ ] Configuration documented
- [ ] Troubleshooting guide ready

### Infrastructure
- [ ] Database backups configured
- [ ] Recovery plan documented
- [ ] Autoscaling configured
- [ ] Health checks implemented
- [ ] Resource limits set

### Deployment
- [ ] CI/CD pipeline setup
- [ ] Automated deployments configured
- [ ] Rollback plan ready
- [ ] Blue-green deployment tested
- [ ] Canary deployment tested

## Health Check

```bash
# Check API health
curl -s http://your-app/api/v1/health | jq

# Expected response
{
  "status": "healthy",
  "service": "RAG-Based Legal Advisor Bot"
}
```

## Monitoring Commands

```bash
# Docker
docker stats
docker logs -f legal-advisor-api

# Kubernetes
kubectl top pods -n legal-advisor
kubectl logs -f deployment/legal-advisor -n legal-advisor

# Docker Compose
docker-compose logs -f
docker-compose stats
```

## Scaling

### Docker Compose
```yaml
services:
  api:
    deploy:
      replicas: 3
  streamlit:
    deploy:
      replicas: 2
```

### Kubernetes
```bash
kubectl scale deployment legal-advisor --replicas=5 -n legal-advisor
```

## Troubleshooting Deployments

### Container won't start
```bash
# Check logs
docker logs container_id

# Check image
docker inspect image_name

# Rebuild
docker build --no-cache -t legal-advisor .
```

### Connection timeout
```bash
# Check service status
docker-compose ps

# Check ports
netstat -an | grep LISTEN

# Verify firewall rules
```

### Memory issues
```bash
# Increase Docker memory limit
# Edit docker-compose.yml or ECS task definition

# Monitor memory
docker stats

# Optimize code
# - Reduce chunk size
# - Limit FAISS index size
```

---

For more help, check the [README.md](../README.md) or open an issue on GitHub.
