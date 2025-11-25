from typing import Any
from agents.base import BaseAgent
from schemas.claim import Claim
from services.observability import observability_service
from ml.models.nli_model import nli_model

class NliVeracityAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="NliVeracityAgent")
        
    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, Claim):
            return await self.assess_veracity(input_data)
        return input_data
    
    async def assess_veracity(self, claim: Claim) -> Claim:
        """
        Assess claim veracity using NLI against evidence
        
        Uses Natural Language Inference to check if evidence
        supports, contradicts, or is neutral to the claim.
        """
        if not claim.evidence:
            observability_service.log_info(f"No evidence for claim {claim.id}, keeping default veracity")
            return claim
        
        try:
            support_scores = []
            
            for evidence in claim.evidence:
                if not evidence.text_snippet:
                    continue
                
                # Use NLI to check if evidence supports claim
                support_score = nli_model.check_veracity(
                    claim=claim.text,
                    evidence=evidence.text_snippet
                )
                
                support_scores.append(support_score)
                
                # Store the support score in evidence
                evidence.support_score = support_score
            
            if support_scores:
                # Average support score
                avg_support = sum(support_scores) / len(support_scores)
                
                # Convert from [-1, 1] to [0, 1]
                # -1 (contradicts) -> 0, 0 (neutral) -> 0.5, 1 (supports) -> 1
                veracity = (avg_support + 1) / 2
                
                # Update claim veracity with weighted average
                # Weight: 70% NLI, 30% existing veracity
                claim.veracity_likelihood = (
                    0.7 * veracity + 
                    0.3 * claim.veracity_likelihood
                )
                
                observability_service.log_info(
                    f"NLI veracity for claim {claim.id}: {veracity:.3f} "
                    f"(avg support: {avg_support:.3f})"
                )
            
        except Exception as e:
            observability_service.log_error(f"NLI veracity assessment failed: {e}")
        
        return claim
