from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Literal
from config import settings
from services.observability import observability_service
import os

class NLIModel:
    """Natural Language Inference using DeBERTa"""
    
    def __init__(self, model_name: str = "microsoft/deberta-v3-base-mnli"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.labels = ["contradiction", "neutral", "entailment"]
        
    def load(self):
        """Load the model"""
        if self.model is None:
            cache_dir = os.path.join(settings.MODEL_CACHE_DIR, "transformers")
            os.makedirs(cache_dir, exist_ok=True)
            
            observability_service.log_info(f"Loading NLI model: {self.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=cache_dir
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                cache_dir=cache_dir
            )
            self.model.to(self.device)
            self.model.eval()
            
            observability_service.log_info(f"NLI model loaded on {self.device}")
    
    def predict(
        self,
        premise: str,
        hypothesis: str
    ) -> dict:
        """
        Predict entailment relationship
        
        Args:
            premise: The premise statement
            hypothesis: The hypothesis to test
            
        Returns:
            Dict with 'label' and 'scores' for each class
        """
        self.load()
        
        # Tokenize
        inputs = self.tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)[0]
        
        # Get scores
        scores = {
            label: float(prob)
            for label, prob in zip(self.labels, probs)
        }
        
        # Get prediction
        pred_idx = torch.argmax(probs).item()
        predicted_label = self.labels[pred_idx]
        
        return {
            "label": predicted_label,
            "scores": scores,
            "entailment_score": scores["entailment"],
            "contradiction_score": scores["contradiction"],
            "neutral_score": scores["neutral"]
        }
    
    def check_veracity(
        self,
        claim: str,
        evidence: str
    ) -> float:
        """
        Check if evidence supports a claim
        
        Returns:
            Support score from -1 (contradicts) to 1 (supports)
        """
        result = self.predict(evidence, claim)
        
        # Convert to support score
        # entailment = +1, neutral = 0, contradiction = -1
        support_score = (
            result["scores"]["entailment"] * 1.0 +
            result["scores"]["neutral"] * 0.0 +
            result["scores"]["contradiction"] * -1.0
        )
        
        return support_score

# Singleton instance
nli_model = NLIModel()
