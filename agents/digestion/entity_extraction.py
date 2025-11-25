import spacy
from typing import List, Dict, Any
from agents.digestion.base import DigestionAgent
from schemas.item import NormalizedItem
from services.observability import observability_service

class EntityExtractionAgent(DigestionAgent):
    def __init__(self):
        super().__init__(name="EntityExtractionAgent")
        try:
            # We use a small model for demo purposes. 
            # In production, we'd use 'en_core_web_trf' or multilingual models.
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            observability_service.log_warning("Downloading spacy model 'en_core_web_sm'...")
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    async def process(self, item: NormalizedItem) -> NormalizedItem:
        text = item.title or ""
        if item.text:
            text += " " + item.text
        
        if not text:
            return item

        doc = self.nlp(text)
        
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        # Update item with extracted entities
        # We need to create a new object or modify existing (Pydantic models are mutable by default)
        item.entities = entities
        observability_service.log_info(f"Extracted {len(entities)} entities from item {item.id}")
        
        return item
