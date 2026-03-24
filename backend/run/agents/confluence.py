from run.agents.base import ProviderAgent


class ConfluenceAgent(ProviderAgent):
    def __init__(self):
        super().__init__()
        self.register("page", "create", create_page)


def create_page(prompt: str, context: dict) -> dict:
    return {
        "page_url": "https://confluence.example/TFE_Workspace_Report"
    }
