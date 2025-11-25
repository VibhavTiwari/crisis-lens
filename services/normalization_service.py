from typing import List
from schemas.item import RawItem, NormalizedItem
from services.language_service import language_service

class NormalizationService:
    @staticmethod
    def normalize_item(item: RawItem) -> NormalizedItem:
        """
        Converts a RawItem to a NormalizedItem.
        Performs language detection.
        """
        text_to_analyze = item.title or ""
        if item.text:
            text_to_analyze += " " + item.text
            
        lang, conf = language_service.detect_language(text_to_analyze)
        
        # If source gave a hint and we failed or are unsure, use hint?
        # For now, trust model if confidence is high, else hint
        if lang == "unknown" and item.language_hint:
            lang = item.language_hint

        return NormalizedItem(
            **item.dict(),
            language_detected=lang,
            entities=[], # To be filled by Entity Extraction Agent
            topics=[]    # To be filled by Topic Agent
        )

normalization_service = NormalizationService()
