"""
Server-Sent Events (SSE) implementation for CrisisLens.

Provides SSE endpoints as an alternative to WebSockets for simpler clients.
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Optional
import asyncio
import json
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

router = APIRouter()


class SSEManager:
    """Manages SSE connections and event streaming."""
    
    def __init__(self):
        # Event queues for each connection
        self.queues: dict[str, asyncio.Queue] = {}
        
        # Queues by user
        self.user_queues: dict[str, set[str]] = defaultdict(set)
        
    def create_queue(self, connection_id: str, user_id: Optional[str] = None) -> asyncio.Queue:
        """Create a new event queue for a connection."""
        queue = asyncio.Queue(maxsize=100)
        self.queues[connection_id] = queue
        
        if user_id:
            self.user_queues[user_id].add(connection_id)
        
        logger.info(f"SSE queue created: {connection_id}")
        return queue
    
    def remove_queue(self, connection_id: str, user_id: Optional[str] = None):
        """Remove an event queue."""
        if connection_id in self.queues:
            del self.queues[connection_id]
        
        if user_id and user_id in self.user_queues:
            self.user_queues[user_id].discard(connection_id)
            if not self.user_queues[user_id]:
                del self.user_queues[user_id]
        
        logger.info(f"SSE queue removed: {connection_id}")
    
    async def broadcast(self, event: dict):
        """Broadcast event to all connections."""
        event['_timestamp'] = datetime.utcnow().isoformat()
        
        for connection_id, queue in self.queues.items():
            try:
                await queue.put(event)
            except asyncio.QueueFull:
                logger.warning(f"Queue full for connection: {connection_id}")
    
    async def send_to_user(self, event: dict, user_id: str):
        """Send event to all connections for a user."""
        if user_id not in self.user_queues:
            return
        
        event['_timestamp'] = datetime.utcnow().isoformat()
        
        for connection_id in self.user_queues[user_id]:
            if connection_id in self.queues:
                try:
                    await self.queues[connection_id].put(event)
                except asyncio.QueueFull:
                    logger.warning(f"Queue full for connection: {connection_id}")


# Global SSE manager
sse_manager = SSEManager()


def format_sse(event: dict) -> str:
    """
    Format event data for SSE protocol.
    
    Args:
        event: Event data dictionary
        
    Returns:
        Formatted SSE string
    """
    event_type = event.get('type', 'message')
    data = json.dumps(event)
    
    return f"event: {event_type}\ndata: {data}\n\n"


async def event_stream(
    connection_id: str,
    user_id: Optional[str] = None,
    heartbeat_interval: int = 30
) -> AsyncGenerator[str, None]:
    """
    Generate SSE event stream.
    
    Args:
        connection_id: Unique connection identifier
        user_id: Optional user identifier
        heartbeat_interval: Seconds between heartbeat messages
        
    Yields:
        Formatted SSE messages
    """
    queue = sse_manager.create_queue(connection_id, user_id)
    
    try:
        # Send initial connection message
        yield format_sse({
            'type': 'connection',
            'status': 'connected',
            'connection_id': connection_id
        })
        
        last_heartbeat = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Wait for event with timeout for heartbeat
                event = await asyncio.wait_for(
                    queue.get(),
                    timeout=heartbeat_interval
                )
                
                yield format_sse(event)
                
            except asyncio.TimeoutError:
                # Send heartbeat
                current_time = asyncio.get_event_loop().time()
                if current_time - last_heartbeat >= heartbeat_interval:
                    yield format_sse({
                        'type': 'heartbeat',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    last_heartbeat = current_time
    
    except asyncio.CancelledError:
        logger.info(f"SSE stream cancelled: {connection_id}")
    
    finally:
        sse_manager.remove_queue(connection_id, user_id)


@router.get("/sse/stream")
async def sse_endpoint(
    request: Request,
    token: Optional[str] = None
):
    """
    SSE endpoint for real-time events.
    
    Query Parameters:
        token: Authentication token
    """
    user_id = None
    
    # Authenticate
    if token:
        from services.auth_service import verify_token
        try:
            user_id = await verify_token(token)
        except:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    # Generate unique connection ID
    connection_id = f"sse_{datetime.utcnow().timestamp()}_{id(request)}"
    
    return StreamingResponse(
        event_stream(connection_id, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.get("/sse/items")
async def sse_items_endpoint(request: Request, token: Optional[str] = None):
    """
    SSE endpoint for item updates only.
    
    Query Parameters:
        token: Authentication token
    """
    user_id = None
    
    # Authenticate
    if token:
        from services.auth_service import verify_token
        try:
            user_id = await verify_token(token)
        except:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    connection_id = f"sse_items_{datetime.utcnow().timestamp()}_{id(request)}"
    
    async def filtered_stream():
        """Stream only item-related events."""
        queue = sse_manager.create_queue(connection_id, user_id)
        
        try:
            yield format_sse({
                'type': 'connection',
                'status': 'connected',
                'stream': 'items'
            })
            
            while True:
                event = await queue.get()
                
                # Only send item-related events
                if event.get('type') in ['new_item', 'item_update', 'item_delete']:
                    yield format_sse(event)
        
        finally:
            sse_manager.remove_queue(connection_id, user_id)
    
    return StreamingResponse(
        filtered_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/sse/alerts")
async def sse_alerts_endpoint(request: Request, token: Optional[str] = None):
    """
    SSE endpoint for alerts only.
    
    Query Parameters:
        token: Authentication token
    """
    user_id = None
    
    # Authenticate
    if token:
        from services.auth_service import verify_token
        try:
            user_id = await verify_token(token)
        except:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    connection_id = f"sse_alerts_{datetime.utcnow().timestamp()}_{id(request)}"
    
    async def filtered_stream():
        """Stream only alert events."""
        queue = sse_manager.create_queue(connection_id, user_id)
        
        try:
            yield format_sse({
                'type': 'connection',
                'status': 'connected',
                'stream': 'alerts'
            })
            
            while True:
                event = await queue.get()
                
                # Only send alert events
                if event.get('type') == 'alert':
                    yield format_sse(event)
        
        finally:
            sse_manager.remove_queue(connection_id, user_id)
    
    return StreamingResponse(
        filtered_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


# Broadcasting functions
async def broadcast_event(event: dict):
    """Broadcast event to all SSE connections."""
    await sse_manager.broadcast(event)


async def send_user_event(event: dict, user_id: str):
    """Send event to specific user's SSE connections."""
    await sse_manager.send_to_user(event, user_id)
