from typing import Any


class WorkflowState:
    def __init__(self):
        self.node_outputs: dict[str, Any] = {}

    def set_output(self, node_id: str, output: Any) -> None:
        self.node_outputs[node_id] = output

    def get_output(self, node_id: str) -> Any:
        return self.node_outputs.get(node_id)

    def get_all_outputs(self) -> dict[str, Any]:
        return self.node_outputs