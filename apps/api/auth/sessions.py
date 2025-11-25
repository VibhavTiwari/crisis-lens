from typing import Dict, Any, Optional
from datetime import timedelta
import uuid
from services.redis_service import redis_service

class SessionManager:
    """Manage user sessions using Redis"""
    
    @staticmethod
    async def create_session(
        user_id: str,
        data: Dict[str, Any],
        ttl: int = 86400  # 24 hours
    ) -> str:
        """
        Create a new session
        
        Args:
            user_id: User ID
            data: Session data to store
            ttl: Time to live in seconds
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "user_id": user_id,
            "created_at": str(datetime.utcnow()),
            **data
        }
        
        await redis_service.set_session(session_id, session_data, ttl)
        
        return session_id
    
    @staticmethod
    async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return await redis_service.get_session(session_id)
    
    @staticmethod
    async def update_session(
        session_id: str,
        data: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Update session data"""
        existing = await redis_service.get_session(session_id)
        
        if existing:
            existing.update(data)
            await redis_service.set_session(
                session_id,
                existing,
                ttl or 86400
            )
    
    @staticmethod
    async def delete_session(session_id: str):
        """Delete a session (logout)"""
        await redis_service.delete_session(session_id)
    
    @staticmethod
    async def refresh_session(session_id: str, ttl: int = 86400):
        """Refresh session TTL"""
        session_data = await redis_service.get_session(session_id)
        
        if session_data:
            await redis_service.set_session(session_id, session_data, ttl)

from datetime import datetime

# Singleton instance
session_manager = SessionManager()
