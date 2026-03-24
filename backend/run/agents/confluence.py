from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from run.agents.base import ProviderAgent


class ConfluenceAgent(ProviderAgent):
    """Confluence testing agent.

    It generates a deterministic page payload from workflow context so end-to-end
    graph execution can be tested without external credentials.
    """

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        page_title = context.get("page_title") or "Automation Report"
        space = context.get("confluence_space") or "ENG"
        timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        return {
            "confluence_page": {
                "title": page_title,
                "space": space,
                "summary": prompt,
                "generated_at": timestamp,
                "source_keys": sorted(context.keys()),
                "url": f"https://confluence.example/wiki/spaces/{space}/pages/automation-report",
            }
        }
