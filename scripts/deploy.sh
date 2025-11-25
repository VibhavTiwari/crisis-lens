#!/bin/bash

# CrisisLens Deployment Script

set -e

echo "==================================="
echo "CrisisLens Production Deployment"
echo "==================================="

# Configuration
NAMESPACE="crisislen"
HELM_RELEASE="crisislen"
ENVIRONMENT=${1:-production}

echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"

# 1. Create namespace
echo ""
echo "1. Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# 2. Apply ConfigMaps and Secrets
echo ""
echo "2. Applying ConfigMaps and Secrets..."
kubectl apply -f infrastructure/k8s/configmaps/ -n $NAMESPACE

echo "⚠️  Remember to update secrets in infrastructure/k8s/configmaps/config.yaml"

# 3. Deploy infrastructure (databases)
echo ""
echo "3. Deploying infrastructure..."
helm upgrade --install postgresql bitnami/postgresql \
  --namespace $NAMESPACE \
  --set auth.database=crisislen \
  --set primary.persistence.size=20Gi

helm upgrade --install redis bitnami/redis \
  --namespace $NAMESPACE \
  --set master.persistence.enabled=true \
  --set master.persistence.size=8Gi

# 4. Deploy application
echo ""
echo "4. Deploying CrisisLens application..."
kubectl apply -f infrastructure/k8s/deployments/ -n $NAMESPACE
kubectl apply -f infrastructure/k8s/ingress.yaml -n $NAMESPACE
kubectl apply -f infrastructure/k8s/hpa.yaml -n $NAMESPACE

# 5. Deploy monitoring
echo ""
echo "5. Deploying monitoring stack..."
kubectl apply -f infrastructure/monitoring/prometheus/servicemonitor.yaml -n $NAMESPACE

# 6. Wait for rollout
echo ""
echo "6. Waiting for deployment to be ready..."
kubectl rollout status deployment/crisislen-api -n $NAMESPACE --timeout=5m

# 7. Show status
echo ""
echo "7. Deployment status:"
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "  - Update DNS to point to the ingress IP"
echo "  - Verify TLS certificates are issued"
echo "  - Check monitoring dashboards"
echo "  - Run smoke tests"
