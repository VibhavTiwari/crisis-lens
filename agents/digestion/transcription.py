from typing import Any, Dict
from agents.base import BaseAgent
from schemas.item import MediaItem
from services.observability import observability_service
from ml.models.whisper_model import whisper_model
import tempfile
import os

class TranscriptionAgent(BaseAgent):
    """Transcribe audio/video using Whisper"""
    
    def __init__(self):
        super().__init__(name="TranscriptionAgent")
    
    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, MediaItem):
            return await self.transcribe(input_data)
        return input_data
    
    async def transcribe(self, media: MediaItem) -> MediaItem:
        """Transcribe audio/video"""
        if media.type not in ["audio", "video"]:
            return media
        
        try:
            observability_service.log_info(f"Transcribing: {media.url}")
            
            # Download media to temp file
            # In production, handle remote URLs properly
            temp_path = self._download_media(media.url)
            
            # Transcribe
            result = whisper_model.transcribe(temp_path)
            
            # Store transcription in metadata
            media.metadata['transcription'] = {
                'text': result['text'],
                'language': result['language'],
                'segments': result['segments'][:10]  # Store first 10 segments
            }
            
            observability_service.log_info(
                f"Transcribed {len(result['segments'])} segments "
                f"(language: {result['language']})"
            )
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
        except Exception as e:
            observability_service.log_error(f"Transcription failed: {e}")
            media.metadata['transcription'] = {'text': '', 'language': 'unknown'}
        
        return media
    
    def _download_media(self, url: str) -> str:
        """Download media to temp file"""
        # Simplified - in production, use aiohttp
        import requests
        
        response = requests.get(url, stream=True)
        
        # Determine extension
        ext = '.mp3' if 'audio' in response.headers.get('content-type', '') else '.mp4'
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
        
        temp_file.close()
        return temp_file.name
