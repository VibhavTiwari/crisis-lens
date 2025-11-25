from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from config import settings
from services.observability import observability_service
import os

class EmbeddingsModel:
    """Sentence Transformer embeddings for semantic similarity"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # for all-MiniLM-L6-v2
        
    def load(self):
        """Load the model"""
        if self.model is None:
            cache_dir = os.path.join(settings.MODEL_CACHE_DIR, "sentence-transformers")
            os.makedirs(cache_dir, exist_ok=True)
            
            observability_service.log_info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=cache_dir
            )
            observability_service.log_info(f"Embedding model loaded: {self.model_name}")
    
    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            
        Returns:
            Array of embeddings (n_texts, embedding_dim)
        """
        self.load()
        
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        
        return embeddings
    
    def encode_single(self, text: str) -> List[float]:
        """Encode a single text and return as list"""
        embedding = self.encode(text)
        return embedding[0].tolist()
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        from sklearn.metrics.pairwise import cosine_similarity
        
        emb1 = self.encode(text1)
        emb2 = self.encode(text2)
        
        sim = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]
        return float(sim)

# Singleton instance
embeddings_model = EmbeddingsModel()
