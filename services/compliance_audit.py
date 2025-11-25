"""
Enhanced Audit Trail with Blockchain-style Integrity

Extension to existing audit service with compliance features.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
import hashlib
from sqlalchemy.orm import Session
from models import AuditLog
import logging

logger = logging.getLogger(__name__)


class ComplianceAuditService:
    """Enhanced audit service for compliance requirements."""
    
    def __init__(self, db: Session):
        self.db = db
        self.previous_hash = self._get_latest_hash()
    
    def log_compliance_action(
        self,
        action_type: str,
        user_id: Optional[int],
        details: Dict[str, Any],
        ip_address: Optional[str] = None
    ) -> AuditLog:
        """Log compliance-related action with integrity hash."""
        timestamp = datetime.utcnow()
        
        # Build audit data
        audit_data = {
            'action_type': action_type,
            'user_id': user_id,
            'details': details,
            'ip_address': ip_address,
            'timestamp': timestamp.isoformat()
        }
        
        # Calculate integrity hash
        entry_hash = self._calculate_hash(audit_data, self.previous_hash)
        audit_data['hash'] = entry_hash
        audit_data['previous_hash'] = self.previous_hash
        
        # Create audit log
        audit_log = AuditLog(
            action_type=action_type,
            user_id=user_id,
            metadata=audit_data,
            created_at=timestamp
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        self.previous_hash = entry_hash
        logger.info(f"Compliance audit logged: {action_type}")
        
        return audit_log
    
    def _calculate_hash(self, data: Dict, previous: Optional[str]) -> str:
        """Calculate SHA-256 hash for audit chain."""
        data_str = json.dumps(data, sort_keys=True)
        combined = f"{previous or ''}{data_str}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def _get_latest_hash(self) -> Optional[str]:
        """Get the latest hash from audit chain."""
        latest = self.db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).first()
        
        if latest and latest.metadata and 'hash' in latest.metadata:
            return latest.metadata['hash']
        return None
    
    def verify_chain_integrity(self) -> bool:
        """Verify the integrity of the audit chain."""
        logs = self.db.query(AuditLog).order_by(AuditLog.created_at).all()
        
        previous_hash = None
        for log in logs:
            if 'hash' not in log.metadata:
                continue
            
            # Recalculate hash
            temp_data = dict(log.metadata)
            stored_hash = temp_data.pop('hash')
            temp_data.pop('previous_hash', None)
            
            recalc_hash = self._calculate_hash(temp_data, previous_hash)
            
            if recalc_hash != stored_hash:
                logger.error(f"Audit chain integrity violated at log {log.id}")
                return False
            
            previous_hash = stored_hash
        
        return True
