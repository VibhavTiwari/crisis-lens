from datetime import datetime
from typing import Optional, Dict, Any
import json
from sqlalchemy.orm import Session
from models.user import AuditLog
from services.clickhouse_service import clickhouse_service

class AuditService:
    """Service for audit logging"""
    
    @staticmethod
    async def log_action(
        db: Session,
        user_id: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """
        Log a user action
        
        Args:
            db: Database session
            user_id: User performing the action
            action: Action name (login, verify_claim, publish_advisory, etc.)
            resource_type: Type of resource (item, claim, advisory)
            resource_id: ID of the resource
            details: Additional details as dict
            ip_address: IP address of the request
        """
        # Log to PostgreSQL for long-term storage and compliance
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            ip_address=ip_address
        )
        
        db.add(audit_log)
        db.commit()
        
        # Also log to ClickHouse for analytics
        await clickhouse_service.record_event(
            event_type=f"audit_{action}",
            item_id=resource_id or "n/a",
            source="audit",
            metadata={
                "user_id": user_id,
                "resource_type": resource_type,
                "ip_address": ip_address,
                **(details or {})
            }
        )
    
    @staticmethod
    def get_user_actions(
        db: Session,
        user_id: str,
        limit: int = 100
    ) -> list[AuditLog]:
        """Get recent actions for a user"""
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_resource_history(
        db: Session,
        resource_type: str,
        resource_id: str,
        limit: int = 50
    ) -> list[AuditLog]:
        """Get action history for a specific resource"""
        return db.query(AuditLog).filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        ).order_by(AuditLog.created_at.desc()).limit(limit).all()

# Singleton instance
audit_service = AuditService()
