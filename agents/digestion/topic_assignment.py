from typing import List
from agents.digestion.base import DigestionAgent
from schemas.item import NormalizedItem
from schemas.claim import Claim
from services.observability import observability_service

class TopicAssignmentAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="TopicAssignmentAgent")
        # In production, load BERTopic model here

    async def process(self, item: NormalizedItem) -> NormalizedItem:
        # Simulate topic assignment
        # We'll assign topics based on simple keywords for the demo
        
        text = (item.title or "") + " " + (item.text or "")
        text = text.lower()
        
        topics = []
        if "flood" in text or "rain" in text:
            topics.append("floods_mumbai_2025")
        elif "earthquake" in text:
            topics.append("earthquake_delhi_2025")
        else:
            topics.append("general_crisis")
            
        item.topics = topics
        observability_service.log_info(f"Assigned topics {topics} to item {item.id}")
        return item

    async def process_claims(self, claims: List[Claim]) -> List[Claim]:
        """
        Assign topics to claims (if different from item).
        """
        for claim in claims:
            # For now, inherit from item or re-evaluate
            # We'll just assume the item's topic applies
            pass 
        return claims
