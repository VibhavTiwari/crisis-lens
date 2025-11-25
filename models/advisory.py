from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Advisory(Base):
    __tablename__ = 'advisories'
    
    id = Column(String, primary_key=True)
    claim_id = Column(String, nullable=False, index=True)
    
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    narrative_what_happened = Column(Text, nullable=False)
    narrative_verified = Column(Text, nullable=False)
    narrative_action = Column(Text, nullable=False)
    
    language = Column(String, default="en")
    region = Column(String, nullable=True)
    
    status = Column(String, default="draft")  # draft, review, published
    version = Column(Integer, default=1)
    
    created_by = Column(String, ForeignKey('users.id'))
    approved_by = Column(String, ForeignKey('users.id'), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
class AdvisoryTranslation(Base):
    __tablename__ = 'advisory_translations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    advisory_id = Column(String, ForeignKey('advisories.id'))
    language = Column(String, nullable=False)
    
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    narrative_what_happened = Column(Text, nullable=False)
    narrative_verified = Column(Text, nullable=False)
    narrative_action = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
