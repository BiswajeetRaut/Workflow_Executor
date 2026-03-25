from __future__ import annotations

from typing import Any, Dict

from run.agents.base import ProviderAgent


class FilterAgent(ProviderAgent):
    """Deterministic filter/selection agent.

    Prompt syntax (simple):
      - "keep:key1,key2" -> keep only those top-level context keys
      - otherwise passthrough
    """

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        normalized = prompt.strip().lower()
        if not normalized.startswith("keep:"):
            return {"filtered": context}

        raw_keys = prompt.split(":", 1)[1]
        keys = [key.strip() for key in raw_keys.split(",") if key.strip()]
        filtered = {key: context[key] for key in keys if key in context}
        return {"filtered": filtered}
