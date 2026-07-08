import pytest

from app.schemas.workflow import WorkflowNode
from app.agents.executor import execute_agent


def _agent_node(config):
    return WorkflowNode(id="agent-1", type="agent", position={"x": 0, "y": 0}, config=config)


@pytest.mark.asyncio
async def test_execute_agent_with_mock_llm_uses_upstream_output():
    node = _agent_node({"name": "Analyzer", "prompt": "Analyze the input", "model": "mock-llm"})

    result = await execute_agent(node, {"output": "Hello HPE"})

    assert result["agent"] == "Analyzer"
    assert result["model_used"] == "mock-llm"
    assert result["used_fallback"] is False
    assert "Analyze the input" in result["output"]
    assert "Hello HPE" in result["output"]


@pytest.mark.asyncio
async def test_execute_agent_with_no_upstream_output_uses_bare_prompt():
    node = _agent_node({"name": "Analyzer", "prompt": "Analyze the input", "model": "mock-llm"})

    result = await execute_agent(node, {})

    assert "Input:" not in result["output"]
    assert "Analyze the input" in result["output"]


@pytest.mark.asyncio
async def test_execute_agent_missing_required_config_raises():
    node = _agent_node({"name": "Analyzer"})  # missing prompt & model
    with pytest.raises(Exception):
        await execute_agent(node, {})
