from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch
import requests
from io import BytesIO
from typing import List, Union
from config import settings
from services.observability import observability_service
import os

class CLIPImageModel:
    """CLIP for image-text multimodal tasks"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedding_dim = 512
        
    def load(self):
        """Load the model"""
        if self.model is None:
            cache_dir = os.path.join(settings.MODEL_CACHE_DIR, "clip")
            os.makedirs(cache_dir, exist_ok=True)
            
            observability_service.log_info(f"Loading CLIP model: {self.model_name}")
            
            self.processor = CLIPProcessor.from_pretrained(
                self.model_name,
                cache_dir=cache_dir
            )
            self.model = CLIPModel.from_pretrained(
                self.model_name,
                cache_dir=cache_dir
            )
            self.model.to(self.device)
            self.model.eval()
            
            observability_service.log_info(f"CLIP model loaded on {self.device}")
    
    def load_image(self, image_source: Union[str, Image.Image]) -> Image.Image:
        """Load image from URL, path, or PIL Image"""
        if isinstance(image_source, Image.Image):
            return image_source
        elif image_source.startswith(('http://', 'https://')):
            response = requests.get(image_source)
            return Image.open(BytesIO(response.content))
        else:
            return Image.open(image_source)
    
    def encode_image(self, image_source: Union[str, Image.Image]) -> List[float]:
        """
        Generate embedding for an image
        
        Args:
            image_source: URL, file path, or PIL Image
            
        Returns:
            Image embedding as list
        """
        self.load()
        
        image = self.load_image(image_source)
        
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            # Normalize
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features[0].cpu().numpy().tolist()
    
    def encode_text(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to encode
            
        Returns:
            Text embedding as list
        """
        self.load()
        
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            # Normalize
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        
        return text_features[0].cpu().numpy().tolist()
    
    def image_text_similarity(
        self,
        image_source: Union[str, Image.Image],
        text: str
    ) -> float:
        """
        Calculate similarity between image and text
        
        Returns:
            Similarity score (0-1)
        """
        self.load()
        
        image = self.load_image(image_source)
        
        inputs = self.processor(
            text=[text],
            images=image,
            return_tensors="pt",
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Get similarity (already computed by CLIP)
            logits_per_image = outputs.logits_per_image
            similarity = torch.sigmoid(logits_per_image)[0][0]
        
        return float(similarity)
    
    def zero_shot_classification(
        self,
        image_source: Union[str, Image.Image],
        candidate_labels: List[str]
    ) -> dict:
        """
        Classify image using text labels
        
        Args:
            image_source: Image to classify
            candidate_labels: List of possible labels
            
        Returns:
            Dict with labels and scores
        """
        self.load()
        
        image = self.load_image(image_source)
        
        inputs = self.processor(
            text=candidate_labels,
            images=image,
            return_tensors="pt",
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = torch.softmax(logits_per_image, dim=1)[0]
        
        results = {
            label: float(prob)
            for label, prob in zip(candidate_labels, probs)
        }
        
        # Sort by score
        results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
        
        return results

# Singleton instance
clip_model = CLIPImageModel()
