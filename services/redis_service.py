import redis.asyncio as redis
import json
from typing import Any, Optional
from datetime import timedelta
from config import settings
from services.observability import observability_service

class RedisService:
    def __init__(self):
        self.redis = None
        
    async def connect(self):
        """Connect to Redis"""
        if not self.redis:
            self.redis = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                encoding="utf-8",
                decode_responses=True
            )
            observability_service.log_info("Connected to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        await self.connect()
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = 3600
    ):
        """Set value in cache with TTL in seconds"""
        await self.connect()
        if not isinstance(value, str):
            value = json.dumps(value)
        
        if ttl:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        await self.connect()
        await self.redis.delete(key)
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check if request is within rate limit.
        Returns True if allowed, False if rate limited.
        """
        await self.connect()
        
        # Use sliding window with sorted sets
        now = int(redis.time.time())
        window_start = now - window_seconds
        
        pipe = self.redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Count requests in window
        pipe.zcard(key)
        # Set expiry
        pipe.expire(key, window_seconds)
        
        results = await pipe.execute()
        request_count = results[2]
        
        return request_count <= max_requests
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return await self.get(f"session:{session_id}")
    
    async def set_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        ttl: int = 86400  # 24 hours
    ):
        """Set session data"""
        await self.set(f"session:{session_id}", data, ttl)
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        await self.delete(f"session:{session_id}")
    
    async def cache_api_response(
        self,
        endpoint: str,
        params: Dict[str, Any],
        response: Any,
        ttl: int = 300  # 5 minutes
    ):
        """Cache API response"""
        cache_key = f"api:{endpoint}:{hash(str(sorted(params.items())))}"
        await self.set(cache_key, response, ttl)
    
    async def get_cached_api_response(
        self,
        endpoint: str,
        params: Dict[str, Any]
    ) -> Optional[Any]:
        """Get cached API response"""
        cache_key = f"api:{endpoint}:{hash(str(sorted(params.items())))}"
        return await self.get(cache_key)

# Singleton instance
redis_service = RedisService()
