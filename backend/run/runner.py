import os
from run.agents.terraform import TerraformAgent
from run.agents.llm import LLMAgent


AGENTS = {
    "terraform": TerraformAgent(token=os.getenv("TERRAFORM_TOKEN")),
    "llm": LLMAgent(),
}
