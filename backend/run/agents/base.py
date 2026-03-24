# from abc import ABC
# from typing import Dict, Callable, Any


# class ProviderAgent(ABC):
#     def __init__(self):
#         self.handlers: Dict[str, Dict[str, Callable]] = {}

#     def register(self, resource: str, action: str, handler: Callable):
#         self.handlers.setdefault(resource, {})
#         self.handlers[resource][action] = handler

#     def execute(
#         self,
#         resource: str,
#         action: str,
#         prompt: str,
#         context: Dict[str, Any],
#     ) -> Dict[str, Any]:

#         if resource not in self.handlers:
#             raise ValueError(f"Resource '{resource}' not supported")

#         if action not in self.handlers[resource]:
#             raise ValueError(
#                 f"Action '{action}' not supported for resource '{resource}'"
#             )

#         return self.handlers[resource][action](
#             prompt=prompt,
#             context=context
#         )

from abc import ABC, abstractmethod
from typing import Dict, Any


class ProviderAgent(ABC):
    @abstractmethod
    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        pass
