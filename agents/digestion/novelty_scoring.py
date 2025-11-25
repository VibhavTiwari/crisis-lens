from typing import List, Any
from agents.digestion.base import DigestionAgent
from schemas.claim import Claim
from services.observability import observability_service

class NoveltyScoringAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="NoveltyScoringAgent")

    async def process(self, item: Any) -> Any:
        # Not applicable for item-level usually, but can be.
        return item

    async def process_claims(self, claims: List[Claim]) -> List[Claim]:
        for claim in claims:
            # Simulate novelty check
            # In prod: compare embedding with existing claims in vector DB
            
            # Mock logic: if text is short, it's not novel (just for variety)
            if len(claim.text) < 20:
                novelty_score = 0.2
            else:
                novelty_score = 0.9
                
            # We don't have a specific field for novelty in Claim schema yet, 
            # let's put it in risk_score or add a metadata field?
            # The schema has 'checkworthiness', 'veracity_likelihood', 'risk_score'.
            # Let's assume novelty feeds into checkworthiness.
            
            claim.checkworthiness = novelty_score * 0.5 + 0.5 # Base score
            observability_service.log_info(f"Claim {claim.id} novelty score: {novelty_score}")
            
        return claims
