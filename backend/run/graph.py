from langgraph.graph import StateGraph, END
from run.runner import AGENTS
from run.state import ExecutionState


def execute_step(state: ExecutionState) -> ExecutionState:
    step = state["execution_plan"][state["step_index"]]
    agent = AGENTS[step["provider"]]

    output = agent.execute(
        prompt=step["prompt"],
        context=state["context"],
    )

    if output:
        state["context"].update(output)

    state["step_outputs"].append({
        "step": step["step"],
        "provider": step["provider"],
        "output": output,
    })

    state["trace"].append(step)
    state["step_index"] += 1
    return state


def should_continue(state: ExecutionState):
    return END if state["step_index"] >= len(state["execution_plan"]) else "execute_step"


def build_graph():
    g = StateGraph(ExecutionState)
    g.add_node("execute_step", execute_step)
    g.set_entry_point("execute_step")
    g.add_conditional_edges("execute_step", should_continue)
    return g.compile()
