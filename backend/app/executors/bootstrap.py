"""Import this module once (e.g. at app startup, or at the top of a test) to
populate EXECUTOR_REGISTRY with every node type this codebase knows about.

Registration happens as a side effect of importing each node type's module,
so anything that walks the workflow graph and calls ``get_executor(type)``
just needs ``import app.executors.bootstrap`` before it starts -- it does
not need to know which package owns which node type.
"""

from app.executors import builtin  # noqa: F401  registers "input", "output"
from app import agents  # noqa: F401  registers "agent"
from app import tools  # noqa: F401  registers "tool"

from app.executors.registry import EXECUTOR_REGISTRY

__all__ = ["EXECUTOR_REGISTRY"]
