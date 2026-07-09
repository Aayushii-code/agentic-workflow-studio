import pytest

from app.schemas.workflow import WorkflowNode
from app.tools.executor import execute_tool


@pytest.mark.asyncio
async def test_tool_node_executes_calculator_with_explicit_input():
    node = WorkflowNode(
        id="tool-1",
        type="tool",
        position={"x": 0, "y": 0},
        config={"tool_name": "calculator", "input": {"expression": "3 * 4"}},
    )
    result = await execute_tool(node, {})
    assert result == {"output": {"result": 12}, "tool": "calculator"}


@pytest.mark.asyncio
async def test_tool_node_falls_back_to_upstream_input_data():
    node = WorkflowNode(
        id="tool-1",
        type="tool",
        position={"x": 0, "y": 0},
        config={"tool_name": "calculator"},
    )
    result = await execute_tool(node, {"expression": "5 + 5"})
    assert result == {"output": {"result": 10}, "tool": "calculator"}
