import re
from typing import List
from agents.digestion.base import DigestionAgent
from schemas.item import NormalizedItem
from schemas.claim import Claim
from services.observability import observability_service

class ClaimExtractionAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="ClaimExtractionAgent")

    async def process(self, item: NormalizedItem) -> List[Claim]:
        """
        Note: This agent returns a List[Claim], not NormalizedItem.
        It branches the pipeline from Item -> Claims.
        """
        text = item.title or ""
        if item.text:
            text += " " + item.text
            
        claims = self._extract_claims_heuristic(text, item.id)
        observability_service.log_info(f"Extracted {len(claims)} claims from item {item.id}")
        return claims

    def _extract_claims_heuristic(self, text: str, item_id: str) -> List[Claim]:
        """
        Simple heuristic to extract claims. 
        In a real system, this would use an LLM or a finetuned BERT model.
        """
        claims = []
        
        # Split by sentences (naive)
        sentences = re.split(r'(?<=[.!?]) +', text)
        
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if len(sent) < 10:
                continue
                
            # Heuristic: Sentences with numbers or specific keywords might be claims
            # This is very basic.
            keywords = ["dead", "injured", "killed", "trapped", "flooded", "collapsed", "fire", "leak"]
            if any(k in sent.lower() for k in keywords) or re.search(r'\d+', sent):
                claim = Claim(
                    id=f"{item_id}_claim_{i}",
                    text=sent,
                    normalized_item_id=item_id,
                    status="new"
                )
                claims.append(claim)
                
        return claims
