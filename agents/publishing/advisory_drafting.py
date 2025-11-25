from typing import List, Any
from agents.base import BaseAgent
from schemas.advisory import Advisory
from schemas.item import NormalizedItem
from services.observability import observability_service
from ml.models.llm_service import llm_service
from datetime import datetime

class AdvisoryDraftingAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AdvisoryDraftingAgent")

    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, NormalizedItem):
            return await self.process(input_data)
        return input_data

    async def process(self, item: NormalizedItem) -> Advisory:
        """Draft advisory using LLM"""
        observability_service.log_info(f"Drafting advisory for item {item.id}")
        
        # Extract verified and debunked claims
        verified_claims = [
            c.text for c in (item.claims or []) 
            if c.veracity_likelihood > 0.8
        ]
        debunked_claims = [
            c.text for c in (item.claims or []) 
            if c.veracity_likelihood < 0.2
        ]
        
        try:
            # Use LLM to draft advisory
            sections = llm_service.draft_advisory(
                item_title=item.title or "Crisis Event",
                item_text=item.text or "",
                verified_claims=verified_claims,
                debunked_claims=debunked_claims
            )
            
            # Create Advisory object
            advisory = Advisory(
                id=f"adv_{item.id}",
                claim_id=item.id,
                title=f"Crisis Advisory: {item.title}",
                summary=sections.get('summary', 'No summary generated.'),
                narrative_what_happened=sections.get('what_happened', item.text[:200] if item.text else ''),
                narrative_verified=sections.get('verified', 'Analysis ongoing.'),
                narrative_action=sections.get('actions', 'Monitor official channels.'),
                status="draft",
                created_at=datetime.utcnow()
            )
            
            observability_service.log_info(f"Advisory drafted for {item.id}")
            
        except Exception as e:
            observability_service.log_error(f"LLM advisory drafting failed: {e}")
            
            # Fallback to template-based drafting
            advisory = self._draft_fallback(item, verified_claims, debunked_claims)
        
        return advisory
    
    def _draft_fallback(
        self,
        item: NormalizedItem,
        verified_claims: List[str],
        debunked_claims: List[str]
    ) -> Advisory:
        """Fallback template-based drafting"""
        summary = f"Reports indicate {item.title}. {item.text[:50] if item.text else ''}..."
        what_happened = item.text or "No details available."
        
        verified_text = (
            "Analysis confirms: " + ", ".join(verified_claims) 
            if verified_claims 
            else "Investigation ongoing."
        )
        action_text = "Avoid the area. Follow official channels for updates."
        
        return Advisory(
            id=f"adv_{item.id}",
            claim_id=item.id,
            title=f"Crisis Advisory: {item.title}",
            summary=summary,
            narrative_what_happened=what_happened,
            narrative_verified=verified_text,
            narrative_action=action_text,
            status="draft",
            created_at=datetime.utcnow()
        )
