from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Advisory(BaseModel):
    id: str
    claim_id: str
    title: str
    summary: str
    narrative_what_happened: str
    narrative_verified: str
    narrative_action: str
    receipts: List[str] = Field(default_factory=list)
    translations: Dict[str, Any] = Field(default_factory=dict)
    
    language: str = "en"
    region: Optional[str] = None
    
    status: str = Field("draft", description="draft, review, published")
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = 1
