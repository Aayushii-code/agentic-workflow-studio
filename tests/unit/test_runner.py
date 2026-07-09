import pytest

from app.schemas.workflow import WorkflowDefinition
from app.executors.runner import WorkflowRunError, run_workflow


@pytest.mark.asyncio
async def test_cycle_raises():
    workflow = WorkflowDefinition.model_validate(
        {
            "name": "Cycle",
            "nodes": [
                {"id": "a", "type": "input", "position": {"x": 0, "y": 0}, "config": {"value": "x"}},
                {"id": "b", "type": "output", "position": {"x": 0, "y": 0}, "config": {}},
            ],
            "edges": [{"source": "a", "target": "b"}, {"source": "b", "target": "a"}],
        }
    )
    with pytest.raises(WorkflowRunError, match="cycle"):
        await run_workflow(workflow)


@pytest.mark.asyncio
async def test_multiple_predecessors_wrapped_in_inputs_list():
    workflow = WorkflowDefinition.model_validate(
        {
            "name": "Fan-in",
            "nodes": [
                {"id": "a", "type": "input", "position": {"x": 0, "y": 0}, "config": {"value": "A"}},
                {"id": "b", "type": "input", "position": {"x": 0, "y": 0}, "config": {"value": "B"}},
                {"id": "c", "type": "output", "position": {"x": 0, "y": 0}, "config": {}},
            ],
            "edges": [{"source": "a", "target": "c"}, {"source": "b", "target": "c"}],
        }
    )
    results = await run_workflow(workflow)
    assert results["c"] == {"inputs": [{"output": "A"}, {"output": "B"}]}
