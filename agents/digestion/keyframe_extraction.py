from typing import Any
from agents.base import BaseAgent
from schemas.item import MediaItem
from services.observability import observability_service
from ml.media.keyframe_extraction import keyframe_extractor
import os
import aiohttp
import aiofiles

class KeyframeExtractionAgent(BaseAgent):
    """Extract keyframes from videos"""
    
    def __init__(self):
        super().__init__(name="KeyframeExtractionAgent")
        self.download_dir = "temp_downloads"
        os.makedirs(self.download_dir, exist_ok=True)
    
    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, MediaItem):
            return await self.extract_keyframes(input_data)
        return input_data
    
    async def extract_keyframes(self, media: MediaItem) -> MediaItem:
        """Extract keyframes from video"""
        if media.type != "video":
            return media
        
        local_path = None
        try:
            observability_service.log_info(f"Processing video: {media.url}")
            
            # 1. Download video if it's a URL
            if media.url.startswith(('http://', 'https://')):
                local_path = await self._download_video(media.url)
            else:
                local_path = media.url
            
            # 2. Get video info
            video_info = keyframe_extractor.get_video_info(local_path)
            media.metadata.update(video_info)
            
            # 3. Extract keyframes
            keyframe_paths = keyframe_extractor.extract_keyframes(local_path)
            
            # 4. Update metadata
            media.metadata['keyframes_extracted'] = True
            media.metadata['keyframe_count'] = len(keyframe_paths)
            media.metadata['keyframe_paths'] = keyframe_paths
            
            observability_service.log_info(f"Extracted {len(keyframe_paths)} keyframes")
            
        except Exception as e:
            observability_service.log_error(f"Keyframe extraction failed: {e}")
            media.metadata['keyframes_error'] = str(e)
        finally:
            # Cleanup temp file if we downloaded it
            if local_path and local_path.startswith(self.download_dir) and os.path.exists(local_path):
                os.remove(local_path)
        
        return media

    async def _download_video(self, url: str) -> str:
        """Download video to temp file"""
        filename = url.split('/')[-1] or "temp_video.mp4"
        path = os.path.join(self.download_dir, filename)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(path, mode='wb') as f:
                        await f.write(await resp.read())
        return path
