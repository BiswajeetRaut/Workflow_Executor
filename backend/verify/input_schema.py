import re
from typing import Dict
from verify.models import Workflow

PROMPT_VAR = re.compile(r"\{\{(.*?)\}\}")

AGENT_INPUTS = {
    "terraform.get.outputs": {
        "workspace": "string"
    },
    "github.list.prs": {
        "repo": "string"
    },
    "confluence.get.page": {
        "page_id": "string"
    }
}


def resolve_input_schema(
    workflow: Workflow,
    execution_plan: Dict[str, dict]
) -> Dict[str, Dict[str, str]]:
    inputs: Dict[str, Dict[str, str]] = {}
    node_map = {n.id: n for n in workflow.nodes}

    # ---- prompt-derived inputs ----
    for meta in execution_plan.values():
        prompt_node = node_map[meta.prompt_node]
        text = prompt_node.data.get("text", "")

        for var in PROMPT_VAR.findall(text):
            inputs[var] = {
                "type": "string",
                "required": "true"
            }

    # ---- agent-required inputs ----
    for meta in execution_plan.values():
        agent = meta.agent
        for name, typ in AGENT_INPUTS.get(agent, {}).items():
            inputs.setdefault(name, {
                "type": typ,
                "required": "true"
            })

    return inputs
