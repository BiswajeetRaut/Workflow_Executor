from __future__ import annotations

from datetime import datetime
from time import perf_counter

from langgraph.graph import END, StateGraph

from run.runner import get_agent
from run.state import ExecutionState


def execute_step(state: ExecutionState) -> ExecutionState:
    step = state["execution_plan"][state["step_index"]]
    agent = get_agent(step["provider"])

    started_at = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
    start = perf_counter()
    output = agent.execute(
        prompt=step["prompt"],
        context=state["context"],
    )
    duration_ms = round((perf_counter() - start) * 1000, 2)

    if output:
        state["context"].update(output)

    state["step_outputs"].append(
        {
            "step": step["step"],
            "provider": step["provider"],
            "output": output,
            "duration_ms": duration_ms,
            "started_at": started_at,
        }
    )

    state["trace"].append(step)
    state["step_index"] += 1
    return state


def should_continue(state: ExecutionState):
    return END if state["step_index"] >= len(state["execution_plan"]) else "execute_step"


def build_graph():
    graph = StateGraph(ExecutionState)
    graph.add_node("execute_step", execute_step)
    graph.set_entry_point("execute_step")
    graph.add_conditional_edges("execute_step", should_continue)
    return graph.compile()
