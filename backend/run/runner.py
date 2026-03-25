import os
from functools import lru_cache
from typing import Dict

from run.agents.base import ProviderAgent
from run.agents.confluence import ConfluenceAgent
from run.agents.filter import FilterAgent
from run.agents.github import GitHubAgent
from run.agents.llm import LLMAgent
from run.agents.terraform import TerraformAgent


@lru_cache(maxsize=1)
def build_agents() -> Dict[str, ProviderAgent]:
    """Lazily create agent instances once per process."""
    return {
        "terraform": TerraformAgent(token=os.getenv("TERRAFORM_TOKEN")),
        "github": GitHubAgent(token=os.getenv("GITHUB_TOKEN")),
        "confluence": ConfluenceAgent(),
        "filter": FilterAgent(),
        "llm": LLMAgent(),
    }


def get_agent(provider: str) -> ProviderAgent:
    agents = build_agents()
    if provider not in agents:
        raise ValueError(f"Unknown provider '{provider}'. Available: {', '.join(sorted(agents.keys()))}")
    return agents[provider]
