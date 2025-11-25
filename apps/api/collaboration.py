"""
Real-time Collaboration Service for CrisisLens.

Handles presence tracking, activity broadcasting, and document locking.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()


class PresenceManager:
    """Manages user presence and activity."""
    
    def __init__(self):
        # Active users by resource
        self.active_users: Dict[str, Set[str]] = defaultdict(set)
        
        # User activity timestamps
        self.user_activity: Dict[str, datetime] = {}
        
        # User cursors/selections
        self.user_cursors: Dict[str, Dict[str, Any]] = {}
        
        # Document locks
        self.locks: Dict[str, Dict[str, Any]] = {}
    
    async def user_joined(self, resource_id: str, user_id: str):
        """
        Mark user as active on a resource.
        
        Args:
            resource_id: Resource identifier (e.g., 'item:123')
            user_id: User identifier
        """
        self.active_users[resource_id].add(user_id)
        self.user_activity[f"{resource_id}:{user_id}"] = datetime.utcnow()
        
        logger.info(f"User {user_id} joined {resource_id}")
        
        # Broadcast to other users
        await self._broadcast_presence_update(resource_id, user_id, 'joined')
    
    async def user_left(self, resource_id: str, user_id: str):
        """
        Mark user as inactive on a resource.
        
        Args:
            resource_id: Resource identifier
            user_id: User identifier
        """
        if resource_id in self.active_users:
            self.active_users[resource_id].discard(user_id)
        
        activity_key = f"{resource_id}:{user_id}"
        if activity_key in self.user_activity:
            del self.user_activity[activity_key]
        
        # Remove cursor
        cursor_key = f"{resource_id}:{user_id}"
        if cursor_key in self.user_cursors:
            del self.user_cursors[cursor_key]
        
        logger.info(f"User {user_id} left {resource_id}")
        
        # Broadcast to other users
        await self._broadcast_presence_update(resource_id, user_id, 'left')
    
    async def update_activity(self, resource_id: str, user_id: str):
        """
        Update user's last activity timestamp.
        
        Args:
            resource_id: Resource identifier
            user_id: User identifier
        """
        self.user_activity[f"{resource_id}:{user_id}"] = datetime.utcnow()
    
    async def update_cursor(
        self,
        resource_id: str,
        user_id: str,
        cursor_data: Dict[str, Any]
    ):
        """
        Update user's cursor position.
        
        Args:
            resource_id: Resource identifier
            user_id: User identifier
            cursor_data: Cursor position and selection data
        """
        cursor_key = f"{resource_id}:{user_id}"
        self.user_cursors[cursor_key] = {
            **cursor_data,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Broadcast to other users
        await self._broadcast_cursor_update(resource_id, user_id, cursor_data)
    
    def get_active_users(self, resource_id: str) -> list[str]:
        """
        Get list of active users on a resource.
        
        Args:
            resource_id: Resource identifier
        
        Returns:
            List of user IDs
        """
        return list(self.active_users.get(resource_id, set()))
    
    def get_user_cursors(self, resource_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all user cursors for a resource.
        
        Args:
            resource_id: Resource identifier
        
        Returns:
            Dictionary mapping user IDs to cursor data
        """
        cursors = {}
        for key, data in self.user_cursors.items():
            if key.startswith(f"{resource_id}:"):
                user_id = key.split(':', 1)[1]
                cursors[user_id] = data
        return cursors
    
    async def acquire_lock(
        self,
        resource_id: str,
        user_id: str,
        lock_type: str = 'edit'
    ) -> bool:
        """
        Acquire a lock on a resource.
        
        Args:
            resource_id: Resource identifier
            user_id: User identifier
            lock_type: Type of lock ('edit', 'delete', etc.)
        
        Returns:
            True if lock acquired, False otherwise
        """
        if resource_id in self.locks:
            existing_lock = self.locks[resource_id]
            
            # Check if lock has expired (30 minutes)
            locked_at = datetime.fromisoformat(existing_lock['locked_at'])
            if datetime.utcnow() - locked_at < timedelta(minutes=30):
                # Lock still valid
                if existing_lock['user_id'] != user_id:
                    return False
        
        # Acquire lock
        self.locks[resource_id] = {
            'user_id': user_id,
            'lock_type': lock_type,
            'locked_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Lock acquired: {resource_id} by {user_id}")
        
        # Broadcast lock status
        await self._broadcast_lock_update(resource_id, user_id, 'locked')
        
        return True
    
    async def release_lock(self, resource_id: str, user_id: str) -> bool:
        """
        Release a lock on a resource.
        
        Args:
            resource_id: Resource identifier
            user_id: User identifier
        
        Returns:
            True if lock released, False if user doesn't hold lock
        """
        if resource_id not in self.locks:
            return False
        
        lock = self.locks[resource_id]
        if lock['user_id'] != user_id:
            return False
        
        del self.locks[resource_id]
        
        logger.info(f"Lock released: {resource_id} by {user_id}")
        
        # Broadcast lock status
        await self._broadcast_lock_update(resource_id, user_id, 'unlocked')
        
        return True
    
    def get_lock_status(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Get lock status for a resource.
        
        Args:
            resource_id: Resource identifier
        
        Returns:
            Lock information if locked, None otherwise
        """
        return self.locks.get(resource_id)
    
    async def _broadcast_presence_update(
        self,
        resource_id: str,
        user_id: str,
        action: str
    ):
        """Broadcast presence update to WebSocket clients."""
        from apps.api.websocket import manager
        
        await manager.broadcast_to_room(
            {
                'type': 'presence_update',
                'resource_id': resource_id,
                'user_id': user_id,
                'action': action,
                'active_users': self.get_active_users(resource_id)
            },
            resource_id
        )
    
    async def _broadcast_cursor_update(
        self,
        resource_id: str,
        user_id: str,
        cursor_data: Dict[str, Any]
    ):
        """Broadcast cursor update to WebSocket clients."""
        from apps.api.websocket import manager
        
        await manager.broadcast_to_room(
            {
                'type': 'cursor_update',
                'resource_id': resource_id,
                'user_id': user_id,
                'cursor': cursor_data
            },
            resource_id
        )
    
    async def _broadcast_lock_update(
        self,
        resource_id: str,
        user_id: str,
        action: str
    ):
        """Broadcast lock update to WebSocket clients."""
        from apps.api.websocket import manager
        
        await manager.broadcast_to_room(
            {
                'type': 'lock_update',
                'resource_id': resource_id,
                'user_id': user_id,
                'action': action,
                'lock_status': self.get_lock_status(resource_id)
            },
            resource_id
        )


# Global presence manager
presence_manager = PresenceManager()


# API endpoints
@router.post("/collaboration/join/{resource_id}")
async def join_resource(
    resource_id: str,
    user_id: str = Depends(lambda: "user_123")  # TODO: Get from auth
):
    """Join a collaborative resource."""
    await presence_manager.user_joined(resource_id, user_id)
    
    return {
        'resource_id': resource_id,
        'user_id': user_id,
        'active_users': presence_manager.get_active_users(resource_id),
        'cursors': presence_manager.get_user_cursors(resource_id),
        'lock_status': presence_manager.get_lock_status(resource_id)
    }


@router.post("/collaboration/leave/{resource_id}")
async def leave_resource(
    resource_id: str,
    user_id: str = Depends(lambda: "user_123")  # TODO: Get from auth
):
    """Leave a collaborative resource."""
    await presence_manager.user_left(resource_id, user_id)
    
    return {'status': 'left', 'resource_id': resource_id}


@router.post("/collaboration/cursor/{resource_id}")
async def update_cursor_position(
    resource_id: str,
    cursor: Dict[str, Any],
    user_id: str = Depends(lambda: "user_123")  # TODO: Get from auth
):
    """Update cursor position in a collaborative session."""
    await presence_manager.update_cursor(resource_id, user_id, cursor)
    
    return {'status': 'updated'}


@router.post("/collaboration/lock/{resource_id}")
async def acquire_resource_lock(
    resource_id: str,
    lock_type: str = 'edit',
    user_id: str = Depends(lambda: "user_123")  # TODO: Get from auth
):
    """Acquire a lock on a resource."""
    success = await presence_manager.acquire_lock(resource_id, user_id, lock_type)
    
    if not success:
        raise HTTPException(
            status_code=409,
            detail="Resource is already locked by another user"
        )
    
    return {
        'status': 'locked',
        'resource_id': resource_id,
        'lock_type': lock_type
    }


@router.delete("/collaboration/lock/{resource_id}")
async def release_resource_lock(
    resource_id: str,
    user_id: str = Depends(lambda: "user_123")  # TODO: Get from auth
):
    """Release a lock on a resource."""
    success = await presence_manager.release_lock(resource_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=403,
            detail="You do not hold the lock on this resource"
        )
    
    return {'status': 'unlocked', 'resource_id': resource_id}


@router.get("/collaboration/presence/{resource_id}")
async def get_presence_info(resource_id: str):
    """Get presence information for a resource."""
    return {
        'resource_id': resource_id,
        'active_users': presence_manager.get_active_users(resource_id),
        'cursors': presence_manager.get_user_cursors(resource_id),
        'lock_status': presence_manager.get_lock_status(resource_id)
    }


# Broadcasting function for Kafka consumer
async def broadcast_activity(activity_data: Dict[str, Any]):
    """
    Broadcast user activity to relevant WebSocket clients.
    
    Args:
        activity_data: Activity event data
    """
    from apps.api.websocket import manager
    
    resource_id = activity_data.get('resource_id')
    user_id = activity_data.get('user_id')
    action = activity_data.get('action')
    
    if resource_id:
        await manager.broadcast_to_room(
            {
                'type': 'user_activity',
                'user_id': user_id,
                'action': action,
                'data': activity_data
            },
            resource_id
        )
