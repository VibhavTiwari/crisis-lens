from google.cloud import translate_v2 as translate
from typing import List, Dict
from config import settings
from services.observability import observability_service
import os

class TranslationService:
    """Google Cloud Translation API"""
    
    def __init__(self):
        self.client = None
        self.target_languages = ["hi", "mr", "bn", "ta", "te"]  # Indian languages
        
    def _get_client(self):
        """Lazy load translation client"""
        if self.client is None:
            # Set credentials
            if hasattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS'):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
            
            try:
                self.client = translate.Client()
                observability_service.log_info("Google Translate client initialized")
            except Exception as e:
                observability_service.log_warning(f"Google Translate not available: {e}")
                self.client = "mock"  # Use mock for development
        
        return self.client
    
    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = None
    ) -> Dict[str, str]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g. 'hi', 'es')
            source_language: Source language (auto-detect if None)
            
        Returns:
            Dict with 'translatedText' and 'detectedSourceLanguage'
        """
        client = self._get_client()
        
        if client == "mock":
            # Mock translation for development
            return {
                "translatedText": f"[{target_language.upper()}] {text[:50]}...",
                "detectedSourceLanguage": source_language or "en"
            }
        
        try:
            result = client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            
            observability_service.log_info(f"Translated to {target_language}")
            
            return {
                "translatedText": result['translatedText'],
                "detectedSourceLanguage": result.get('detectedSourceLanguage', source_language)
            }
        except Exception as e:
            observability_service.log_error(f"Translation failed: {e}")
            return {
                "translatedText": text,
                "detectedSourceLanguage": source_language or "unknown"
            }
    
    def translate_advisory(
        self,
        advisory: Dict[str, str],
        target_languages: List[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """
        Translate advisory to multiple languages
        
        Args:
            advisory: Dict with 'title', 'summary', etc.
            target_languages: List of language codes
            
        Returns:
            Dict mapping language code to translated advisory
        """
        if target_languages is None:
            target_languages = self.target_languages
        
        translations = {}
        
        for lang in target_languages:
            translations[lang] = {}
            for field, value in advisory.items():
                if isinstance(value, str) and value:
                    result = self.translate_text(value, lang)
                    translations[lang][field] = result['translatedText']
        
        return translations
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        client = self._get_client()
        
        if client == "mock":
            return "en"
        
        try:
            result = client.detect_language(text)
            return result['language']
        except Exception as e:
            observability_service.log_error(f"Language detection failed: {e}")
            return "unknown"

# Singleton instance
translation_service = TranslationService()
