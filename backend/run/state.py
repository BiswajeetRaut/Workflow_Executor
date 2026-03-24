from typing import TypedDict, List, Dict, Any


class ExecutionState(TypedDict):
    step_index: int
    execution_plan: List[Dict[str, Any]]
    context: Dict[str, Any]
    step_outputs: List[Dict[str, Any]]
    trace: List[Dict[str, Any]]
