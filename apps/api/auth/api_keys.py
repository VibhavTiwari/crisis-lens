from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from sqlalchemy.orm import Session
from models.user import APIKey

class APIKeyManager:
    """Manage API keys"""
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a new API key"""
        # Generate a random 32-byte key
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def create_api_key(
        db: Session,
        user_id: str,
        name: str,
        expires_in_days: Optional[int] = 90
    ) -> tuple[APIKey, str]:
        """
        Create a new API key
        
        Args:
            db: Database session
            user_id: User ID to associate with
            name: Friendly name for the key
            expires_in_days: Days until expiration (None for no expiration)
            
        Returns:
            Tuple of (APIKey object, plaintext key)
            IMPORTANT: The plaintext key is only returned once!
        """
        # Generate key
        plaintext_key = APIKeyManager.generate_api_key()
        key_hash = APIKeyManager.hash_api_key(plaintext_key)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key object
        api_key = APIKey(
            user_id=user_id,
            key_hash=key_hash,
            name=name,
            expires_at=expires_at,
            is_active=True
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        # Return both the object and the plaintext key
        # The plaintext key should be shown to the user only once
        return api_key, plaintext_key
    
    @staticmethod
    def revoke_api_key(db: Session, api_key_id: str, user_id: str):
        """Revoke an API key"""
        api_key = db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id
        ).first()
        
        if api_key:
            api_key.is_active = False
            db.commit()
    
    @staticmethod
    def list_user_api_keys(db: Session, user_id: str) -> list[APIKey]:
        """List all API keys for a user"""
        return db.query(APIKey).filter(
            APIKey.user_id == user_id
        ).order_by(APIKey.created_at.desc()).all()
