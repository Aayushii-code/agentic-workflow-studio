"""Calculator tool: evaluates a basic arithmetic expression safely.

Uses Python's ``ast`` module to parse the expression and walks the resulting
tree, allowing only numeric literals and +, -, *, /, //, %, ** operators.
Never calls ``eval()``/``exec()`` -- there is no way to reach arbitrary code
execution through this tool.
"""

import ast
import operator
from typing import Any

from app.tools.base import Tool, ToolError, register_tool

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise ToolError(f"Unsupported constant in expression: {node.value!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_eval_node(node.operand))
    raise ToolError(f"Unsupported expression element: {ast.dump(node)}")


def _safe_eval(expression: str) -> float:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ToolError(f"Could not parse expression: {exc}") from exc
    try:
        return _eval_node(tree.body)
    except ZeroDivisionError as exc:
        raise ToolError("Division by zero.") from exc


async def _execute(data: dict[str, Any]) -> dict[str, Any]:
    result = _safe_eval(data["expression"])
    return {"result": result}


calculator_tool = register_tool(
    Tool(
        name="calculator",
        description="Evaluates a basic arithmetic expression (+, -, *, /, //, %, **).",
        input_schema={
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {"result": {"type": "number"}},
            "required": ["result"],
        },
        execute=_execute,
        auth_config={"type": "none"},
    )
)
