from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models.base import get_db
from models.user import User, Role, Permission
from apps.api.auth.jwt import verify_token
from services.redis_service import redis_service
import hashlib

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token
    
    Dependency for protected endpoints
    """
    token = credentials.credentials
    
    # Verify token
    user_id = verify_token(token, token_type="access")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token is blacklisted
    is_blacklisted = await redis_service.get(f"blacklist:token:{token}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_roles(required_roles: List[str]):
    """
    Dependency to require specific roles
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: User = Depends(require_roles(["admin"]))):
            ...
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        user_role_names = [role.name for role in user.roles]
        
        if not any(role in user_role_names for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(required_roles)}"
            )
        
        return user
    
    return role_checker

def require_permission(resource: str, action: str):
    """
    Dependency to require specific permission
    
    Usage:
        @app.post("/items")
        async def create_item(
            user: User = Depends(require_permission("items", "create"))
        ):
            ...
    """
    async def permission_checker(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        # Superusers have all permissions
        if user.is_superuser:
            return user
        
        # Check if user has the required permission
        for role in user.roles:
            permissions = db.query(Permission).filter(
                Permission.role_id == role.id,
                Permission.resource == resource,
                Permission.action == action
            ).all()
            
            if permissions:
                return user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires permission: {action} on {resource}"
        )
    
    return permission_checker

async def verify_api_key(
    api_key: str,
    db: Session = Depends(get_db)
) -> User:
    """Verify API key and return associated user"""
    from models.user import APIKey
    
    # Hash the API key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Look up API key
    api_key_obj = db.query(APIKey).filter(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    ).first()
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check expiration
    from datetime import datetime
    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key expired"
        )
    
    # Update last used time
    api_key_obj.last_used_at = datetime.utcnow()
    db.commit()
    
    # Get user
    user = db.query(User).filter(User.id == api_key_obj.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user
