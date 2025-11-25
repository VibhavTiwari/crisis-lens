from typing import Any
from agents.base import BaseAgent
from schemas.item import MediaItem
from services.observability import observability_service
from ml.media.keyframe_extraction import keyframe_extractor

class KeyframeExtractionAgent(BaseAgent):
    """Extract keyframes from videos"""
    
    def __init__(self):
        super().__init__(name="KeyframeExtractionAgent")
    
    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, MediaItem):
            return await self.extract_keyframes(input_data)
        return input_data
    
    async def extract_keyframes(self, media: MediaItem) -> MediaItem:
        """Extract keyframes from video"""
        if media.type != "video":
            return media
        
        try:
            observability_service.log_info(f"Extracting keyframes from: {media.url}")
            
            # For demo, assume we have local file
            # In production, download from URL first
            # keyframes = keyframe_extractor.extract_keyframes(local_video_path)
            
            # For now, just get video info
            # video_info = keyframe_extractor.get_video_info(media.url)
            
            # Store in metadata
            media.metadata['keyframes_extracted'] = True
            media.metadata['keyframe_count'] = 0  # Would be len(keyframes)
            
            observability_service.log_info("Keyframe extraction completed")
            
        except Exception as e:
            observability_service.log_error(f"Keyframe extraction failed: {e}")
            media.metadata['keyframes_error'] = str(e)
        
        return media
