from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from run.agents.base import ProviderAgent


class GitHubAgent(ProviderAgent):
    """Simple GitHub tool agent for quick local testing.

    Supported prompts:
    - "list repos"
    - "list branches" (requires context["repo"] or first repo in context["repos"])
    """

    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        action = self._decide_action(prompt)

        if action == "list_repos":
            return self._list_repositories(context)
        if action == "list_branches":
            return self._list_branches(context)

        raise ValueError(f"GitHub agent cannot handle prompt: {prompt}")

    def _decide_action(self, prompt: str) -> str:
        normalized = prompt.lower()
        if "branch" in normalized:
            return "list_branches"
        return "list_repos"

    def _list_repositories(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Fast-path for offline testing (user can pass repos directly in run inputs)
        if context.get("repos"):
            return {"repos": context["repos"]}

        owner = context.get("github_owner") or context.get("owner")
        if not owner:
            return {"repos": []}

        url = f"{self.base_url}/users/{owner}/repos"
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()

        repos: List[Dict[str, Any]] = []
        for repo in response.json():
            repos.append(
                {
                    "repo": repo["name"],
                    "full_name": repo["full_name"],
                    "default_branch": repo.get("default_branch", "main"),
                }
            )

        return {"repos": repos}

    def _list_branches(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = context.get("github_owner") or context.get("owner")
        repo_name = context.get("repo")

        if not repo_name and context.get("repos"):
            repo_name = context["repos"][0].get("repo")

        if not owner or not repo_name:
            return {"branches": []}

        url = f"{self.base_url}/repos/{owner}/{repo_name}/branches"
        response = requests.get(url, headers=self.headers, timeout=15)
        response.raise_for_status()

        branches = [{"name": b["name"]} for b in response.json()]
        return {"repo": repo_name, "branches": branches}
