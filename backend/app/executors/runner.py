"""A minimal topological runner over the executor registry.

This exists so node executors (agent/tool/input/output) can be proven
correct end-to-end without depending on the real DAG execution engine that
Aayushi owns in ``app.engine``. It performs a plain Kahn's-algorithm
topological sort and feeds each node the output of its single predecessor
(or ``{"inputs": [...]}`` if a node has multiple predecessors). It does not
attempt to handle cycles, conditional branching, or parallel execution --
those are the real engine's job.
"""

from collections import deque
from typing import Any

from app.schemas.workflow import WorkflowDefinition
from app.executors.registry import get_executor


class WorkflowRunError(Exception):
    pass


def _topological_order(workflow: WorkflowDefinition) -> list[str]:
    node_ids = [node.id for node in workflow.nodes]
    if len(node_ids) != len(set(node_ids)):
        raise WorkflowRunError("Duplicate node IDs are not allowed.")

    indegree = {node_id: 0 for node_id in node_ids}
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in workflow.edges:
        if edge.source not in indegree or edge.target not in indegree:
            raise WorkflowRunError(
                f"Edge references unknown node: {edge.source} -> {edge.target}"
            )
        adjacency[edge.source].append(edge.target)
        indegree[edge.target] += 1

    queue = deque(node_id for node_id, deg in indegree.items() if deg == 0)
    order: list[str] = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for neighbor in adjacency[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(node_ids):
        raise WorkflowRunError("Workflow graph contains a cycle.")

    return order


async def run_workflow(workflow: WorkflowDefinition) -> dict[str, dict[str, Any]]:
    """Execute every node in topological order, return each node's output by id."""
    nodes_by_id = {node.id: node for node in workflow.nodes}

    predecessors: dict[str, list[str]] = {node.id: [] for node in workflow.nodes}
    for edge in workflow.edges:
        predecessors[edge.target].append(edge.source)

    order = _topological_order(workflow)

    results: dict[str, dict[str, Any]] = {}
    for node_id in order:
        node = nodes_by_id[node_id]
        preds = predecessors[node_id]
        if not preds:
            input_data: dict[str, Any] = {}
        elif len(preds) == 1:
            input_data = results[preds[0]]
        else:
            input_data = {"inputs": [results[p] for p in preds]}

        executor = get_executor(node.type)
        results[node_id] = await executor(node, input_data)

    return results
