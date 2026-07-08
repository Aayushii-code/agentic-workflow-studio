from app.schemas.workflow import WorkflowDefinition


ALLOWED_NODE_TYPES = {
    "input",
    "agent",
    "tool",
    "output",
}


def validate_workflow(workflow: WorkflowDefinition) -> list[str]:
    errors = []

    node_ids = [node.id for node in workflow.nodes]

    # Check duplicate node IDs
    if len(node_ids) != len(set(node_ids)):
        errors.append("Duplicate node IDs are not allowed.")

    # Check invalid node types
    for node in workflow.nodes:
        if node.type not in ALLOWED_NODE_TYPES:
            errors.append(
                f"Invalid node type '{node.type}' for node '{node.id}'."
            )

    return errors