"""
WebSocket Server for real-time updates in CrisisLens.

Provides WebSocket connections for live updates to frontend clients.
"""
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Dict, Set, Optional, Any
import json
import logging
from datetime import datetime
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        # All active connections
        self.active_connections: Set[WebSocket] = set()
        
        # Connections by user ID
        self.user_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        
        # Connections by room/channel
        self.room_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        
        # WebSocket metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        user_id: Optional[str] = None,
        rooms: Optional[list[str]] = None
    ):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            user_id: Optional user identifier
            rooms: Optional list of rooms to join
        """
        await websocket.accept()
        
        # Add to active connections
        self.active_connections.add(websocket)
        
        # Store metadata
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'rooms': rooms or [],
            'connected_at': datetime.utcnow().isoformat()
        }
        
        # Add to user connections
        if user_id:
            self.user_connections[user_id].add(websocket)
        
        # Add to rooms
        if rooms:
            for room in rooms:
                self.room_connections[room].add(websocket)
        
        logger.info(
            f"WebSocket connected: user={user_id}, rooms={rooms}, "
            f"total_connections={len(self.active_connections)}"
        )
        
        # Send welcome message
        await self.send_personal_message(
            {
                'type': 'connection',
                'status': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            },
            websocket
        )
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
        """
        if websocket not in self.active_connections:
            return
        
        # Get metadata
        metadata = self.connection_metadata.get(websocket, {})
        user_id = metadata.get('user_id')
        rooms = metadata.get('rooms', [])
        
        # Remove from active connections
        self.active_connections.discard(websocket)
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from rooms
        for room in rooms:
            if room in self.room_connections:
                self.room_connections[room].discard(websocket)
                if not self.room_connections[room]:
                    del self.room_connections[room]
        
        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        logger.info(
            f"WebSocket disconnected: user={user_id}, "
            f"total_connections={len(self.active_connections)}"
        )
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            message: Message data
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Message data to broadcast
        """
        # Add timestamp
        message['_broadcast_at'] = datetime.utcnow().isoformat()
        
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
        
        logger.debug(f"Broadcast to {len(self.active_connections)} connections")
    
    async def broadcast_to_user(self, message: dict, user_id: str):
        """
        Send a message to all connections for a specific user.
        
        Args:
            message: Message data
            user_id: Target user ID
        """
        if user_id not in self.user_connections:
            logger.warning(f"No connections found for user: {user_id}")
            return
        
        connections = self.user_connections[user_id].copy()
        disconnected = set()
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
        
        logger.debug(f"Sent message to user {user_id}")
    
    async def broadcast_to_room(self, message: dict, room: str):
        """
        Broadcast a message to all connections in a room.
        
        Args:
            message: Message data
            room: Room/channel name
        """
        if room not in self.room_connections:
            logger.warning(f"No connections found in room: {room}")
            return
        
        connections = self.room_connections[room].copy()
        disconnected = set()
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to room {room}: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
        
        logger.debug(f"Broadcast to room {room}: {len(connections)} connections")
    
    async def join_room(self, websocket: WebSocket, room: str):
        """Add a connection to a room."""
        self.room_connections[room].add(websocket)
        
        # Update metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]['rooms'].append(room)
        
        logger.info(f"Connection joined room: {room}")
    
    async def leave_room(self, websocket: WebSocket, room: str):
        """Remove a connection from a room."""
        if room in self.room_connections:
            self.room_connections[room].discard(websocket)
            
            # Update metadata
            if websocket in self.connection_metadata:
                rooms = self.connection_metadata[websocket]['rooms']
                if room in rooms:
                    rooms.remove(room)
        
        logger.info(f"Connection left room: {room}")
    
    def get_active_users(self) -> list[str]:
        """Get list of active user IDs."""
        return list(self.user_connections.keys())
    
    def get_room_users(self, room: str) -> list[str]:
        """Get list of user IDs in a specific room."""
        if room not in self.room_connections:
            return []
        
        users = set()
        for conn in self.room_connections[room]:
            metadata = self.connection_metadata.get(conn, {})
            user_id = metadata.get('user_id')
            if user_id:
                users.add(user_id)
        
        return list(users)


# Global connection manager instance
manager = ConnectionManager()


# Authentication dependency
async def get_current_user_ws(websocket: WebSocket) -> Optional[str]:
    """
    Extract and validate user from WebSocket connection.
    
    Args:
        websocket: WebSocket connection
        
    Returns:
        User ID if authenticated, None otherwise
    """
    try:
        # Get token from query parameters
        token = websocket.query_params.get('token')
        
        if not token:
            return None
        
        # Validate token (simplified - use your auth service)
        from services.auth_service import verify_token
        
        user_id = await verify_token(token)
        return user_id
    
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        return None


# WebSocket endpoints
from fastapi import APIRouter

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    Main WebSocket endpoint for real-time updates.
    
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
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    
    # Connect
    await manager.connect(websocket, user_id=user_id, rooms=['global'])
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get('type')
            
            if message_type == 'ping':
                await manager.send_personal_message({'type': 'pong'}, websocket)
            
            elif message_type == 'join_room':
                room = data.get('room')
                if room:
                    await manager.join_room(websocket, room)
                    await manager.send_personal_message(
                        {'type': 'joined_room', 'room': room},
                        websocket
                    )
            
            elif message_type == 'leave_room':
                room = data.get('room')
                if room:
                    await manager.leave_room(websocket, room)
                    await manager.send_personal_message(
                        {'type': 'left_room', 'room': room},
                        websocket
                    )
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/items/{item_id}")
async def item_websocket_endpoint(
    websocket: WebSocket,
    item_id: str,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for a specific item.
    
    Path Parameters:
        item_id: Item identifier
    
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
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    
    # Connect to item-specific room
    room = f"item:{item_id}"
    await manager.connect(websocket, user_id=user_id, rooms=[room])
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Handle item-specific messages
            message_type = data.get('type')
            
            if message_type == 'ping':
                await manager.send_personal_message({'type': 'pong'}, websocket)
            
            elif message_type == 'cursor_move':
                # Broadcast cursor position to other users in room
                await manager.broadcast_to_room(
                    {
                        'type': 'cursor_update',
                        'user_id': user_id,
                        'position': data.get('position')
                    },
                    room
                )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Broadcasting functions
async def broadcast_new_item(item_data: dict):
    """Broadcast new item to all connected clients."""
    await manager.broadcast({
        'type': 'new_item',
        'data': item_data
    })


async def broadcast_item_update(item_id: str, updates: dict):
    """Broadcast item update to relevant clients."""
    await manager.broadcast_to_room(
        {
            'type': 'item_update',
            'item_id': item_id,
            'updates': updates
        },
        f"item:{item_id}"
    )


async def broadcast_alert(alert_data: dict):
    """Broadcast alert to all connected clients."""
    await manager.broadcast({
        'type': 'alert',
        'data': alert_data,
        'severity': alert_data.get('severity', 'medium')
    })


async def send_user_notification(user_id: str, notification: dict):
    """Send notification to specific user."""
    await manager.broadcast_to_user(
        {
            'type': 'notification',
            'data': notification
        },
        user_id
    )
