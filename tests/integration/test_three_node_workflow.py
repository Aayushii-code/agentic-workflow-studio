"""Proves the executor registry can run the exact 3-node sample workflow
from the team's shared JSON contract, end to end, using mock-llm (no API
key). This is the primary compatibility proof for the rest of the team.
"""

import pytest

from app.schemas.workflow import WorkflowDefinition
from app.executors.runner import run_workflow

SAMPLE_WORKFLOW = {
    "name": "Demo Workflow",
    "nodes": [
        {"id": "input-1", "type": "input", "position": {"x": 100, "y": 100}, "config": {"value": "Hello HPE"}},
        {
            "id": "agent-1",
            "type": "agent",
            "position": {"x": 350, "y": 100},
            "config": {"name": "Analyzer", "prompt": "Analyze the input", "model": "mock-llm"},
        },
        {"id": "output-1", "type": "output", "position": {"x": 600, "y": 100}, "config": {}},
    ],
    "edges": [
        {"source": "input-1", "target": "agent-1"},
        {"source": "agent-1", "target": "output-1"},
    ],
}


@pytest.mark.asyncio
async def test_sample_workflow_end_to_end():
    workflow = WorkflowDefinition.model_validate(SAMPLE_WORKFLOW)

    results = await run_workflow(workflow)

    assert results["input-1"] == {"output": "Hello HPE"}

    assert results["agent-1"]["agent"] == "Analyzer"
    assert results["agent-1"]["model_used"] == "mock-llm"
    assert results["agent-1"]["used_fallback"] is False
    assert "Analyze the input" in results["agent-1"]["output"]
    assert "Hello HPE" in results["agent-1"]["output"]

    # the output node is a passthrough sink, so it must equal the agent's result exactly
    assert results["output-1"] == results["agent-1"]
