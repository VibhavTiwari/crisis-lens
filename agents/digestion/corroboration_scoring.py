from typing import List, Any
from agents.digestion.base import DigestionAgent
from schemas.claim import Claim
from services.observability import observability_service

class CorroborationScoringAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="CorroborationScoringAgent")

    async def process(self, item: Any) -> Any:
        return item

    async def process_claims(self, claims: List[Claim]) -> List[Claim]:
        for claim in claims:
            if not claim.evidence:
                claim.risk_score = 0.5 # Default uncertainty
                continue

            # Simple weighted average of evidence support
            # support_score: -1 (refute) to 1 (support)
            # weight = source_reliability
            
            total_weight = 0.0
            weighted_sum = 0.0
            
            for ev in claim.evidence:
                weight = ev.source_reliability
                weighted_sum += ev.support_score * weight
                total_weight += weight
            
            if total_weight > 0:
                final_score = weighted_sum / total_weight
                # final_score is between -1 and 1
                # We map this to veracity_likelihood (0 to 1)
                # -1 -> 0 (False), 0 -> 0.5 (Uncertain), 1 -> 1 (True)
                claim.veracity_likelihood = (final_score + 1) / 2
                observability_service.log_info(f"Claim {claim.id} veracity: {claim.veracity_likelihood} (based on {len(claim.evidence)} evidence)")
            
        return claims
