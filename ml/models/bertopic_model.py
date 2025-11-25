from bertopic import BERTopic
from typing import List, Tuple, Dict, Any
import numpy as np
from config import settings
from services.observability import observability_service
import os

class TopicModel:
    """BERTopic for dynamic topic modeling"""
    
    def __init__(self):
        self.model = None
        self.topics = None
        self.probs = None
        
    def load(self, model_path: str = None):
        """Load a pre-trained model or create a new one"""
        if self.model is None:
            if model_path and os.path.exists(model_path):
                observability_service.log_info(f"Loading BERTopic from {model_path}")
                self.model = BERTopic.load(model_path)
            else:
                observability_service.log_info("Creating new BERTopic model")
                # Create model with custom config
                self.model = BERTopic(
                    language="multilingual",
                    calculate_probabilities=True,
                    verbose=False,
                    min_topic_size=10,
                    nr_topics="auto"
                )
        
    def fit(self, documents: List[str], embeddings: np.ndarray = None) -> Tuple[List[int], np.ndarray]:
        """
        Fit the model on documents
        
        Args:
            documents: List of text documents
            embeddings: Pre-computed embeddings (optional)
            
        Returns:
            Tuple of (topics, probabilities)
        """
        self.load()
        
        observability_service.log_info(f"Fitting BERTopic on {len(documents)} documents")
        
        self.topics, self.probs = self.model.fit_transform(documents, embeddings)
        
        observability_service.log_info(f"Found {len(set(self.topics))} topics")
        
        return self.topics, self.probs
    
    def transform(self, documents: List[str], embeddings: np.ndarray = None) -> Tuple[List[int], np.ndarray]:
        """
        Predict topics for new documents
        
        Args:
            documents: List of text documents
            embeddings: Pre-computed embeddings (optional)
            
        Returns:
            Tuple of (topics, probabilities)
        """
        if self.model is None:
            raise ValueError("Model not fitted or loaded")
        
        topics, probs = self.model.transform(documents, embeddings)
        return topics, probs
    
    def get_topic_info(self, topic_id: int = None) -> Dict[str, Any]:
        """Get information about a topic"""
        if self.model is None:
            raise ValueError("Model not fitted or loaded")
        
        if topic_id is not None:
            # Get specific topic
            topic_words = self.model.get_topic(topic_id)
            return {
                "topic_id": topic_id,
                "words": [word for word, _ in topic_words],
                "scores": [score for _, score in topic_words]
            }
        else:
            # Get all topics
            return self.model.get_topic_info()
    
    def get_topic_label(self, topic_id: int) -> str:
        """Get a human-readable label for a topic"""
        if topic_id == -1:
            return "Outlier"
        
        topic_words = self.model.get_topic(topic_id)
        if topic_words:
            # Use top 3 words
            top_words = [word for word, _ in topic_words[:3]]
            return "_".join(top_words)
        return f"Topic_{topic_id}"
    
    def save(self, path: str):
        """Save the model"""
        if self.model:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.model.save(path)
            observability_service.log_info(f"BERTopic saved to {path}")

# Singleton instance
topic_model = TopicModel()
