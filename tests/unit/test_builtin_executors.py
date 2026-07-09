import pytest

from app.schemas.workflow import WorkflowNode
from app.executors.builtin import execute_input, execute_output


def _node(node_id, node_type, config):
    return WorkflowNode(id=node_id, type=node_type, position={"x": 0, "y": 0}, config=config)


@pytest.mark.asyncio
async def test_execute_input_reads_value_from_config():
    node = _node("in-1", "input", {"value": "Hello HPE"})
    result = await execute_input(node, {})
    assert result == {"output": "Hello HPE"}


@pytest.mark.asyncio
async def test_execute_output_passes_through_input_data():
    node = _node("out-1", "output", {})
    upstream = {"output": "some text", "agent": "Analyzer"}
    result = await execute_output(node, upstream)
    assert result == upstream
    assert result is not upstream  # defensive copy, not the same dict
