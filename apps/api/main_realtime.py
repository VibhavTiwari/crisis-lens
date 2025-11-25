"""
Main application entry point with WebSocket and SSE routes.

Integrates all Phase 21 real-time features.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routers
from apps.api.websocket import router as websocket_router
from apps.api.sse import router as sse_router
from apps.api.collaboration import router as collaboration_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CrisisLens API",
    description="Real-time crisis intelligence platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sse_router, prefix="/api", tags=["SSE"])
app.include_router(collaboration_router, prefix="/api", tags=["Collaboration"])

# Note: WebSocket routes are registered directly, not through routers
from apps.api.websocket import websocket_endpoint, item_websocket_endpoint
app.add_api_websocket_route("/ws", websocket_endpoint)
app.add_api_websocket_route("/ws/items/{item_id}", item_websocket_endpoint)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "CrisisLens API",
        "version": "1.0.0",
        "features": [
            "WebSocket real-time updates",
            "Server-Sent Events (SSE)",
            "Kafka event streaming",
            "Multi-channel notifications",
            "Real-time collaboration"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    # Start Kafka consumers in background
    import asyncio
    from services.kafka_consumer import (
        create_main_consumer,
        create_notifications_consumer,
        create_activity_consumer
    )
    
    async def start_consumers():
        """Start all Kafka consumers."""
        logger.info("Starting Kafka consumers...")
        
        # Create consumers
        main_consumer = create_main_consumer()
        notifications_consumer = create_notifications_consumer()
        activity_consumer = create_activity_consumer()
        
        # Start consumers
        await asyncio.gather(
            main_consumer.start(),
            notifications_consumer.start(),
            activity_consumer.start()
        )
    
    # Note: In production, run consumers as separate services
    # For development, they can be started with the app
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
