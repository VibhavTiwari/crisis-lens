from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    url: str
    text_snippet: Optional[str] = None
    source_reliability: float = 0.5
    support_score: float = 0.0 # -1 (refute) to 1 (support)
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

class Claim(BaseModel):
    id: str
    text: str
    normalized_item_id: str
    topic: Optional[str] = None
    
    # Scores
    checkworthiness: float = 0.0
    veracity_likelihood: float = 0.5
    harm_potential: float = 0.0
    risk_score: float = 0.0
    
    evidence: List[Evidence] = Field(default_factory=list)
    
    status: str = Field("new", description="new, processing, verified, discarded")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
