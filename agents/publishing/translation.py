from typing import List, Any
from agents.base import BaseAgent
from schemas.advisory import Advisory
from services.observability import observability_service

class AdvisoryTranslationAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="AdvisoryTranslationAgent")
        self.target_languages = ["hi", "mr", "bn"] # Hindi, Marathi, Bengali

    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, Advisory):
            return await self.process(input_data)
        return input_data

    async def process(self, advisory: Advisory) -> Advisory:
        observability_service.log_info(f"Translating advisory {advisory.id}")
        
        # Simulate translation
        translations = {}
        for lang in self.target_languages:
            # Mock translation
            translations[lang] = {
                "title": f"[{lang.upper()}] {advisory.title}",
                "summary": f"[{lang.upper()}] {advisory.summary[:50]}...",
                "narrative_what_happened": f"[{lang.upper()}] {advisory.narrative_what_happened[:50]}...",
                "narrative_verified": f"[{lang.upper()}] {advisory.narrative_verified[:50]}...",
                "narrative_action": f"[{lang.upper()}] {advisory.narrative_action[:50]}..."
            }
            
        advisory.translations = translations
        return advisory
