from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
from config import settings
from services.observability import observability_service
import uuid

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.claims_collection = "claim_embeddings"
        self.images_collection = "image_embeddings"
        
    async def ensure_collections(self):
        """Create collections if they don't exist"""
        collections = [c.name for c in self.client.get_collections().collections]
        
        # Claims collection (sentence embeddings)
        if self.claims_collection not in collections:
            self.client.create_collection(
                collection_name=self.claims_collection,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            observability_service.log_info(f"Created collection: {self.claims_collection}")
        
        # Images collection (CLIP embeddings)
        if self.images_collection not in collections:
            self.client.create_collection(
                collection_name=self.images_collection,
                vectors_config=VectorParams(size=512, distance=Distance.COSINE)
            )
            observability_service.log_info(f"Created collection: {self.images_collection}")
    
    async def add_claim_embedding(
        self,
        claim_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Add a claim embedding to Qdrant"""
        try:
            self.client.upsert(
                collection_name=self.claims_collection,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={"claim_id": claim_id, **metadata}
                    )
                ]
            )
            observability_service.log_info(f"Added embedding for claim: {claim_id}")
        except Exception as e:
            observability_service.log_error(f"Failed to add claim embedding: {e}")
    
    async def search_similar_claims(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar claims using vector similarity"""
        try:
            results = self.client.search(
                collection_name=self.claims_collection,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            return [
                {
                    "claim_id": hit.payload.get("claim_id"),
                    "score": hit.score,
                    "metadata": hit.payload
                }
                for hit in results
            ]
        except Exception as e:
            observability_service.log_error(f"Qdrant search failed: {e}")
            return []
    
    async def add_image_embedding(
        self,
        image_url: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ):
        """Add an image embedding"""
        try:
            self.client.upsert(
                collection_name=self.images_collection,
                points=[
                    PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={"image_url": image_url, **metadata}
                    )
                ]
            )
        except Exception as e:
            observability_service.log_error(f"Failed to add image embedding: {e}")
    
    async def search_similar_images(
        self,
        query_embedding: List[float],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find visually similar images"""
        try:
            results = self.client.search(
                collection_name=self.images_collection,
                query_vector=query_embedding,
                limit=limit
            )
            
            return [
                {
                    "image_url": hit.payload.get("image_url"),
                    "score": hit.score,
                    "metadata": hit.payload
                }
                for hit in results
            ]
        except Exception as e:
            observability_service.log_error(f"Image search failed: {e}")
            return []

# Singleton instance
qdrant_service = QdrantService()
