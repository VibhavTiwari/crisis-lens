from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MediaItem(BaseModel):
    url: str
    type: str = Field(..., description="image, video, or audio")
    thumbnail_url: Optional[str] = None
    phash: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RawItem(BaseModel):
    id: str
    source: str = Field(..., description="gdelt, youtube, twitter, etc.")
    source_id: str
    url: str
    title: Optional[str] = None
    text: Optional[str] = None
    author: Optional[str] = None
    timestamp: datetime
    language_hint: Optional[str] = None
    media: List[MediaItem] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    ingested_at: datetime = Field(default_factory=datetime.utcnow)

class NormalizedItem(RawItem):
    language_detected: Optional[str] = None
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    # Enriched fields
    claims: List[Any] = Field(default_factory=list) # List[Claim] - using Any to avoid circular import
    risk_score: float = 0.0
