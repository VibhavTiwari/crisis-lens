from abc import abstractmethod
from typing import List
from agents.base import BaseAgent
from schemas.item import RawItem

class IngestionAgent(BaseAgent):
    def __init__(self, name: str, source_name: str):
        super().__init__(name)
        self.source_name = source_name

    @abstractmethod
    async def fetch(self) -> List[RawItem]:
        """Fetch items from the source."""
        pass

    async def run(self, input_data: Any = None) -> List[RawItem]:
        self.log(f"Starting ingestion from {self.source_name}...")
        items = await self.fetch()
        self.log(f"Fetched {len(items)} items from {self.source_name}.")
        return items
