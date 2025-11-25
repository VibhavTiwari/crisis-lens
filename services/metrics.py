from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

crisislen_items_processed_total = Counter(
    'crisislen_items_processed_total',
    'Total items processed'
)

crisislen_workflows_active = Gauge(
    'crisislen_workflows_active',
    'Number of active workflows'
)

crisislen_risk_score = Histogram(
    'crisislen_risk_score',
    'Risk scores of processed items',
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
)

def get_metrics():
    """Return Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

class MetricsMiddleware:
    """Middleware to track request metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        method = scope["method"]
        path = scope["path"]
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message["status"]
                duration = time.time() - start_time
                
                # Record metrics
                http_requests_total.labels(
                    method=method,
                    endpoint=path,
                    status=str(status)
                ).inc()
                
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
