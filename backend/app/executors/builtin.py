"""Executors for the two non-agent, non-tool node types in the shared contract.

Importing this module registers "input" and "output" into EXECUTOR_REGISTRY.
"""

from typing import Any

from app.schemas.workflow import WorkflowNode
from app.executors.registry import register_executor


@register_executor("input")
async def execute_input(node: WorkflowNode, input_data: dict[str, Any]) -> dict[str, Any]:
    """An input node has no upstream data; it seeds the graph from its config."""
    return {"output": node.config.get("value")}


@register_executor("output")
async def execute_output(node: WorkflowNode, input_data: dict[str, Any]) -> dict[str, Any]:
    """An output node is a passthrough sink; it forwards whatever it receives."""
    return dict(input_data)
