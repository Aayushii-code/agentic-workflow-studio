"""Node-type executor registry.

Maps a workflow node's ``type`` string to an async ``execute(node, input_data)``
function. This is the extension point for adding new node types: write a
function, decorate it with ``@register_executor("your-type")`` in a module
that gets imported (see ``builtin.py``, ``app.agents.executor``,
``app.tools.executor``), and it is immediately usable by anything that walks
the workflow graph and dispatches through ``get_executor``.

This registry is intentionally separate from ``app.engine`` (the DAG
compiler/execution engine). This module only answers "how do I run a single
node of type X"; graph traversal, ordering, and parallelism are the engine's
concern.
"""

from typing import Any, Awaitable, Callable

from app.schemas.workflow import WorkflowNode

ExecuteFn = Callable[[WorkflowNode, dict[str, Any]], Awaitable[dict[str, Any]]]

EXECUTOR_REGISTRY: dict[str, ExecuteFn] = {}


def register_executor(node_type: str) -> Callable[[ExecuteFn], ExecuteFn]:
    """Decorator that registers an executor function for a node type."""

    def decorator(fn: ExecuteFn) -> ExecuteFn:
        EXECUTOR_REGISTRY[node_type] = fn
        return fn

    return decorator


def get_executor(node_type: str) -> ExecuteFn:
    try:
        return EXECUTOR_REGISTRY[node_type]
    except KeyError as exc:
        raise ValueError(
            f"No executor registered for node type '{node_type}'. "
            f"Known types: {sorted(EXECUTOR_REGISTRY)}"
        ) from exc
