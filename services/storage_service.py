from typing import List, Optional
from schemas.item import NormalizedItem
from schemas.claim import Claim
from services.observability import observability_service
from services.opensearch_service import opensearch_service
# from services.iceberg_service import iceberg_service  # Assuming this exists
# from services.qdrant_service import qdrant_service    # Assuming this exists

class StorageService:
    """
    Unified storage service that writes to all data stores:
    - OpenSearch (Hot storage, search)
    - Iceberg (Cold storage, analytics)
    - Qdrant (Vector storage)
    - PostgreSQL (Relational metadata)
    """
    
    def __init__(self):
        pass

    async def save_item(self, item: NormalizedItem):
        """
        Save normalized item to all storage backends.
        """
        try:
            observability_service.log_info(f"Saving item {item.id} to storage.")
            
            # 1. OpenSearch (Search)
            await opensearch_service.index_item(item.dict())
            
            # 2. Iceberg (Data Lake) - Uncomment when Iceberg service is fully ready
            # await iceberg_service.write_item(item)
            
            # 3. Qdrant (Vectors) - If embeddings exist
            # if item.embedding:
            #     await qdrant_service.upsert_item(item)
            
            observability_service.log_info(f"Successfully saved item {item.id}")
            
        except Exception as e:
            observability_service.log_error(f"Failed to save item {item.id}: {e}")
            raise

    async def save_claims(self, claims: List[Claim]):
        """
        Save claims to all storage backends.
        """
        if not claims:
            return
            
        try:
            observability_service.log_info(f"Saving {len(claims)} claims to storage.")
            
            for claim in claims:
                # 1. OpenSearch
                await opensearch_service.index_claim(claim.dict())
                
                # 2. PostgreSQL (via SQLAlchemy) - Handled by separate DB session usually
                # but could be triggered here
                
            observability_service.log_info(f"Successfully saved {len(claims)} claims")
            
        except Exception as e:
            observability_service.log_error(f"Failed to save claims: {e}")
            raise

storage_service = StorageService()
