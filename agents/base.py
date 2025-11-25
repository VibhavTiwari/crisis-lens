from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        """Execute the agent's main logic."""
        pass

    def log(self, message: str):
        print(f"[{self.name}] {message}")
