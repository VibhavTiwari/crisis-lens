from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from config import settings

# Initialize tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configure Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name=getattr(settings, 'JAEGER_HOST', 'localhost'),
    agent_port=getattr(settings, 'JAEGER_PORT', 6831),
)

# Add span processor
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

def instrument_app(app):
    """Instrument FastAPI app with tracing"""
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
    
    return app

def trace_function(name: str = None):
    """Decorator to trace a function"""
    def decorator(func):
        func_name = name or func.__name__
        
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(func_name):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(func_name):
                return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
