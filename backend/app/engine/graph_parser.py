from collections import deque

from app.schemas.workflow import WorkflowDefinition


def get_execution_order(workflow: WorkflowDefinition) -> list[str]:
    graph = {
        node.id: []
        for node in workflow.nodes
    }

    indegree = {
        node.id: 0
        for node in workflow.nodes
    }

    for edge in workflow.edges:
        graph[edge.source].append(edge.target)
        indegree[edge.target] += 1

    queue = deque(
        node_id
        for node_id, degree in indegree.items()
        if degree == 0
    )

    execution_order = []

    while queue:
        node_id = queue.popleft()
        execution_order.append(node_id)

        for neighbour in graph[node_id]:
            indegree[neighbour] -= 1

            if indegree[neighbour] == 0:
                queue.append(neighbour)

    return execution_order