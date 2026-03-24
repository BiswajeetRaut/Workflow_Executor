from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal


class Node(BaseModel):
    id: str
    type: str
    data: Dict = Field(default_factory=dict)


class Edge(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")


class Workflow(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


class ExecutionStep(BaseModel):
    step: int
    kind: Literal["provider", "llm", "filter"]
    provider: str
    prompt: str


class ExecutionPlan(BaseModel):
    steps: List[ExecutionStep]


class VerifyRequest(BaseModel):
    workflow: Workflow


class VerifyResponse(BaseModel):
    status: Literal["VALID"]
    execution_plan: ExecutionPlan
