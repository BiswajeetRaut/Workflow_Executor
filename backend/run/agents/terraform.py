from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, Optional

import requests
from groq import Groq

from run.agents.base import ProviderAgent


class TerraformAgent(ProviderAgent):
    """Terraform provider agent with a broader toolset.

    Preferred prompt style for deterministic routing:
      tool:<tool_name>

    Example:
      tool:list_organizations
      tool:get_workspace_variables
    """

    def __init__(self, token: Optional[str]):
        self.base_url = "https://app.terraform.io/api/v2"
        self.headers = {
            "Authorization": f"Bearer {token}" if token else "",
            "Content-Type": "application/vnd.api+json",
        }
        self.llm = Groq()
        self.tools: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "list_organizations": self._list_organizations,
            "list_workspaces": self._list_workspaces,
            "get_workspace": self._get_workspace,
            "list_workspace_variables": self._list_workspace_variables,
            "list_projects": self._list_projects,
            "list_teams": self._list_teams,
            "list_runs": self._list_runs,
            "list_state_versions": self._list_state_versions,
            "list_variable_sets": self._list_variable_sets,
            "list_policies": self._list_policies,
        }

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = self._decide_tool(prompt)
        handler = self.tools.get(tool_name)
        if not handler:
            raise ValueError(
                f"Terraform agent tool '{tool_name}' is not available. "
                f"Available tools: {', '.join(sorted(self.tools.keys()))}"
            )
        result = handler(context)
        return {"terraform": {"tool": tool_name, "result": result}}

    def _decide_tool(self, prompt: str) -> str:
        normalized = prompt.strip().lower()
        if normalized.startswith("tool:"):
            requested = normalized.split(":", 1)[1].strip().replace("-", "_")
            if requested in self.tools:
                return requested

        keyword_map = {
            "organization": "list_organizations",
            "workspace variables": "list_workspace_variables",
            "workspace": "list_workspaces",
            "project": "list_projects",
            "team": "list_teams",
            "run": "list_runs",
            "state": "list_state_versions",
            "variable set": "list_variable_sets",
            "policy": "list_policies",
        }
        for keyword, tool in keyword_map.items():
            if keyword in normalized:
                return tool

        response = self.llm.chat.completions.create(
            model="openai/gpt-oss-120b",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Choose exactly one Terraform tool name from this list: "
                        + ", ".join(sorted(self.tools.keys()))
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        decision = response.choices[0].message.content.strip().lower().replace("-", "_")
        return decision if decision in self.tools else "list_organizations"

    def _get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = requests.get(
            f"{self.base_url}{path}",
            headers=self.headers,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def _first_organization_name(self, context: Dict[str, Any]) -> Optional[str]:
        organizations = context.get("organizations") or context.get("terraform", {}).get("result", {}).get("organizations")
        if organizations:
            return organizations[0].get("org_name")
        return context.get("organization_name")

    def _first_workspace_id(self, context: Dict[str, Any]) -> Optional[str]:
        workspaces = context.get("workspaces") or context.get("terraform", {}).get("result", {}).get("workspaces")
        if workspaces:
            return workspaces[0].get("workspace_id")
        return context.get("workspace_id")

    def _list_organizations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._get("/organizations")
        return {
            "organizations": [
                {
                    "org_id": org["id"],
                    "org_name": org["attributes"]["name"],
                }
                for org in payload.get("data", [])
            ]
        }

    def _fetch_org_workspaces(self, org_name: str) -> list[Dict[str, Any]]:
        payload = self._get(f"/organizations/{org_name}/workspaces")
        return [
            {
                "workspace_id": workspace["id"],
                "workspace_name": workspace["attributes"]["name"],
                "org_name": org_name,
            }
            for workspace in payload.get("data", [])
        ]

    def _list_workspaces(self, context: Dict[str, Any]) -> Dict[str, Any]:
        organizations = context.get("organizations") or []
        if not organizations:
            org_name = context.get("organization_name")
            if org_name:
                organizations = [{"org_name": org_name}]

        if not organizations:
            return {"workspaces": []}

        workspaces: list[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=min(8, len(organizations))) as executor:
            futures = {
                executor.submit(self._fetch_org_workspaces, org["org_name"]): org["org_name"]
                for org in organizations
            }
            for future in as_completed(futures):
                workspaces.extend(future.result())

        return {"workspaces": workspaces}

    def _get_workspace(self, context: Dict[str, Any]) -> Dict[str, Any]:
        workspace_id = self._first_workspace_id(context)
        if not workspace_id:
            return {"workspace": None, "note": "workspace_id missing in context"}

        payload = self._get(f"/workspaces/{workspace_id}")
        data = payload.get("data", {})
        return {
            "workspace": {
                "workspace_id": data.get("id"),
                "name": data.get("attributes", {}).get("name"),
                "terraform_version": data.get("attributes", {}).get("terraform-version"),
                "locked": data.get("attributes", {}).get("locked"),
            }
        }

    def _list_workspace_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        workspace_id = self._first_workspace_id(context)
        if not workspace_id:
            return {"variables": [], "note": "workspace_id missing in context"}

        payload = self._get(f"/workspaces/{workspace_id}/vars")
        return {
            "variables": [
                {
                    "id": var.get("id"),
                    "key": var.get("attributes", {}).get("key"),
                    "category": var.get("attributes", {}).get("category"),
                    "sensitive": var.get("attributes", {}).get("sensitive"),
                }
                for var in payload.get("data", [])
            ]
        }

    def _list_projects(self, context: Dict[str, Any]) -> Dict[str, Any]:
        org_name = self._first_organization_name(context)
        if not org_name:
            return {"projects": [], "note": "organization_name missing in context"}

        payload = self._get(f"/organizations/{org_name}/projects")
        return {
            "projects": [
                {
                    "id": project.get("id"),
                    "name": project.get("attributes", {}).get("name"),
                }
                for project in payload.get("data", [])
            ]
        }

    def _list_teams(self, context: Dict[str, Any]) -> Dict[str, Any]:
        org_name = self._first_organization_name(context)
        if not org_name:
            return {"teams": [], "note": "organization_name missing in context"}

        payload = self._get(f"/organizations/{org_name}/teams")
        return {
            "teams": [
                {
                    "id": team.get("id"),
                    "name": team.get("attributes", {}).get("name"),
                }
                for team in payload.get("data", [])
            ]
        }

    def _list_runs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        workspace_id = self._first_workspace_id(context)
        if not workspace_id:
            return {"runs": [], "note": "workspace_id missing in context"}

        payload = self._get("/runs", params={"filter[workspace][id]": workspace_id})
        return {
            "runs": [
                {
                    "id": run.get("id"),
                    "status": run.get("attributes", {}).get("status"),
                    "message": run.get("attributes", {}).get("message"),
                }
                for run in payload.get("data", [])
            ]
        }

    def _list_state_versions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        workspace_id = self._first_workspace_id(context)
        if not workspace_id:
            return {"state_versions": [], "note": "workspace_id missing in context"}

        payload = self._get(f"/workspaces/{workspace_id}/state-versions")
        return {
            "state_versions": [
                {
                    "id": state.get("id"),
                    "serial": state.get("attributes", {}).get("serial"),
                    "created_at": state.get("attributes", {}).get("created-at"),
                }
                for state in payload.get("data", [])
            ]
        }

    def _list_variable_sets(self, context: Dict[str, Any]) -> Dict[str, Any]:
        org_name = self._first_organization_name(context)
        if not org_name:
            return {"variable_sets": [], "note": "organization_name missing in context"}

        payload = self._get(f"/organizations/{org_name}/varsets")
        return {
            "variable_sets": [
                {
                    "id": varset.get("id"),
                    "name": varset.get("attributes", {}).get("name"),
                }
                for varset in payload.get("data", [])
            ]
        }

    def _list_policies(self, context: Dict[str, Any]) -> Dict[str, Any]:
        org_name = self._first_organization_name(context)
        if not org_name:
            return {"policies": [], "note": "organization_name missing in context"}

        payload = self._get(f"/organizations/{org_name}/policies")
        return {
            "policies": [
                {
                    "id": policy.get("id"),
                    "name": policy.get("attributes", {}).get("name"),
                    "kind": policy.get("attributes", {}).get("kind"),
                }
                for policy in payload.get("data", [])
            ]
        }
