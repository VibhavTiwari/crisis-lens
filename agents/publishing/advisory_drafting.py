from typing import List, Any
from agents.base import BaseAgent
from schemas.advisory import Advisory
from schemas.item import NormalizedItem
from services.observability import observability_service
from datetime import datetime

class AdvisoryDraftingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AdvisoryDraftingAgent")

    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, NormalizedItem):
            return await self.process(input_data)
        return input_data

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
                
        # Construct narrative fields
        summary = f"Reports indicate {item.title}. {item.text[:50]}..."
        what_happened = item.text or "No details available."
        
        verified_text = "Analysis confirms: " + ", ".join([c.text for c in verified_claims]) if verified_claims else "Investigation ongoing."
        action_text = "Avoid the area. Follow official channels."
        
        advisory = Advisory(
            id=f"adv_{item.id}",
            claim_id=item.id, # Using item_id as claim_id for now
            title=f"Crisis Advisory: {item.title}",
            summary=summary,
            narrative_what_happened=what_happened,
            narrative_verified=verified_text,
            narrative_action=action_text,
            status="draft",
            created_at=datetime.utcnow()
        )
        
        return advisory
