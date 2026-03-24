import requests
from groq import Groq
from typing import Dict, Any
import os
from run.agents.base import ProviderAgent


class TerraformAgent(ProviderAgent):
    def __init__(self, token: str):
        self.base_url = "https://app.terraform.io/api/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/vnd.api+json",
        }
        self.llm = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        plan = self._decide_tool(prompt)

        if plan == "list_orgs":
            return self._list_organizations()

        if plan == "list_workspaces":
            return self._list_workspaces(context)

        raise ValueError(f"Terraform MCP cannot handle prompt: {prompt}")

    def _decide_tool(self, prompt: str) -> str:
        response = self.llm.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0,
            messages=[
                {"role": "system", "content": "Decide Terraform action. Reply ONLY with: list_orgs OR list_workspaces"},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    def _list_organizations(self) -> Dict[str, Any]:
        r = requests.get(f"{self.base_url}/organizations", headers=self.headers)
        r.raise_for_status()
        return {
            "organizations": [
                {
                    "org_id": o["id"],
                    "org_name": o["attributes"]["name"],
                }
                for o in r.json()["data"]
            ]
        }

    def _list_workspaces(self, context: Dict[str, Any]) -> Dict[str, Any]:
        workspaces = []
        for org in context.get("organizations", []):
            r = requests.get(
                f"{self.base_url}/organizations/{org['org_id']}/workspaces",
                headers=self.headers,
            )
            r.raise_for_status()
            for ws in r.json()["data"]:
                workspaces.append({
                    "workspace_id": ws["id"],
                    "workspace_name": ws["attributes"]["name"],
                    "org_id": org["org_id"],
                })
        return {"workspaces": workspaces}
