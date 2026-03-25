from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from run.graph import build_graph
from verify.models import VerifyRequest, VerifyResponse
from verify.service import build_execution_plan
from verify.validator import WorkflowValidationError

app = FastAPI(title="Workflow Executor", version="0.2.0")
graph = build_graph()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest):
    try:
        plan = build_execution_plan(req.workflow)
        return {"status": "VALID", "execution_plan": plan}
    except WorkflowValidationError as exc:
        raise HTTPException(400, str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/run")
def run_workflow(payload: dict):
    try:
        execution_plan = payload["execution_plan"]["steps"]
    except KeyError as exc:
        raise HTTPException(400, "execution_plan.steps is required") from exc

    state = {
        "step_index": 0,
        "execution_plan": execution_plan,
        "context": payload.get("inputs", {}),
        "step_outputs": [],
        "trace": [],
    }

    result = graph.invoke(state)

    return {
        "status": "SUCCESS",
        "steps": result["step_outputs"],
        "final_context": result["context"],
        "trace": result["trace"],
    }
