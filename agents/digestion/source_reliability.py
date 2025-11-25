from typing import List, Any
from agents.digestion.base import DigestionAgent
from schemas.claim import Claim
from services.observability import observability_service

class SourceReliabilityAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="SourceReliabilityAgent")
        # In prod: Load reliability scores from DB
        self.source_scores = {
            "google_fact_check": 0.95,
            "who_ears": 0.9,
            "gdelt": 0.7,
            "youtube": 0.5,
            "reddit": 0.4,
            "twitter": 0.3
        }

    async def process(self, item: Any) -> Any:
        return item

    async def process_claims(self, claims: List[Claim]) -> List[Claim]:
        # This agent might update the reliability of the source of the CLAIM itself
        # or the sources of the EVIDENCE.
        
        # 1. Update evidence reliability
        for claim in claims:
            for evidence in claim.evidence:
                # Simple domain extraction or source matching
                # For now, we assume we can map URL to a source key or use default
                score = 0.5
                for key, val in self.source_scores.items():
                    if key in evidence.url:
                        score = val
                        break
                
                evidence.source_reliability = score
                observability_service.log_info(f"Updated evidence reliability for {evidence.url} to {score}")

        return claims
