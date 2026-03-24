from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):

    @abstractmethod
    def execute(
        self,
        prompt: str,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass
