"""Sandboxed(-ish) Python code execution tool.

SANDBOXING RULE (see tools/README.md): any code-execution tool MUST run
untrusted code via ``subprocess``, never ``exec()``/``eval()`` in-process --
an in-process exec shares the parent's memory, filesystem handles, and
imported modules, so a malicious or buggy snippet could read secrets,
corrupt state, or take down the whole API process. This tool:

  - runs the snippet in a separate ``python -I`` (isolated mode) process,
    which ignores PYTHONPATH/PYTHONHOME and disables user site-packages
  - enforces a hard wall-clock timeout via ``asyncio.wait_for`` + kill
  - on POSIX, additionally caps address space and CPU time via
    ``resource.setrlimit`` in a ``preexec_fn``

REMAINING RISK (explicitly not solved here, out of scope for this task):
this is process isolation, not a real sandbox. The subprocess still has
full filesystem and network access with the same OS-user permissions as the
parent process, and the POSIX resource limits are unavailable on Windows
(no ``resource`` module) -- on Windows this tool relies on the timeout
alone. Do not point this at genuinely untrusted/adversarial input in
production; that requires a real sandbox (container/VM/gVisor/Firecracker
with no network and a read-only filesystem).
"""

import asyncio
import sys
from typing import Any

from app.tools.base import Tool, ToolError, register_tool

_TIMEOUT_SECONDS = 5.0
_MAX_OUTPUT_CHARS = 4000
_MEMORY_LIMIT_BYTES = 128 * 1024 * 1024
_CPU_LIMIT_SECONDS = 5


def _limit_resources() -> None:  # pragma: no cover - exercised only on POSIX
    import resource

    resource.setrlimit(resource.RLIMIT_AS, (_MEMORY_LIMIT_BYTES, _MEMORY_LIMIT_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (_CPU_LIMIT_SECONDS, _CPU_LIMIT_SECONDS))


async def _execute(data: dict[str, Any]) -> dict[str, Any]:
    code = data["code"]

    subprocess_kwargs: dict[str, Any] = {}
    if sys.platform != "win32":
        subprocess_kwargs["preexec_fn"] = _limit_resources

    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-I",
        "-c",
        code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        **subprocess_kwargs,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=_TIMEOUT_SECONDS)
    except asyncio.TimeoutError as exc:
        proc.kill()
        await proc.wait()
        raise ToolError(f"code_exec timed out after {_TIMEOUT_SECONDS}s") from exc

    return {
        "stdout": stdout.decode(errors="replace")[:_MAX_OUTPUT_CHARS],
        "stderr": stderr.decode(errors="replace")[:_MAX_OUTPUT_CHARS],
        "exit_code": proc.returncode if proc.returncode is not None else -1,
    }


code_exec_tool = register_tool(
    Tool(
        name="code_exec",
        description=(
            "Executes a short Python snippet in an isolated subprocess with a timeout. "
            "See module docstring for sandboxing guarantees and remaining risk."
        ),
        input_schema={
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "stdout": {"type": "string"},
                "stderr": {"type": "string"},
                "exit_code": {"type": "integer"},
            },
            "required": ["stdout", "stderr", "exit_code"],
        },
        execute=_execute,
        auth_config={"type": "none"},
    )
)
