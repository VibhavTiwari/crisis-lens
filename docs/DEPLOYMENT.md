# CrisisLens Deployment Guide

## Production Deployment Checklist

- [ ] Kubernetes cluster setup (v1.24+)
- [ ] kubectl configured
- [ ] Helm 3 installed
- [ ] Domain name configured
- [ ] TLS certificates (Let's Encrypt)
- [ ] Database backups configured
- [ ] Monitoring stack deployed
- [ ] API keys obtained
- [ ] Security scan completed
- [ ] Load testing passed

##Infrastructure Requirements

### Kubernetes Cluster

**Minimum Specifications:**
- **Nodes**: 3+ worker nodes
- **CPU**: 8 cores per node
- **Memory**: 32 GB per node
- **Storage**: 500 GB SSD
- **Network**: 1 Gbps

**Recommended for Production:**
- **Nodes**: 5+ worker nodes
- **CPU**: 16 cores per node
- **Memory**: 64 GB per node
- **Storage**: 1 TB NVMe SSD
- **Network**: 10 Gbps

### Databases

| Database | Purpose | Min Size | Recommended |
|----------|---------|----------|-------------|
| PostgreSQL | Relational data | 20 GB | 100 GB SSD |
| OpenSearch | Full-text search | 50 GB | 200 GB SSD |
| Qdrant | Vector storage | 25 GB | 100 GB SSD |
| Neo4j | Graph data | 20 GB | 50 GB SSD |
| ClickHouse | Analytics | 30 GB | 150 GB SSD |
| Redis | Cache/sessions | 8 GB RAM | 16 GB RAM |

## Pre-Deployment Setup

### 1. Configure Environment Variables

Create `.env` file:

```bash
# Application
APP_NAME=CrisisLens
ENV=production
SECRET_KEY=$(openssl rand -hex 32)

# Databases
DATABASE_URL=postgresql://user:pass@postgres:5432/crisislen
REDIS_HOST=redis-service
OPENSEARCH_HOST=opensearch-service
QDRANT_HOST=qdrant-service
NEO4J_URI=bolt://neo4j-service:7687
CLICKHOUSE_HOST=clickhouse-service

# ML/AI APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...

# Monitoring
JAEGER_HOST=jaeger-service
JAEGER_PORT=6831
```

### 2. Update Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace crisislen

# Create secrets
kubectl create secret generic crisislen-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=secret-key="$(openssl rand -hex 32)" \
  --from-literal=openai-api-key="sk-..." \
  -n crisislen
```

### 3. Configure Ingress

Update `infrastructure/k8s/ingress.yaml`:

```yaml
spec:
  tls:
  - hosts:
    - api.yourdomain.com  # ← Change this
    - app.yourdomain.com   # ← Change this
```

## Deployment Steps

### Option 1: One-Command Deployment

```bash
bash scripts/deploy.sh production
```

### Option 2: Manual Deployment

#### Step 1: Deploy Infrastructure

```bash
# Create namespace
kubectl apply -f infrastructure/k8s/namespace.yaml

# Deploy ConfigMaps and Secrets
kubectl apply -f infrastructure/k8s/configmaps/
```

#### Step 2: Deploy Databases

```bash
# PostgreSQL
helm upgrade --install postgresql bitnami/postgresql \
  --namespace crisislen \
  --set auth.database=crisislen \
  --set auth.username=postgres \
  --set primary.persistence.size=100Gi

# Redis
helm upgrade --install redis bitnami/redis \
  --namespace crisislen \
  --set master.persistence.size=16Gi

# OpenSearch
helm upgrade --install opensearch opensearch/opensearch \
  --namespace crisislen \
  --set replicas=3 \
  --set persistence.size=200Gi

# Qdrant
helm upgrade --install qdrant qdrant/qdrant \
  --namespace crisislen \
  --set persistence.size=100Gi
```

#### Step 3: Deploy Application

```bash
# Deploy API
kubectl apply -f infrastructure/k8s/deployments/api-deployment.yaml

# Deploy Ingress
kubectl apply -f infrastructure/k8s/ingress.yaml

# Deploy HPA
kubectl apply -f infrastructure/k8s/hpa.yaml
```

#### Step 4: Deploy Monitoring

```bash
# Prometheus
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Apply ServiceMonitor
kubectl apply -f infrastructure/monitoring/prometheus/servicemonitor.yaml

# Import Grafana dashboards
kubectl create configmap grafana-dashboards \
  --from-file=infrastructure/monitoring/grafana/dashboards/ \
  -n monitoring
```

#### Step 5: Initialize Databases

```bash
# Port-forward to PostgreSQL
kubectl port-forward svc/postgresql 5432:5432 -n crisislen &

# Run initialization
python scripts/init_databases.py
python scripts/init_roles.py

# Kill port-forward
killall kubectl
```

### Option 3: Helm Chart Deployment

```bash
helm install crisislen ./infrastructure/helm/crisislen \
  --namespace crisislen \
  --create-namespace \
  --values values-production.yaml
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Check pods
kubectl get pods -n crisislen

# Check services
kubectl get svc -n crisislen

# Check ingress
kubectl get ingress -n crisislen

# View logs
kubectl logs -f deployment/crisislen-api -n crisislen
```

### 2. Configure DNS

Point your domain to the ingress IP:

```bash
# Get ingress IP
kubectl get ingress crisislen-ingress -n crisislen -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Add DNS records:
# api.yourdomain.com  → <INGRESS_IP>
# app.yourdomain.com  → <INGRESS_IP>
```

### 3. Verify TLS

```bash
# Check certificate
kubectl get certificate -n crisislen

# Wait for cert-manager to issue certificate
kubectl describe certificate crisislen-tls -n crisislen
```

### 4. Smoke Tests

```bash
# Health check
curl https://api.yourdomain.com/health

# Authentication
curl -X POST https://api.yourdomain.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"..."}'

# Start workflow
curl -X POST https://api.yourdomain.com/workflows/start \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"raw_item":{...}}'
```

## Scaling

### Horizontal Scaling

HPA is configured to scale 3-20 pods:

```bash
# Check HPA status
kubectl get hpa -n crisislen

# Manual scaling
kubectl scale deployment crisislen-api --replicas=10 -n crisislen
```

### Vertical Scaling

Update resource limits:

```yaml
# infrastructure/k8s/deployments/api-deployment.yaml
resources:
  limits:
    cpu: 4000m      # ← Increase
    memory: 8Gi     # ← Increase
```

### Database Scaling

```bash
# Scale PostgreSQL replicas
helm upgrade postgresql bitnami/postgresql \
  --set replication.enabled=true \
  --set replication.readReplicas=2

# Scale OpenSearch cluster
helm upgrade opensearch opensearch/opensearch \
  --set replicas=5
```

## Monitoring

### Access Grafana

```bash
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
```

Default credentials: admin/prom-operator

### Access Prometheus

```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring
```

### Access Jaeger

```bash
kubectl port-forward svc/jaeger-query 16686:16686 -n monitoring
```

### Alerts

Alert emails configured in Prometheus AlertManager:

```bash
kubectl edit alertmanagerconfig -n monitoring
```

## Backup & Recovery

### Database Backups

```bash
# PostgreSQL backup
kubectl exec -it postgresql-0 -n crisislen -- \
  pg_dump -U postgres crisislen > backup_$(date +%Y%m%d).sql

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d).sql s3://your-bucket/backups/
```

### Automated Backups

Use Velero for cluster-wide backups:

```bash
# Install Velero
velero install \
  --provider aws \
  --bucket your-backup-bucket \
  --secret-file ./credentials-velero

