from fastapi import APIRouter

from app.schemas.workflow import WorkflowDefinition
from app.engine.validator import validate_workflow
from app.engine.graph_parser import get_execution_order
from app.engine.workflow_engine import WorkflowEngine


router = APIRouter(
    prefix="/api/workflows",
    tags=["Workflows"],
)


@router.post("/validate")
async def validate_workflow_api(workflow: WorkflowDefinition):
    errors = validate_workflow(workflow)

    if errors:
        return {
            "valid": False,
            "errors": errors,
        }

    return {
        "valid": True,
        "workflow_name": workflow.name,
        "node_count": len(workflow.nodes),
        "edge_count": len(workflow.edges),
        "execution_order": get_execution_order(workflow),
        "errors": [],
    }


@router.post("/run")
async def run_workflow_api(workflow: WorkflowDefinition):
    errors = validate_workflow(workflow)

    if errors:
        return {
            "success": False,
            "errors": errors,
        }

    engine = WorkflowEngine()
    result = await engine.run(workflow)

    return {
        "success": True,
        "workflow_name": workflow.name,
        "result": result,
    }