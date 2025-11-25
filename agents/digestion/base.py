from abc import abstractmethod
from typing import Any
from agents.base import BaseAgent
from schemas.item import NormalizedItem

class DigestionAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)

    @abstractmethod
    async def process(self, item: NormalizedItem) -> NormalizedItem:
        """Process a normalized item and return it (potentially modified/enriched)."""
        pass

    async def run(self, input_data: Any) -> Any:
        if isinstance(input_data, NormalizedItem):
            return await self.process(input_data)
        else:
            self.log(f"Invalid input type: {type(input_data)}")
            return input_data