# Create backup schedule
velero schedule create daily-backup \
  --schedule="0 2 * * *" \
  --include-namespaces crisislen
```

### Restore

```bash
# Restore from backup
velero restore create --from-backup daily-backup-20240115
```

## Troubleshooting

### Pods Not Starting

```bash
# Check events
kubectl describe pod <pod-name> -n crisislen

# Check logs
kubectl logs <pod-name> -n crisislen

# Common issues:
# - ImagePullBackOff: Check image registry
# - CrashLoopBackOff: Check application logs
# - Pending: Check resource availability
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql -h postgresql -U postgres -d crisislen

# Test Redis
kubectl run -it --rm debug --image=redis:7 --restart=Never -- \
  redis-cli -h redis-service ping
```

### High Memory Usage

```bash
# Check memory usage
kubectl top pods -n crisislen

# Increase limits if needed
kubectl set resources deployment crisislen-api \
  --limits=memory=8Gi \
  -n crisislen
```

### Slow Response Times

1. Check HPA scaling
2. Review Prometheus metrics
3. Enable caching (Redis)
4. Optimize database queries
5. Add read replicas

## Security Hardening

### 1. Network Policies

```bash
kubectl apply -f infrastructure/k8s/network-policies/
```

### 2. Pod Security Policies

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  runAsUser:
    rule: MustRunAsNonRoot
```

### 3. Secrets Management

Use external secrets (e.g., Vault):

```bash
helm install vault hashicorp/vault --namespace vault
```

### 4. RBAC

```bash
# Create service account
kubectl create serviceaccount crisislen-sa -n crisislen

# Bind role
kubectl create rolebinding crisislen-binding \
  --serviceaccount=crisislen:crisislen-sa \
  --role=crisislen-role \
  -n crisislen
```

## Performance Optimization

### 1. Enable Caching

Redis caching for frequent queries:

```python
# In config
CACHE_TTL = 300  # 5 minutes
CACHE_ENABLED = True
```

### 2. Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_items_risk ON items(risk_score);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_claims_veracity ON claims(veracity_likelihood);
```

### 3. Connection Pooling

```python
# SQLAlchemy connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40
)
```

### 4. CDN for Assets

Use CloudFlare or AWS CloudFront for static assets.

## Maintenance

### Rolling Updates

```bash
# Update image
kubectl set image deployment/crisislen-api \
  api=crisislen/api:v1.1.0 \
  -n crisislen

# Monitor rollout
kubectl rollout status deployment/crisislen-api -n crisislen

# Rollback if needed
kubectl rollout undo deployment/crisislen-api -n crisislen
```

### Draining Nodes

```bash
# Drain node for maintenance
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# Bring back online
kubectl uncordon <node-name>
```

## Support

- **Documentation**: https://docs.crisislen.example.com
- **Slack**: #crisislen-ops
- **On-call**: +91-XX-XXXX-XXXX
