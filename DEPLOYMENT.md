# Production Deployment Guide

## Quick Start

### Prerequisites
- Docker installed
- kubectl configured
- AWS CLI configured
- Terraform installed

### Local Production Test
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check health
curl http://localhost:8000/health

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Kubernetes Deployment

**1. Setup infrastructure with Terraform:**
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**2. Configure kubectl:**
```bash
aws eks update-kubeconfig --name crisis-lens-cluster --region us-east-1
```

**3. Deploy to Kubernetes:**
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl get services
```

**4. Access services:**
```bash
# API
kubectl port-forward svc/crisis-lens-api 8000:80

# Prometheus
 kubectl port-forward svc/prometheus 9090:9090

# Grafana
kubectl port-forward svc/grafana 3000:3000
```

## Monitoring

### Prometheus
- URL: http://localhost:9090
- Metrics: API requests, CPU, memory, Kafka lag
- Alerts: Configured in `monitoring/alerts.yml`

### Grafana
- URL: http://localhost:3000
- Default credentials: admin/admin
- Dashboards: Overview, API metrics, Infrastructure

### Alerts
Critical alerts configured for:
- API downtime
- High error rate (>5%)
- High latency (>1s)
- High CPU/memory usage
- Kafka consumer lag
- Pod restarts

## CI/CD

### GitHub Actions
Automated deployment on push to `main`:
1. Build Docker images
2. Push to GitHub Container Registry
3. Deploy to Kubernetes
4. Run smoke tests
5. Rollback on failure

### Manual Deployment
```bash
# Build and push
docker build -t ghcr.io/org/crisis-lens-api:v1.0.0 -f docker/Dockerfile.api .
docker push ghcr.io/org/crisis-lens-api:v1.0.0

# Update Kubernetes
kubectl set image deployment/crisis-lens-api \
  api=ghcr.io/org/crisis-lens-api:v1.0.0
  
kubectl rollout status deployment/crisis-lens-api
```

## Scaling

### Horizontal Scaling
```bash
# Manual scaling
kubectl scale deployment crisis-lens-api --replicas=5

# Auto-scaling (HPA configured)
kubectl get hpa
```

### Vertical Scaling
Update resources in `k8s/api-deployment.yaml` and apply.

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod crisis-lens-api-xxx
kubectl logs crisis-lens-api-xxx
```

### High memory usage
```bash
kubectl top pods
kubectl top nodes
```

### Database connection issues
```bash
kubectl exec -it crisis-lens-api-xxx -- env | grep DATABASE
```

## Security

- Secrets stored in Kubernetes Secrets
- HTTPS enforced via Ingress
- Network policies for pod isolation
- RBAC configured
- Images scanned in CI/CD

## Backup & Recovery

```bash
# Database backup
kubectl exec -it postgres-0 -- pg_dump -U postgres crisis_lens > backup.sql

# Restore
kubectl exec -i postgres-0 -- psql -U postgres crisis_lens < backup.sql
```

## Cost Optimization

- Use Spot instances for workers
- Enable cluster autoscaling
- Right-size resources
- Use caching (Redis)
- Enable compression
