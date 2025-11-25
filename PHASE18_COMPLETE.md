# Phase 18: Production Infrastructure - Complete!

## Components Implemented

### 1. Kubernetes Manifests (`infrastructure/k8s/`)

**Deployments:**
- `api-deployment.yaml` - API service with 3 replicas
  - Health/readiness probes
  - Resource limits (CPU: 2000m, Memory: 4Gi)
  - Environment variables from ConfigMap/Secrets
  - Prometheus annotations

**Configuration:**
- `namespace.yaml` - Dedicated namespace
- `configmaps/config.yaml` - Application configuration + secrets
- Resource requests/limits for optimal scheduling

**Networking:**
- `ingress.yaml` - NGINX ingress with TLS
  - Let's Encrypt certificate automation
  - Rate limiting (100 req/s)
  - SSL redirect
  - 50MB body size limit

**Auto-scaling:**
- `hpa.yaml` - Horizontal Pod Autoscaler
  - Min: 3, Max: 20 replicas
  - Target: 70% CPU, 80% memory
  - Smart scale-up/down policies
  - 5-minute stabilization window

### 2. Helm Chart (`infrastructure/helm/crisislen/`)

**Chart Structure:**
- `Chart.yaml` - Metadata (v0.1.0)
- `values.yaml` - Default configuration
- `templates/deployment.yaml` - Deployment template
- `templates/_helpers.tpl` - Helper functions

**Features:**
- Parameterized deployments
- Environment-specific values
- Checksum-based config reload
- Built-in database charts

**Usage:**
```bash
helm install crisislen ./infrastructure/helm/crisislen \
  --namespace crisislen \
  --values values-production.yaml
```

### 3. Prometheus Monitoring (`infrastructure/monitoring/prometheus/`)

**ServiceMonitor:**
- Auto-discovery of API pods
- 30-second scrape interval
- `/metrics` endpoint

**Alert Rules:**
- **HighErrorRate** - >5% 5xx errors for 5min → critical
- **HighCPUUsage** - >80% CPU for 10min → warning
- **HighMemoryUsage** - >90% memory for 5min → warning  
- **APIDown** - Service down for 1min → critical

### 4. Grafana Dashboards (`infrastructure/monitoring/grafana/`)

**System Overview Dashboard:**
- Request rate (by method/status)
- Response time (p95)
- CPU usage per pod
- Memory usage per pod
- Active workflows (gauge)
- Items processed (24h counter)
- Average risk score
- High-risk items count

**Refresh:** 30 seconds

### 5. Metrics Exporter (`services/metrics.py`)

**Prometheus Metrics:**
- `http_requests_total` - Counter (method, endpoint, status)
- `http_request_duration_seconds` - Histogram (method, endpoint)
- `crisislen_items_processed_total` - Counter
- `crisislen_workflows_active` - Gauge
- `crisislen_risk_score` - Histogram (buckets: 0.1-1.0)

**Middleware:**
- Automatic request tracking
- Response time recording
- Status code labels

### 6. Distributed Tracing (`services/tracing.py`)

**OpenTelemetry + Jaeger:**
- FastAPI auto-instrumentation
- Requests library instrumentation
- BatchSpanProcessor for efficiency
- `@trace_function` decorator

**Integration:**
```python
from services.tracing import instrument_app, trace_function

app = instrument_app(app)

@trace_function("process_claim")
async def process_claim(claim):
    ...
```

### 7. Deployment Script (`scripts/deploy.sh`)

**Automated Deployment:**
1. Create namespace
2. Apply ConfigMaps/Secrets
3. Deploy databases (PostgreSQL, Redis via Helm)
4. Deploy application
5. Configure ingress
6. Enable auto-scaling
7. Deploy monitoring
8. Wait for rollout
9. Show status

**Usage:**
```bash
bash scripts/deploy.sh production
```

## Architecture

```
┌─────────────────┐
│   Ingress       │
│  (NGINX + TLS)  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Service  │
    └────┬─────┘
         │
    ┌────▼──────────┐
    │  API Pods     │
    │  (3-20)       │
    │  + HPA        │
    └───┬───────────┘
        │
   ┌────▼──────┬─────────┬──────────┐
   │           │         │          │
   ▼           ▼         ▼          ▼
PostgreSQL  Redis  OpenSearch  Qdrant


Monitoring Stack:
┌──────────┐    ┌───────────┐    ┌─────────┐
│Prometheus│───▶│  Grafana  │    │ Jaeger  │
└────┬─────┘    └───────────┘    └────┬────┘
     │                                 │
     └─────────────┬───────────────────┘
                   │
              ┌────▼────┐
              │   API   │
              └─────────┘
```

## Deployment Guide

### Prerequisites

1. **Kubernetes cluster** (1.24+)
2. **kubectl** configured
3. **Helm 3** installed
4. **cert-manager** for TLS
5. **NGINX Ingress Controller**
6. **Prometheus Operator** (optional)

### Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/crisis-lens
cd crisis-lens

# 2. Update secrets
vim infrastructure/k8s/configmaps/config.yaml
# Change all dummy values!

# 3. Deploy
bash scripts/deploy.sh production

# 4. Verify deployment
kubectl get pods -n crisislen
kubectl get ingress -n crisislen

# 5. Access application
# Update DNS: api.crisislen.example.com → <INGRESS_IP>

# 6. Check monitoring
kubectl port-forward -n monitoring svc/grafana 3000:80
# Open http://localhost:3000
```

### Environment Variables

Update in `configmaps/config.yaml`:

```yaml
apiVersion: v1
kind: Secret
stringData:
  database-url: "postgresql://user:pass@host:5432/db"
  secret-key: "<generate with: openssl rand -hex 32>"
  openai-api-key: "sk-..."
  google-client-id: "..."
  google-client-secret: "..."
```

## Monitoring Access

**Grafana:**
```bash
kubectl port-forward -n monitoring svc/grafana 3000:80
```
Default: admin/admin

**Prometheus:**
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

**Jaeger:**
```bash
kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
```

## Scaling

**Manual:**
```bash
kubectl scale deployment crisislen-api -n crisislen --replicas=10
```

**Auto-scaling:** Already enabled via HPA
- Scales 3-20 based on CPU/memory
- Metrics collected every 30s

## Next Steps (Phase 19)

Implement advanced NLP & analytics:
- Coreference resolution
- Temporal reasoning
- Geospatial analysis
- Social network analysis
- Sentiment analysis
