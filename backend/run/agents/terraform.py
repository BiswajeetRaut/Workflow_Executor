from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional

import requests
from groq import Groq

from run.agents.base import ProviderAgent


class TerraformAgent(ProviderAgent):
    def __init__(self, token: Optional[str]):
        self.base_url = "https://app.terraform.io/api/v2"
        self.headers = {
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/vnd.api+json",
        }
        self.llm = Groq()

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        plan = self._decide_tool(prompt)

        if plan == "list_orgs":
            return self._list_organizations()
        if plan == "list_workspaces":
            return self._list_workspaces(context)

        raise ValueError(f"Terraform agent cannot handle prompt: {prompt}")

    def _decide_tool(self, prompt: str) -> str:
        normalized = prompt.lower()
        if "workspace" in normalized:
            return "list_workspaces"
        if "org" in normalized or "organization" in normalized:
            return "list_orgs"

        # fallback only when keyword matching is inconclusive
        response = self.llm.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "Decide Terraform action. Reply ONLY with: list_orgs OR list_workspaces",
                },
                {"role": "user", "content": prompt},
            ],
        )
        decision = response.choices[0].message.content.strip()
        return decision if decision in {"list_orgs", "list_workspaces"} else "list_orgs"

    def _list_organizations(self) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}/organizations",
            headers=self.headers,
            timeout=20,
        )
        response.raise_for_status()
        return {
            "organizations": [
                {
                    "org_id": org["id"],
                    "org_name": org["attributes"]["name"],
                }
                for org in response.json().get("data", [])
            ]
        }

    def _fetch_org_workspaces(self, org_id: str) -> list[Dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/organizations/{org_id}/workspaces",
            headers=self.headers,
            timeout=20,
        )
        response.raise_for_status()
        workspaces: list[Dict[str, Any]] = []
        for workspace in response.json().get("data", []):
            workspaces.append(
                {
                    "workspace_id": workspace["id"],
                    "workspace_name": workspace["attributes"]["name"],
                    "org_id": org_id,
                }
            )
        return workspaces

    def _list_workspaces(self, context: Dict[str, Any]) -> Dict[str, Any]:
        orgs = context.get("organizations", [])
        if not orgs:
            return {"workspaces": []}

        workspaces: list[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=min(8, len(orgs))) as executor:
            futures = {
                executor.submit(self._fetch_org_workspaces, org["org_id"]): org["org_id"]
                for org in orgs
            }
            for future in as_completed(futures):
                workspaces.extend(future.result())

        return {"workspaces": workspaces}
