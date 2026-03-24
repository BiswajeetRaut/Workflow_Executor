from collections import defaultdict, deque
from typing import List, Dict
from verify.models import Workflow, Node


def topological_sort(workflow: Workflow) -> List[Node]:
    nodes = {n.id: n for n in workflow.nodes}
    graph = defaultdict(list)
    indegree = {nid: 0 for nid in nodes}

    for e in workflow.edges:
        graph[e.from_node].append(e.to_node)
        indegree[e.to_node] += 1

    queue = deque([n for n, d in indegree.items() if d == 0])
    ordered = []

    while queue:
        curr = queue.popleft()
        ordered.append(nodes[curr])
        for nxt in graph[curr]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    return ordered


def build_prompt_execution_pairs(workflow: Workflow) -> Dict[str, str]:
    parents = defaultdict(list)
    node_map = {n.id: n for n in workflow.nodes}

    for e in workflow.edges:
        parents[e.to_node].append(e.from_node)

    mapping = {}
    for node in workflow.nodes:
        if node.type != "prompt":
            prompt = next(
                node_map[p].data["text"]
                for p in parents[node.id]
                if node_map[p].type == "prompt"
            )
            mapping[node.id] = prompt

    return mapping


def plan_workflow(workflow: Workflow):
    ordered = topological_sort(workflow)
    prompts = build_prompt_execution_pairs(workflow)

    steps = []
    step_no = 1

    for node in ordered:
        if node.type == "prompt":
            continue

        kind = (
            "llm" if node.type == "llm"
            else "filter" if node.type == "filter"
            else "provider"
        )

        steps.append({
            "step": step_no,
            "kind": kind,
            "provider": node.type,
            "prompt": prompts[node.id],
        })

        step_no += 1

    return steps
