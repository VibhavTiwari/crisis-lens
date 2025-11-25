from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from models.base import get_db
from models.user import User, Role
from apps.api.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password
)
from apps.api.auth.rbac import get_current_user, require_roles
from apps.api.auth.oauth import oauth, get_google_user_info, get_github_user_info
from apps.api.auth.api_keys import APIKeyManager
from services.audit_service import audit_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    roles: list[str]
    
    class Config:
        from_attributes = True

# Registration
@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True
    )
    
    # Assign default role
    default_role = db.query(Role).filter(Role.name == "verifier").first()
    if default_role:
        user.roles.append(default_role)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Audit log
    await audit_service.log_action(
        db=db,
        user_id=user.id,
        action="register",
        details={"email": user.email, "username": user.username}
    )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        roles=[role.name for role in user.roles]
    )

# Login
@router.post("/login", response_model=Token)
async def login(
    request: Request,
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    # Find user
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Audit log
    await audit_service.log_action(
        db=db,
        user_id=user.id,
        action="login",
        ip_address=request.client.host if request.client else None
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)

# Refresh token
@router.post("/refresh", response_model=Token)
async def refresh(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    user_id = verify_token(token_data.refresh_token, token_type="refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    return Token(access_token=access_token, refresh_token=refresh_token)

# Get current user
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        roles=[role.name for role in current_user.roles]
    )

# OAuth routes
@router.get("/google/login")
async def google_login(request: Request):
    """Redirect to Google OAuth"""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    token = await oauth.google.authorize_access_token(request)
    user_info = await get_google_user_info(token)
    
    email = user_info.get('email')
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by Google")
    
    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        user = User(
            email=email,
            username=email.split('@')[0],
            full_name=user_info.get('name'),
            oauth_provider='google',
            oauth_id=user_info.get('sub'),
            is_active=True
        )
        
        # Assign default role
        default_role = db.query(Role).filter(Role.name == "verifier").first()
        if default_role:
            user.roles.append(default_role)
        
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Audit log
    await audit_service.log_action(
        db=db,
        user_id=user.id,
        action="oauth_login",
        details={"provider": "google"},
        ip_address=request.client.host if request.client else None
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)

# API Key management
class APIKeyCreate(BaseModel):
    name: str
    expires_in_days: Optional[int] = 90

class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: Optional[str] = None  # Only included on creation
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    is_active: bool

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key"""
    api_key, plaintext_key = APIKeyManager.create_api_key(
        db=db,
        user_id=current_user.id,
        name=key_data.name,
        expires_in_days=key_data.expires_in_days
    )
    
    # Audit log
    await audit_service.log_action(
        db=db,
        user_id=current_user.id,
        action="create_api_key",
        resource_id=api_key.id,
        details={"name": key_data.name}
    )
    
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key=plaintext_key,  # Only returned once!
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used_at=api_key.last_used_at,
        is_active=api_key.is_active
    )

@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's API keys"""
    keys = APIKeyManager.list_user_api_keys(db, current_user.id)
    
    return [
        APIKeyResponse(
            id=key.id,
            name=key.name,
            created_at=key.created_at,
            expires_at=key.expires_at,
            last_used_at=key.last_used_at,
            is_active=key.is_active
        )
        for key in keys
    ]

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke an API key"""
    APIKeyManager.revoke_api_key(db, key_id, current_user.id)
    
    # Audit log
    await audit_service.log_action(
        db=db,
        user_id=current_user.id,
        action="revoke_api_key",
        resource_id=key_id
    )
    
    return {"message": "API key revoked"}

# Admin routes
@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    users = db.query(User).all()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            roles=[role.name for role in user.roles]
        )
        for user in users
    ]
