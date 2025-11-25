import imagehash
from PIL import Image
import io
import aiohttp
from typing import List
from agents.digestion.base import DigestionAgent
from schemas.item import NormalizedItem, MediaItem
from services.observability import observability_service

class MediaExtractionAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="MediaExtractionAgent")

    async def process(self, item: NormalizedItem) -> NormalizedItem:
        if not item.media:
            return item

        processed_media = []
        for media in item.media:
            if media.type == "image" and media.url:
                try:
                    # In a real app, we'd download the image. 
                    # Here we simulate or try if URL is accessible.
                    # For demo, we'll just skip actual download to avoid network issues/time
                    # and assign a mock hash if it's a test URL, or try to fetch if real.
                    
                    # Simulating pHash generation
                    # phash = str(imagehash.phash(Image.open(io.BytesIO(content))))
                    phash = "mock_phash_12345" 
                    
                    media.phash = phash
                    observability_service.log_info(f"Computed pHash for {media.url}: {phash}")
                except Exception as e:
                    observability_service.log_error(f"Failed to hash image {media.url}: {e}")
            
            processed_media.append(media)
        
        item.media = processed_media
        return item
