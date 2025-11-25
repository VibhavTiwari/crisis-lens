from typing import List, Any
from agents.digestion.base import DigestionAgent
from schemas.claim import Claim
from services.observability import observability_service

class RiskScoringAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="RiskScoringAgent")

    async def process(self, item: Any) -> Any:
        return item

    async def process_claims(self, claims: List[Claim]) -> List[Claim]:
        for claim in claims:
            # Risk Score = Function(Checkworthiness, Veracity, Harm)
            # High Risk = High Harm + (Low Veracity OR High Uncertainty) + High Checkworthiness
            
            # Veracity: 0 (False), 0.5 (Uncertain), 1 (True)
            # We care about "False" or "Uncertain" combined with Harm.
            
            # Invert veracity for risk: 1 - veracity? 
            # If veracity is 0 (False), risk factor is 1.
            # If veracity is 0.5 (Uncertain), risk factor is 0.5?
            # If veracity is 1 (True), risk factor is 0.
            
            veracity_risk_factor = 1.0 - claim.veracity_likelihood
            
            # Simple formula
            # Risk = (Harm * 0.5) + (VeracityRisk * 0.3) + (Checkworthiness * 0.2)
            
            risk = (claim.harm_potential * 0.5) + \
                   (veracity_risk_factor * 0.3) + \
                   (claim.checkworthiness * 0.2)
                   
            claim.risk_score = min(1.0, risk)
            observability_service.log_info(f"Claim {claim.id} FINAL RISK SCORE: {claim.risk_score:.2f}")
            
        return claims
