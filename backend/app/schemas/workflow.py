from typing import Any
from pydantic import BaseModel, Field


class Position(BaseModel):
    x: float
    y: float


class WorkflowNode(BaseModel):
    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    position: Position
    config: dict[str, Any] = {}


class WorkflowEdge(BaseModel):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)


class WorkflowDefinition(BaseModel):
    name: str = Field(min_length=1)
    nodes: list[WorkflowNode]
    edges: list[WorkflowEdge]