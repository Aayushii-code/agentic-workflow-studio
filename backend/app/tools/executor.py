"""Executor for the "tool" node type -- bridges the Tool-node SDK into the
node executor registry.

Config shape:
    {"tool_name": "calculator", "input": {"expression": "2 + 2"}}

If "input" is omitted, the node forwards whatever it received from its
upstream node (so a tool can consume an upstream agent's ``{"output": ...}``
directly, e.g. by mapping "input" from config at authoring time).
"""

from typing import Any

from app.schemas.workflow import WorkflowNode
from app.executors.registry import register_executor
from app.tools.base import get_tool


@register_executor("tool")
async def execute_tool(node: WorkflowNode, input_data: dict[str, Any]) -> dict[str, Any]:
    tool_name = node.config["tool_name"]
    tool_input = node.config.get("input", input_data)

    tool = get_tool(tool_name)
    result = await tool.run(tool_input)
    return {"output": result, "tool": tool_name}
