from typing import Any, Dict
from agents.base import BaseAgent
from schemas.item import MediaItem
from services.observability import observability_service
from ml.models.ocr_service import ocr_service

class OCRAgent(BaseAgent):
    """Extract text from images using OCR"""
    
    def __init__(self):
        super().__init__(name="OCRAgent")
    
    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, MediaItem):
            return await self.extract_text(input_data)
        return input_data
    
    async def extract_text(self, media: MediaItem) -> MediaItem:
        """Extract text from image"""
        if media.type != "image":
            return media
        
        try:
            observability_service.log_info(f"Running OCR on image: {media.url}")
            
            # Extract text with multilingual support
            result = ocr_service.extract_multilingual(
                image_source=media.url,
                languages=['eng', 'hin', 'ben']
            )
            
            # Store OCR results in metadata
            media.metadata['ocr'] = {
                'text': result['text'],
                'confidence': result['confidence'],
                'language': result['language'],
                'word_count': len(result['text'].split())
            }
            
            observability_service.log_info(
                f"OCR extracted {len(result['text'].split())} words "
                f"(confidence: {result['confidence']:.2f}%)"
            )
            
        except Exception as e:
            observability_service.log_error(f"OCR failed: {e}")
            media.metadata['ocr'] = {'text': '', 'confidence': 0}
        
        return media
