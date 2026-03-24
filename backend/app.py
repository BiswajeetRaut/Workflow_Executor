from fastapi import FastAPI, HTTPException
from verify.models import VerifyRequest, VerifyResponse
from verify.validator import validate_workflow, WorkflowValidationError
from verify.service import build_execution_plan
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

import os
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))

@app.post("/verify", response_model=VerifyResponse)
def verify(req: VerifyRequest):
    try:
        plan = build_execution_plan(req.workflow)
        return {"status": "VALID", "execution_plan": plan}
    except Exception as e:
        raise HTTPException(400, str(e))



from run.graph import build_graph


graph = build_graph()


@app.post("/run")
def run_workflow(payload: dict):
    state = {
        "step_index": 0,
        "execution_plan": payload["execution_plan"]["steps"],
        "context": payload.get("inputs", {}),
        "step_outputs": [],
        "trace": [],
    }

    result = graph.invoke(state)

    return {
        "status": "SUCCESS",
        "steps": result["step_outputs"],      # 👈 step-by-step outputs
        "final_context": result["context"],   # 👈 aggregated result
        "trace": result["trace"],              # 👈 execution trace
    }
