# Tool-node SDK

A formal contract for tools an agent (or a `"tool"` workflow node) can call.

```python
@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict       # JSON Schema
    output_schema: dict      # JSON Schema
    execute: Callable[[dict], Awaitable[dict]]
    auth_config: dict        # e.g. {"type": "none"} or {"type": "api_key", "env_var": "..."}
```

`tool.run(data)` validates `data` against `input_schema`, calls `execute(data)`, validates the
result against `output_schema`, and returns it. Validation failures and execution failures both
raise `ToolError`.

## Adding a new tool

1. Write a module with an `async def _execute(data: dict) -> dict` and a
   `register_tool(Tool(...))` call at import time (`calculator.py` is the simplest example).
2. Import that module from `app/tools/__init__.py`.
3. If it should be reachable as a `"tool"` workflow node, no further wiring is needed —
   `executor.py` looks tools up by name from `node.config["tool_name"]` at run time.

## Example tools included here

| Tool | What it proves | Auth |
|---|---|---|
| `calculator` | Pure computation; parses with `ast`, **never `eval()`** | none |
| `web_search` | Deterministic stub for an "external API" shaped tool | none (stub) |
| `http_call` | Real async I/O (`httpx` GET) with a hard timeout | none (add `api_key` auth_config for a real target) |
| `code_exec` | Sandboxing pattern for code-execution tools | none |

## Sandboxing rule

**Any code-execution tool must run untrusted code via `subprocess`, never `exec()`/`eval()`
in-process.** An in-process `exec()` shares the parent's memory, file handles, and imported
modules — a bad snippet can read secrets or take down the API process. `code_exec.py`:

- runs snippets via `python -I` (isolated mode: ignores `PYTHONPATH`/`PYTHONHOME`, no user
  site-packages) in a separate process
- enforces a hard wall-clock timeout (`asyncio.wait_for` + kill)
- on POSIX, also caps address space and CPU time via `resource.setrlimit`

**Remaining risk, explicitly out of scope here:** this is process isolation, not a real sandbox.
The subprocess still has the parent OS user's filesystem and network access, and the POSIX
resource limits don't exist on Windows (no `resource` module) — there, only the timeout applies.
Do not point this tool at genuinely adversarial input in production; that needs a real sandbox
(container/VM/gVisor/Firecracker, no network, read-only filesystem).

## Tool node config (workflow JSON)

```json
{"id": "tool-1", "type": "tool", "config": {"tool_name": "calculator", "input": {"expression": "2 + 2"}}}
```

If `config.input` is omitted, the node forwards whatever it received from its upstream node.
