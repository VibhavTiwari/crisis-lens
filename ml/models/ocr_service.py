import pytesseract
from PIL import Image
from typing import Dict, List
from config import settings
from services.observability import observability_service
import requests
from io import BytesIO

class OCRService:
    """Tesseract OCR for text extraction from images"""
    
    def __init__(self):
        # Set tesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_text(
        self,
        image_source: str,
        language: str = 'eng'
    ) -> Dict[str, any]:
        """
        Extract text from image
        
        Args:
            image_source: URL or file path to image
            language: Language code (eng, hin, ben, etc.)
            
        Returns:
            Dict with 'text', 'confidence', and 'boxes'
        """
        try:
            # Load image
            if image_source.startswith(('http://', 'https://')):
                response = requests.get(image_source)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image_source)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=language)
            
            # Get detailed data with bounding boxes
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract word boxes
            boxes = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    boxes.append({
                        'text': data['text'][i],
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': int(data['conf'][i])
                    })
            
            observability_service.log_info(f"OCR extracted {len(text.split())} words")
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence,
                'boxes': boxes,
                'language': language
            }
            
        except Exception as e:
            observability_service.log_error(f"OCR failed: {e}")
            return {
                'text': '',
                'confidence': 0,
                'boxes': [],
                'language': language
            }
    
    def extract_multilingual(
        self,
        image_source: str,
        languages: List[str] = None
    ) -> Dict[str, any]:
        """
        Try OCR with multiple languages
        
        Args:
            image_source: Image to process
            languages: List of language codes to try
            
        Returns:
            Best result across all languages
        """
        if languages is None:
            languages = ['eng', 'hin', 'ben']  # English, Hindi, Bengali
        
        results = []
        for lang in languages:
            result = self.extract_text(image_source, lang)
            results.append(result)
        
        # Return result with highest confidence
        best_result = max(results, key=lambda x: x['confidence'])
        return best_result

# Singleton instance
ocr_service = OCRService()
