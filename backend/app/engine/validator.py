from app.schemas.workflow import WorkflowDefinition


ALLOWED_NODE_TYPES = {
    "input",
    "agent",
    "tool",
    "output",
}

def has_cycle(workflow: WorkflowDefinition) -> bool:
    graph = {
        node.id: []
        for node in workflow.nodes
    }

    for edge in workflow.edges:
        if edge.source in graph and edge.target in graph:
            graph[edge.source].append(edge.target)

    visiting = set()
    visited = set()

    def dfs(node_id: str) -> bool:
        if node_id in visiting:
            return True

        if node_id in visited:
            return False

        visiting.add(node_id)

        for neighbour in graph[node_id]:
            if dfs(neighbour):
                return True

        visiting.remove(node_id)
        visited.add(node_id)

        return False

    for node_id in graph:
        if dfs(node_id):
            return True

    return False

def validate_workflow(workflow: WorkflowDefinition) -> list[str]:
    errors = []

    node_ids = [node.id for node in workflow.nodes]
    node_id_set = set(node_ids)

    # Check duplicate node IDs
    if len(node_ids) != len(node_id_set):
        errors.append("Duplicate node IDs are not allowed.")

    # Check invalid node types
    for node in workflow.nodes:
        if node.type not in ALLOWED_NODE_TYPES:
            errors.append(
                f"Invalid node type '{node.type}' for node '{node.id}'."
            )

    # Check edge references
    for edge in workflow.edges:
        if edge.source not in node_id_set:
            errors.append(
                f"Edge source '{edge.source}' does not exist."
            )

        if edge.target not in node_id_set:
            errors.append(
                f"Edge target '{edge.target}' does not exist."
            )

    
    # Check disconnected nodes
    connected_node_ids = set()

    for edge in workflow.edges:
        connected_node_ids.add(edge.source)
        connected_node_ids.add(edge.target)

    for node in workflow.nodes:
        if node.id not in connected_node_ids:
            errors.append(
                f"Node '{node.id}' is disconnected."
            )

    
        # Check workflow cycles
    if has_cycle(workflow):
        errors.append(
            "Workflow contains a cycle."
        )
    return errors