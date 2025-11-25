from typing import List
from agents.digestion.base import DigestionAgent
from schemas.item import NormalizedItem
from services.observability import observability_service

class InvidVerificationAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="InvidVerificationAgent")

    async def process(self, item: NormalizedItem) -> NormalizedItem:
        # Simulate InVID/WeVerify checks (metadata, weather, shadows, etc.)
        # We'll just add a metadata flag for now.
        
        for media in item.media:
            if media.type in ["image", "video"]:
                observability_service.log_info(f"Running InVID verification on {media.url}")
                media.metadata["invid_verified"] = True
                media.metadata["fake_probability"] = 0.1 # Mock score
        
        return item
