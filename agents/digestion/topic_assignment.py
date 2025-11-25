from typing import Any
from agents.base import BaseAgent
from schemas.item import NormalizedItem
from services.observability import observability_service
from ml.models.bertopic_model import topic_model
from ml.models.embeddings import embeddings_model

class TopicAssignmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="TopicAssignmentAgent")
        self.model_fitted = False
        
    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, list):
            # Batch processing
            return await self.assign_topics_batch(input_data)
        elif isinstance(input_data, NormalizedItem):
            return await self.assign_topic(input_data)
        return input_data
    
    async def assign_topic(self, item: NormalizedItem) -> NormalizedItem:
        """Assign topic to a single item"""
        if not item.text:
            return item
        
        try:
            # Generate embedding
            embedding = embeddings_model.encode_single(item.text)
            
            # Predict topic
            topics, probs = topic_model.transform([item.text], [embedding])
            
            topic_id = topics[0]
            topic_label = topic_model.get_topic_label(topic_id)
            
            item.topics = [topic_label]
            
            observability_service.log_info(
                f"Assigned topic '{topic_label}' to item {item.id}"
            )
            
        except Exception as e:
            observability_service.log_error(f"Topic assignment failed: {e}")
            # Fallback to keyword-based topic
            item.topics = self._extract_keywords(item.text)
        
        return item
    
    async def assign_topics_batch(self, items: list[NormalizedItem]) -> list[NormalizedItem]:
        """Assign topics to a batch of items"""
        texts = [item.text for item in items if item.text]
        
        if not texts:
            return items
        
        try:
            # Generate embeddings for all texts
            embeddings = embeddings_model.encode(texts, batch_size=32)
            
            # Fit or transform
            if not self.model_fitted:
                observability_service.log_info(f"Fitting BERTopic on {len(texts)} documents")
                topics, probs = topic_model.fit(texts, embeddings)
                self.model_fitted = True
            else:
                topics, probs = topic_model.transform(texts, embeddings)
            
            # Assign topics to items
            text_idx = 0
            for item in items:
                if item.text:
                    topic_id = topics[text_idx]
                    topic_label = topic_model.get_topic_label(topic_id)
                    item.topics = [topic_label]
                    text_idx += 1
            
            observability_service.log_info(f"Assigned topics to {len(texts)} items")
            
        except Exception as e:
            observability_service.log_error(f"Batch topic assignment failed: {e}")
            # Fallback
            for item in items:
                if item.text:
                    item.topics = self._extract_keywords(item.text)
        
        return items
    
    def _extract_keywords(self, text: str) -> list[str]:
        """Fallback keyword extraction"""
        keywords = []
        text_lower = text.lower()
        
        crisis_keywords = {
            "flood": "flooding",
            "fire": "fire",
            "earthquake": "earthquake",
            "violence": "violence",
            "accident": "accident",
            "explosion": "explosion",
            "storm": "storm",
            "pandemic": "health_crisis"
        }
        
        for keyword, topic in crisis_keywords.items():
            if keyword in text_lower:
                keywords.append(topic)
        
        return keywords if keywords else ["general"]
