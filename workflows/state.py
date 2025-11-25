from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class WorkflowState(TypedDict, total=False):
    """State for the verification workflow"""
    
    # Input
    raw_item_id: str
    raw_item: Dict[str, Any]
    
    # Normalization
    normalized_item: Optional[Dict[str, Any]]
    language_detected: Optional[str]
    
    # Entities & Claims
    entities: List[Dict[str, Any]]
    claims: List[Dict[str, Any]]
    
    # Topics & Analysis
    topics: List[str]
    novelty_score: float
    is_burst: bool
    
    # Evidence
    evidence: List[Dict[str, Any]]
    fact_checks: List[Dict[str, Any]]
    
    # Scoring
    source_reliability: float
    corroboration_score: float
    veracity_scores: Dict[str, float]  # claim_id -> score
    risk_score: float
    
    # Advisory
    advisory_draft: Optional[Dict[str, Any]]
    advisory_translations: Optional[Dict[str, Any]]
    advisory_published: bool
    
    # Workflow control
    needs_human_review: bool
    human_review_status: Optional[str]  # pending, approved, rejected
    human_feedback: Optional[str]
    
    # Error handling
    errors: List[str]
    retry_count: int
    
    # Metadata
    workflow_id: str
    started_at: datetime
    updated_at: datetime
    status: str  # running, paused, completed, failed
