from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

import requests

from run.agents.base import ProviderAgent


class GitHubAgent(ProviderAgent):
    """GitHub provider agent with 10+ tools.

    Preferred deterministic prompt style:
      tool:<tool_name>

    Example:
      tool:list_repositories
      tool:list_pull_requests
    """

    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

        self.tools: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "list_repositories": self._list_repositories,
            "get_repository": self._get_repository,
            "list_branches": self._list_branches,
            "list_issues": self._list_issues,
            "list_pull_requests": self._list_pull_requests,
            "list_commits": self._list_commits,
            "list_tags": self._list_tags,
            "list_workflows": self._list_workflows,
            "list_releases": self._list_releases,
            "get_file_content": self._get_file_content,
        }

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = self._decide_tool(prompt)
        handler = self.tools.get(tool_name)
        if not handler:
            raise ValueError(
                f"GitHub agent tool '{tool_name}' is not available. "
                f"Available tools: {', '.join(sorted(self.tools.keys()))}"
            )
        result = handler(context)
        return {"github": {"tool": tool_name, "result": result}}

    def _decide_tool(self, prompt: str) -> str:
        normalized = prompt.strip().lower()

        if normalized.startswith("tool:"):
            requested = normalized.split(":", 1)[1].strip().replace("-", "_")
            if requested in self.tools:
                return requested

        keyword_map = {
            "repo details": "get_repository",
            "repository": "list_repositories",
            "branch": "list_branches",
            "issue": "list_issues",
            "pull": "list_pull_requests",
            "commit": "list_commits",
            "tag": "list_tags",
            "workflow": "list_workflows",
            "release": "list_releases",
            "file": "get_file_content",
        }
        for keyword, tool in keyword_map.items():
            if keyword in normalized:
                return tool

        return "list_repositories"

    def _owner(self, context: Dict[str, Any]) -> Optional[str]:
        return context.get("github_owner") or context.get("owner")

    def _repo(self, context: Dict[str, Any]) -> Optional[str]:
        repo = context.get("repo") or context.get("repository")
        if repo:
            return repo

        repos = context.get("repos")
        if repos and isinstance(repos, list) and repos[0].get("repo"):
            return repos[0]["repo"]

        github_result = context.get("github", {}).get("result", {})
        repos = github_result.get("repos")
        if repos and isinstance(repos, list) and repos[0].get("repo"):
            return repos[0]["repo"]
        return None

    def _get(self, path: str, *, params: Optional[Dict[str, Any]] = None) -> Any:
        response = requests.get(
            f"{self.base_url}{path}",
            headers=self.headers,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def _list_repositories(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if context.get("repos"):
            return {"repos": context["repos"]}

        owner = self._owner(context)
        if not owner:
            return {"repos": [], "note": "github_owner/owner missing in context"}

        payload = self._get(f"/users/{owner}/repos")
        repos: List[Dict[str, Any]] = []
        for repo in payload:
            repos.append(
                {
                    "repo": repo["name"],
                    "full_name": repo["full_name"],
                    "default_branch": repo.get("default_branch", "main"),
                    "private": repo.get("private", False),
                }
            )
        return {"repos": repos}

    def _get_repository(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        if not owner or not repo:
            return {"repository": None, "note": "owner/repo missing in context"}

        data = self._get(f"/repos/{owner}/{repo}")
        return {
            "repository": {
                "full_name": data.get("full_name"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "open_issues": data.get("open_issues_count"),
            }
        }

    def _list_branches(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        if not owner or not repo:
            return {"branches": [], "note": "owner/repo missing in context"}

        payload = self._get(f"/repos/{owner}/{repo}/branches")
        return {"repo": repo, "branches": [{"name": branch["name"]} for branch in payload]}

    def _list_issues(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        if not owner or not repo:
            return {"issues": [], "note": "owner/repo missing in context"}

        payload = self._get(f"/repos/{owner}/{repo}/issues", params={"state": "open", "per_page": 20})
        issues = []
        for issue in payload:
            if "pull_request" in issue:
                continue
            issues.append({"number": issue.get("number"), "title": issue.get("title"), "state": issue.get("state")})
        return {"repo": repo, "issues": issues}

    def _list_pull_requests(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        if not owner or not repo:
            return {"pull_requests": [], "note": "owner/repo missing in context"}

        payload = self._get(f"/repos/{owner}/{repo}/pulls", params={"state": "open", "per_page": 20})
        return {
            "repo": repo,
            "pull_requests": [
                {"number": pr.get("number"), "title": pr.get("title"), "state": pr.get("state")}
                for pr in payload
            ],
        }

    def _list_commits(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        if not owner or not repo:
            return {"commits": [], "note": "owner/repo missing in context"}

        payload = self._get(f"/repos/{owner}/{repo}/commits", params={"per_page": 20})
        return {
            "repo": repo,
            "commits": [
                {
                    "sha": commit.get("sha"),
                    "message": commit.get("commit", {}).get("message"),
                    "author": commit.get("commit", {}).get("author", {}).get("name"),
                }
                for commit in payload
            ],
        }

    def _list_tags(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        if not owner or not repo:
            return {"tags": [], "note": "owner/repo missing in context"}

        payload = self._get(f"/repos/{owner}/{repo}/tags")
        return {"repo": repo, "tags": [{"name": tag.get("name"), "sha": tag.get("commit", {}).get("sha")} for tag in payload]}

    def _list_workflows(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        if not owner or not repo:
            return {"workflows": [], "note": "owner/repo missing in context"}

        payload = self._get(f"/repos/{owner}/{repo}/actions/workflows")
        workflows = payload.get("workflows", []) if isinstance(payload, dict) else []
        return {
            "repo": repo,
            "workflows": [
                {"id": workflow.get("id"), "name": workflow.get("name"), "state": workflow.get("state")}
                for workflow in workflows
            ],
        }

    def _list_releases(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        if not owner or not repo:
            return {"releases": [], "note": "owner/repo missing in context"}

        payload = self._get(f"/repos/{owner}/{repo}/releases")
        return {
            "repo": repo,
            "releases": [
                {
                    "id": release.get("id"),
                    "tag_name": release.get("tag_name"),
                    "name": release.get("name"),
                    "draft": release.get("draft"),
                }
                for release in payload
            ],
        }

    def _get_file_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        owner = self._owner(context)
        repo = self._repo(context)
        path = context.get("file_path") or "README.md"
        if not owner or not repo:
            return {"file": None, "note": "owner/repo missing in context"}

        payload = self._get(f"/repos/{owner}/{repo}/contents/{path}")
        return {
            "file": {
                "path": payload.get("path"),
                "size": payload.get("size"),
                "encoding": payload.get("encoding"),
                "sha": payload.get("sha"),
            }
        }
