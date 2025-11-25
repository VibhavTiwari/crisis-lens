"""
Data Anonymization Service

Anonymizes personally identifiable information (PII) while
retaining data utility for analytics.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from models import User, Item, Claim, AuditLog
import hashlib
import secrets
import logging

logger = logging.getLogger(__name__)


class DataAnonymizer:
    """Service for anonymizing user data."""
    
    @staticmethod
    def anonymize_email(email: str) -> str:
        """Anonymize email address."""
        # Keep domain for analytics, hash local part
        local, domain = email.split('@')
        hashed = hashlib.sha256(local.encode()).hexdigest()[:8]
        return f"user_{hashed}@{domain}"
    
    @staticmethod
    def anonymize_name(name: str) -> str:
        """Anonymize user name."""
        return f"Anonymous_{secrets.token_hex(4)}"
    
    @staticmethod
    def anonymize_ip(ip_address: str) -> str:
        """Anonymize IP address (keep first 2 octets)."""
        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.0.0"
        return "0.0.0.0"
    
    @staticmethod
    def anonymize_location(location: str) -> str:
        """Anonymize location (keep only country/city)."""
        # Keep only high-level location
        parts = location.split(',')
        if len(parts) >= 2:
            return f"{parts[-2].strip()}, {parts[-1].strip()}"
        return location
    
    @staticmethod
    def remove_pii_from_text(text: str) -> str:
        """Remove PII from free text."""
        import re
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Remove phone numbers
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        text = re.sub(r'\+\d{1,3}\s?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,9}', '[PHONE]', text)
        
        # Remove credit card numbers
        text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', '[CARD]', text)
        
        # Remove SSN
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        # Remove URLs with usernames
        text = re.sub(r'https?://[^\s]+', '[URL]', text)
        
        return text


async def anonymize_user(db: Session, user_id: int) -> Dict[str, Any]:
    """
    Anonymize all data for a user.
    
    Replaces PII with anonymized versions while retaining
    data structure for analytics.
    """
    logger.info(f"Anonymizing user {user_id}")
    
    anonymizer = DataAnonymizer()
    summary = {
        'user_id': user_id,
        'anonymized_fields': [],
        'items_processed': 0,
        'claims_processed': 0
    }
    
    # Anonymize user profile
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        original_email = user.email
        user.email = anonymizer.anonymize_email(user.email)
        user.name = anonymizer.anonymize_name(user.name)
        user.is_anonymized = True
        summary['anonymized_fields'].extend(['email', 'name'])
        
        logger.info(f"Anonymized user {user_id}: {original_email} -> {user.email}")
    
    # Anonymize items
    items = db.query(Item).filter(Item.user_id == user_id).all()
    for item in items:
        if item.content:
            item.content = anonymizer.remove_pii_from_text(item.content)
        if item.location:
            item.location = anonymizer.anonymize_location(item.location)
        summary['items_processed'] += 1
    
    # Anonymize claims
    claims = db.query(Claim).filter(Claim.user_id == user_id).all()
    for claim in claims:
        if claim.text:
            claim.text = anonymizer.remove_pii_from_text(claim.text)
        summary['claims_processed'] += 1
    
    # Anonymize audit logs (keep structure, remove PII)
    logs = db.query(AuditLog).filter(AuditLog.user_id == user_id).all()
    for log in logs:
        if log.metadata and 'ip_address' in log.metadata:
            log.metadata['ip_address'] = anonymizer.anonymize_ip(
                log.metadata['ip_address']
            )
    
    db.commit()
    
    return summary


class PseudonymizationService:
    """Pseudonymization for data processing."""
    
    @staticmethod
    def pseudonymize(value: str, salt: str) -> str:
        """Create consistent pseudonym for a value."""
        return hashlib.sha256(f"{value}{salt}".encode()).hexdigest()
    
    @staticmethod
    def depseudonymize(pseudonym: str, mapping: Dict[str, str]) -> str:
        """Reverse pseudonymization if mapping exists."""
        return mapping.get(pseudonym, pseudonym)


# Utility functions
def anonymize_dataset(
    db: Session,
    table_name: str,
    fields: List[str]
) -> int:
    """
    Anonymize specific fields in a table.
    
    Returns number of records processed.
    """
    anonymizer = DataAnonymizer()
    count = 0
    
    # This is a simplified example
    # In production, use SQLAlchemy Core or specific model queries
    
    return count


def create_anonymized_export(
    db: Session,
    filters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create anonymized data export for research/analytics.
    """
    # Export data with all PII removed
    # Useful for sharing with researchers or third parties
    pass
