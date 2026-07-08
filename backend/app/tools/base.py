"""Formal Tool-node SDK.

Every tool is a ``Tool``: a name, a JSON Schema describing its input, a JSON
Schema describing its output, an async ``execute()`` function, and an
``auth_config`` describing what credentials (if any) it needs. Tools are
registered by name in ``TOOL_REGISTRY`` and looked up by the "tool" node
executor (``app.tools.executor``).

To add a new tool: write a module with a ``Tool(...)`` instance and call
``register_tool(...)`` at import time (see ``calculator.py`` for the
simplest example), then import that module from ``app/tools/__init__.py``.
"""

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

import jsonschema

ExecuteFn = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class ToolError(Exception):
    """Raised for input validation failures or tool execution failures."""


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    execute: ExecuteFn
    auth_config: dict[str, Any] = field(default_factory=lambda: {"type": "none"})

    def validate_input(self, data: dict[str, Any]) -> None:
        try:
            jsonschema.validate(instance=data, schema=self.input_schema)
        except jsonschema.ValidationError as exc:
            raise ToolError(f"Input for tool '{self.name}' failed validation: {exc.message}") from exc

    def validate_output(self, data: dict[str, Any]) -> None:
        try:
            jsonschema.validate(instance=data, schema=self.output_schema)
        except jsonschema.ValidationError as exc:
            raise ToolError(f"Output of tool '{self.name}' failed validation: {exc.message}") from exc

    async def run(self, data: dict[str, Any]) -> dict[str, Any]:
        self.validate_input(data)
        result = await self.execute(data)
        self.validate_output(result)
        return result


TOOL_REGISTRY: dict[str, Tool] = {}


def register_tool(tool: Tool) -> Tool:
    TOOL_REGISTRY[tool.name] = tool
    return tool


def get_tool(name: str) -> Tool:
    try:
        return TOOL_REGISTRY[name]
    except KeyError as exc:
        raise ToolError(f"No tool registered as '{name}'. Known tools: {sorted(TOOL_REGISTRY)}") from exc
