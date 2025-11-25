from typing import List, Any
from agents.base import BaseAgent
from schemas.advisory import Advisory
from services.observability import observability_service
from ml.models.translation_service import translation_service

class AdvisoryTranslationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AdvisoryTranslationAgent")
        self.target_languages = ["hi", "mr", "bn", "ta", "te"]  # Indian languages

    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, Advisory):
            return await self.process(input_data)
        return input_data

    async def process(self, advisory: Advisory) -> Advisory:
        """Translate advisory to multiple languages"""
        observability_service.log_info(f"Translating advisory {advisory.id}")
        
        try:
            # Prepare advisory fields for translation
            to_translate = {
                "title": advisory.title,
                "summary": advisory.summary,
                "narrative_what_happened": advisory.narrative_what_happened,
                "narrative_verified": advisory.narrative_verified,
                "narrative_action": advisory.narrative_action
            }
            
            # Translate to all target languages
            translations = translation_service.translate_advisory(
                advisory=to_translate,
                target_languages=self.target_languages
            )
            
            # Store translations
            advisory.translations = translations
            
            observability_service.log_info(
                f"Translated advisory {advisory.id} to {len(translations)} languages"
            )
            
        except Exception as e:
            observability_service.log_error(f"Translation failed: {e}")
            
            # Fallback: mock translations
            advisory.translations = self._mock_translations(advisory)
        
        return advisory
    
    def _mock_translations(self, advisory: Advisory) -> dict:
        """Fallback mock translations"""
        translations = {}
        for lang in self.target_languages:
            translations[lang] = {
                "title": f"[{lang.upper()}] {advisory.title[:30]}...",
                "summary": f"[{lang.upper()}] {advisory.summary[:30]}...",
                "narrative_what_happened": f"[{lang.upper()}] Translation in progress",
                "narrative_verified": f"[{lang.upper()}] Translation in progress",
                "narrative_action": f"[{lang.upper()}] Translation in progress"
            }
        return translations
