from typing import Any

from app.schemas.workflow import WorkflowDefinition, WorkflowNode
from app.engine.graph_parser import get_execution_order
from app.engine.state_manager import WorkflowState


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
            return None

        if len(incoming_outputs) == 1:
            return incoming_outputs[0]

        return incoming_outputs

    async def run(
        self,
        workflow: WorkflowDefinition,
    ) -> dict[str, Any]:
        execution_order = get_execution_order(workflow)

        for node_id in execution_order:
            node = self._get_node(workflow, node_id)
            node_input = self._get_input(workflow, node_id)

            result = {
                "node_id": node.id,
                "node_type": node.type,
                "input": node_input,
            }

            self.state.set_output(
                node.id,
                result,
            )

        return {
            "execution_order": execution_order,
            "outputs": self.state.get_all_outputs(),
        }