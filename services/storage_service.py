from typing import List, Optional
from schemas.item import NormalizedItem
from schemas.claim import Claim
from services.observability import observability_service

class StorageService:
    def __init__(self):
        # In a real app, we'd initialize OpenSearch/Iceberg clients here
        pass

    async def save_item(self, item: NormalizedItem):
        """
        Save normalized item to 'Iceberg' (simulated) and 'OpenSearch' (simulated).
        """
        observability_service.log_info(f"Saving item {item.id} to storage.")
        # Simulate DB write
        pass

    async def save_claims(self, claims: List[Claim]):
        """
        Save claims to storage.
        """
        if not claims:
            return
            
        observability_service.log_info(f"Saving {len(claims)} claims to storage.")
        # Simulate DB write
        pass

storage_service = StorageService()
