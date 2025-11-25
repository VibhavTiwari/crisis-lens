"""
GDPR Compliance Service

Implements GDPR rights:
- Right to access (data export)
- Right to be forgotten (data deletion)
- Right to rectification
- Right to data portability
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import zipfile
import io
from sqlalchemy.orm import Session
from models import User, Item, Claim, AuditLog
import logging

logger = logging.getLogger(__name__)


class GDPRService:
    """Service for handling GDPR compliance requests."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def export_user_data(self, user_id: int) -> bytes:
        """
        Export all user data (Right to Access).
        
        Returns ZIP file with user data in JSON format.
        """
        logger.info(f"Exporting data for user {user_id}")
        
        # Collect all user data
        user_data = await self._collect_user_data(user_id)
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add user profile
            zip_file.writestr(
                'profile.json',
                json.dumps(user_data['profile'], indent=2)
            )
            
            # Add items
            zip_file.writestr(
                'items.json',
                json.dumps(user_data['items'], indent=2)
            )
            
            # Add claims
            zip_file.writestr(
                'claims.json',
                json.dumps(user_data['claims'], indent=2)
            )
            
            # Add activity logs
            zip_file.writestr(
                'activity.json',
                json.dumps(user_data['activity'], indent=2)
            )
            
            # Add metadata
            metadata = {
                'export_date': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'data_types': list(user_data.keys())
            }
            zip_file.writestr(
                'metadata.json',
                json.dumps(metadata, indent=2)
            )
        
        # Log export
        self._log_gdpr_action(user_id, 'data_export', 'completed')
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    async def delete_user_data(
        self,
        user_id: int,
        reason: Optional[str] = None,
        retain_anonymized: bool = True
    ) -> Dict[str, Any]:
        """
        Delete user data (Right to be Forgotten).
        
        Args:
            user_id: User ID to delete
            reason: Deletion reason
            retain_anonymized: Keep anonymized records for analytics
        
        Returns:
            Deletion summary
        """
        logger.info(f"Deleting data for user {user_id}")
        
        summary = {
            'user_id': user_id,
            'deleted_at': datetime.utcnow().isoformat(),
            'reason': reason,
            'items_deleted': 0,
            'claims_deleted': 0,
            'logs_deleted': 0
        }
        
        try:
            # Get user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            if retain_anonymized:
                # Anonymize instead of delete
                summary.update(await self._anonymize_user_data(user_id))
            else:
                # Hard delete
                # Delete user items
                items = self.db.query(Item).filter(Item.user_id == user_id).all()
                summary['items_deleted'] = len(items)
                for item in items:
                    self.db.delete(item)
                
                # Delete claims
                claims = self.db.query(Claim).filter(Claim.user_id == user_id).all()
                summary['claims_deleted'] = len(claims)
                for claim in claims:
                    self.db.delete(claim)
                
                # Delete activity logs (except audit trail)
                logs = self.db.query(AuditLog).filter(
                    AuditLog.user_id == user_id,
                    AuditLog.action_type != 'gdpr_deletion'
                ).all()
                summary['logs_deleted'] = len(logs)
                for log in logs:
                    self.db.delete(log)
                
                # Delete user
                self.db.delete(user)
            
            # Log deletion (preserved for compliance)
            self._log_gdpr_action(
                user_id,
                'data_deletion',
                'completed',
                metadata={'summary': summary, 'reason': reason}
            )
            
            self.db.commit()
            
            return summary
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting user data: {e}")
            raise
    
    async def rectify_user_data(
        self,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user data (Right to Rectification).
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Update allowed fields
        allowed_fields = ['name', 'email', 'preferences']
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(user, field, value)
        
        self._log_gdpr_action(user_id, 'data_rectification', 'completed')
        self.db.commit()
        
        return {'user_id': user_id, 'updated_fields': list(updates.keys())}
    
    async def _collect_user_data(self, user_id: int) -> Dict[str, Any]:
        """Collect all user data from database."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Profile data
        profile = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'preferences': user.preferences
        }
        
        # Items
        items = self.db.query(Item).filter(Item.user_id == user_id).all()
        items_data = [
            {
                'id': item.id,
                'title': item.title,
                'content': item.content,
                'created_at': item.created_at.isoformat() if item.created_at else None
            }
            for item in items
        ]
        
        # Claims
        claims = self.db.query(Claim).filter(Claim.user_id == user_id).all()
        claims_data = [
            {
                'id': claim.id,
                'text': claim.text,
                'verdict': claim.verdict,
                'created_at': claim.created_at.isoformat() if claim.created_at else None
            }
            for claim in claims
        ]
        
        # Activity logs
        logs = self.db.query(AuditLog).filter(AuditLog.user_id == user_id).all()
        activity_data = [
            {
                'action': log.action_type,
                'timestamp': log.created_at.isoformat() if log.created_at else None,
                'details': log.metadata
            }
            for log in logs
        ]
        
        return {
            'profile': profile,
            'items': items_data,
            'claims': claims_data,
            'activity': activity_data
        }
    
    async def _anonymize_user_data(self, user_id: int) -> Dict[str, Any]:
        """Anonymize user data while retaining for analytics."""
        from services.anonymization.anonymizer import anonymize_user
        
        result = await anonymize_user(self.db, user_id)
        return result
    
    def _log_gdpr_action(
        self,
        user_id: int,
        action: str,
        status: str,
        metadata: Optional[Dict] = None
    ):
        """Log GDPR action to audit trail."""
        audit_log = AuditLog(
            user_id=user_id,
            action_type=f"gdpr_{action}",
            status=status,
            metadata=metadata or {},
            created_at=datetime.utcnow()
        )
        self.db.add(audit_log)
        self.db.commit()


# API Endpoints
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

router = APIRouter(prefix="/gdpr", tags=["GDPR"])


class DataExportRequest(BaseModel):
    user_id: int


class DataDeletionRequest(BaseModel):
    user_id: int
    reason: Optional[str] = None
    confirm: bool


@router.post("/export")
async def export_data(
    request: DataExportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Export user data (GDPR Right to Access)."""
    # Verify user can only export their own data or is admin
    if request.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    service = GDPRService(db)
    zip_data = await service.export_user_data(request.user_id)
    
    return Response(
        content=zip_data,
        media_type='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename=user_data_{request.user_id}.zip'
        }
    )


@router.post("/delete")
async def delete_data(
    request: DataDeletionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete user data (GDPR Right to be Forgotten)."""
    if not request.confirm:
        raise HTTPException(status_code=400, detail="Deletion not confirmed")
    
    if request.user_id != current_user.id and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    service = GDPRService(db)
    summary = await service.delete_user_data(
        request.user_id,
        reason=request.reason
    )
    
    return {"message": "Data deletion initiated", "summary": summary}
