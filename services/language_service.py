import os
import fasttext
from typing import Tuple
from config import settings

class LanguageService:
    def __init__(self):
        self.model_path = os.path.join(settings.MODEL_CACHE_DIR, "lid.176.bin")
        self.model = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            print(f"Warning: Language model not found at {self.model_path}. Language detection will be disabled.")
            return
        
        try:
            self.model = fasttext.load_model(self.model_path)
        except Exception as e:
            print(f"Error loading language model: {e}")

    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detects language of the text.
        Returns (language_code, confidence).
        """
        if not self.model or not text:
            return "unknown", 0.0
        
        clean_text = text.replace("\n", " ")
        try:
            predictions = self.model.predict(clean_text, k=1)
            lang_label = predictions[0][0]
            confidence = predictions[1][0]
            
            # Format: __label__en -> en
            lang_code = lang_label.replace("__label__", "")
            return lang_code, float(confidence)
        except Exception as e:
            print(f"Error during language detection: {e}")
            return "unknown", 0.0

language_service = LanguageService()
