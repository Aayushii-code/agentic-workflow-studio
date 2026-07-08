from fastapi import APIRouter

from app.schemas.workflow import WorkflowDefinition
from app.engine.validator import validate_workflow


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
        "errors": [],
    }