from verify.models import ExecutionPlan, Workflow
from verify.validator import validate_workflow
from verify.planner import plan_workflow


def build_execution_plan(workflow: Workflow) -> ExecutionPlan:
    validate_workflow(workflow)
    steps = plan_workflow(workflow)
    return ExecutionPlan(steps=steps)
