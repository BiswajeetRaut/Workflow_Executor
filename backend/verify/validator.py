from collections import defaultdict, deque
from verify.models import Workflow, Node, Edge
from typing import List, Dict


class WorkflowValidationError(Exception):
    pass


def validate_workflow(workflow: Workflow):
    nodes = workflow.nodes
    edges = workflow.edges

    if not nodes:
        raise WorkflowValidationError("Workflow must contain at least one node")

    node_map = {n.id: n for n in nodes}

    # 1. Unique IDs
    if len(node_map) != len(nodes):
        raise WorkflowValidationError("Duplicate node IDs found")

    # 2. At least one prompt
    if not any(n.type == "prompt" for n in nodes):
        raise WorkflowValidationError("At least one prompt node is required")

    # 3. Edge references
    for e in edges:
        if e.from_node not in node_map or e.to_node not in node_map:
            raise WorkflowValidationError("Edge references unknown node")

    # 4. DAG validation
    _validate_dag(nodes, edges)

    # 5. Prompt-before-execution (STRICT)
    _validate_prompt_before_execution(nodes, edges, node_map)


def _validate_dag(nodes: List[Node], edges: List[Edge]):
    graph = defaultdict(list)
    indegree = {n.id: 0 for n in nodes}

    for e in edges:
        graph[e.from_node].append(e.to_node)
        indegree[e.to_node] += 1

    queue = deque([nid for nid, deg in indegree.items() if deg == 0])
    visited = 0

    while queue:
        curr = queue.popleft()
        visited += 1
        for nxt in graph[curr]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    if visited != len(nodes):
        raise WorkflowValidationError("Cycle detected in workflow")


def _validate_prompt_before_execution(
    nodes: List[Node],
    edges: List[Edge],
    node_map: Dict[str, Node],
):
    parents = defaultdict(list)
    for e in edges:
        parents[e.to_node].append(e.from_node)

    for node in nodes:
        if node.type == "prompt":
            continue

        incoming = parents.get(node.id, [])
        if not incoming:
            raise WorkflowValidationError(
                f"Execution node '{node.id}' has no incoming prompt"
            )

        if not any(node_map[p].type == "prompt" for p in incoming):
            raise WorkflowValidationError(
                f"Execution node '{node.id}' must have a prompt node immediately before it"
            )
