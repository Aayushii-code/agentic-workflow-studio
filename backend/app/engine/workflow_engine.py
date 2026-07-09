from typing import Any

import app.executors.bootstrap  # noqa: F401

from app.schemas.workflow import WorkflowDefinition, WorkflowNode
from app.engine.graph_parser import get_execution_order
from app.engine.state_manager import WorkflowState
from app.executors.registry import get_executor


class WorkflowEngine:
    def __init__(self):
        self.state = WorkflowState()

    def _get_node(
        self,
        workflow: WorkflowDefinition,
        node_id: str,
    ) -> WorkflowNode:
        for node in workflow.nodes:
            if node.id == node_id:
                return node

        raise ValueError(
            f"Node '{node_id}' not found."
        )

    def _get_input(
        self,
        workflow: WorkflowDefinition,
        node_id: str,
    ) -> Any:
        incoming_outputs = []

        for edge in workflow.edges:
            if edge.target == node_id:
                output = self.state.get_output(edge.source)
                incoming_outputs.append(output)

        if not incoming_outputs:
            return {}

        if len(incoming_outputs) == 1:
            return incoming_outputs[0]

        return {
            "inputs": incoming_outputs
        }

    async def run(
        self,
        workflow: WorkflowDefinition,
    ) -> dict[str, Any]:
        execution_order = get_execution_order(workflow)

        for node_id in execution_order:
            node = self._get_node(workflow, node_id)
            node_input = self._get_input(workflow, node_id)

            executor = get_executor(node.type)

            result = await executor(
                node,
                node_input,
            )

            self.state.set_output(
                node.id,
                result,
            )

        return {
            "execution_order": execution_order,
            "outputs": self.state.get_all_outputs(),
        }