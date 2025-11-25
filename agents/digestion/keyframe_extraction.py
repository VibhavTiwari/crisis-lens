from typing import List
from agents.digestion.base import DigestionAgent
from schemas.item import NormalizedItem, MediaItem
from services.observability import observability_service

class KeyframeExtractionAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="KeyframeExtractionAgent")

    async def process(self, item: NormalizedItem) -> NormalizedItem:
        if not item.media:
            return item

        new_media = []
        for media in item.media:
            new_media.append(media)
            
            if media.type == "video":
                # Simulate extracting keyframes
                observability_service.log_info(f"Extracting keyframes for video {media.url}")
                
                # Create a mock keyframe image
                keyframe = MediaItem(
                    url=f"{media.url}_keyframe_1.jpg",
                    type="image",
                    metadata={"source_video": media.url, "is_keyframe": True}
                )
                new_media.append(keyframe)
        
        item.media = new_media
        return item
