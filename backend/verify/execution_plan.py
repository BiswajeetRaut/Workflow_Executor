from typing import Dict
from verify.models import Workflow, ExecutionPlanEntry


def build_execution_plan(workflow: Workflow) -> Dict[str, ExecutionPlanEntry]:
    node_map = {n.id: n for n in workflow.nodes}
    plan: Dict[str, ExecutionPlanEntry] = {}

    for edge in workflow.edges:
        src = node_map[edge.from_node]
        tgt = node_map[edge.to_node]

        if tgt.type != "prompt" and src.type == "prompt":
            plan[tgt.id] = ExecutionPlanEntry(
                agent=tgt.type,
                prompt_node=src.id
            )

    return plan
