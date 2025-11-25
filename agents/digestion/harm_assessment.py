from typing import List, Any
from agents.digestion.base import DigestionAgent
from schemas.claim import Claim
from services.observability import observability_service

class HarmAssessmentAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="HarmAssessmentAgent")

    async def process(self, item: Any) -> Any:
        return item

    async def process_claims(self, claims: List[Claim]) -> List[Claim]:
        for claim in claims:
            # Simulate harm assessment
            # Keywords like "cure", "drink", "kill", "attack" might indicate high harm potential
            
            text = claim.text.lower()
            harm_score = 0.1 # Low baseline
            
            high_harm_keywords = ["cure", "medicine", "drink", "inject", "kill", "attack", "riot"]
            medium_harm_keywords = ["scam", "money", "fake", "lie"]
            
            if any(k in text for k in high_harm_keywords):
                harm_score = 0.9
            elif any(k in text for k in medium_harm_keywords):
                harm_score = 0.5
                
            claim.harm_potential = harm_score
            observability_service.log_info(f"Claim {claim.id} harm potential: {harm_score}")
            
        return claims
