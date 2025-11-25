from typing import List, Any
from agents.base import BaseAgent
from schemas.advisory import Advisory
from schemas.item import NormalizedItem
from services.observability import observability_service
from datetime import datetime

class AdvisoryDraftingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AdvisoryDraftingAgent")

    async def process(self, item: NormalizedItem) -> Advisory:
        # Simulate LLM drafting an advisory based on the item and its verified claims
        observability_service.log_info(f"Drafting advisory for item {item.id}")
        
        # In prod: Prompt LLM with item.text, claims, and verification status
        
        draft_text = f"ADVISORY: {item.title}\n\n"
        draft_text += f"Summary: {item.text[:100]}...\n\n"
        
        verified_claims = [c for c in (item.claims or []) if c.veracity_likelihood > 0.8]
        debunked_claims = [c for c in (item.claims or []) if c.veracity_likelihood < 0.2]
        
        if verified_claims:
            draft_text += "VERIFIED FACTS:\n"
            for c in verified_claims:
                draft_text += f"- {c.text}\n"
        
        if debunked_claims:
            draft_text += "\nFALSE CLAIMS:\n"
            for c in debunked_claims:
                draft_text += f"- {c.text}\n"
                
        advisory = Advisory(
            id=f"adv_{item.id}",
            item_id=item.id,
            title=f"Crisis Advisory: {item.title}",
            content=draft_text,
            severity="high" if item.risk_score > 0.7 else "medium",
            status="draft",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return advisory
