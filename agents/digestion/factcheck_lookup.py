from typing import List, Any
from agents.digestion.base import DigestionAgent
from schemas.claim import Claim, Evidence
from services.observability import observability_service

class FactCheckLookupAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="FactCheckLookupAgent")

    async def process(self, item: Any) -> Any:
        return item

    async def process_claims(self, claims: List[Claim]) -> List[Claim]:
        for claim in claims:
            observability_service.log_info(f"Checking for existing fact-checks for: {claim.text}")
            
            # Simulate lookup in our 'fact_checks' index
            # If found, add as high-confidence evidence
            
            # Mock hit
            if "Mumbai" in claim.text:
                mock_fc = Evidence(
                    url="http://factcheck.org/mumbai-floods",
                    text_snippet="Verified: The video is from 2020, not 2025.",
                    source_reliability=1.0,
                    support_score=-1.0 # Refutes
                )
                claim.evidence.append(mock_fc)
                observability_service.log_info(f"Found existing fact-check for claim {claim.id}")
            
        return claims
