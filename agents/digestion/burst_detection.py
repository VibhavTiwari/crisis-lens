from typing import List
from agents.digestion.base import DigestionAgent
from schemas.item import NormalizedItem
from services.observability import observability_service

class BurstDetectionAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="BurstDetectionAgent")
        self.topic_counts = {}

    async def process(self, item: NormalizedItem) -> NormalizedItem:
        for topic in item.topics:
            count = self.topic_counts.get(topic, 0)
            self.topic_counts[topic] = count + 1
            
            # Simple burst detection: if count > threshold
            if count > 5:
                observability_service.log_warning(f"BURST DETECTED for topic: {topic}")
                # We could add a 'burst' flag to the item or trigger an alert
                
        return item
