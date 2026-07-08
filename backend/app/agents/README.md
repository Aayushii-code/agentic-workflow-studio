# Agent node

Implements the `"agent"` node type from the shared workflow JSON contract: an LLM with a role,
system prompt, memory scope, and (optionally) bound tools.

## Config shape (`AgentConfig` in `schemas.py`)

```json
{
  "name": "Analyzer",
  "prompt": "Analyze the input",
  "model": "mock-llm",
  "system_prompt": null,
  "memory_scope": "none",
  "tools": [],
  "fallback_model": null
}
```

Only `name`, `prompt`, and `model` are required — that matches the minimal sample in the shared
contract. The rest have defaults so existing sample workflows keep working unchanged.

## Execution (`executor.py`)

`execute_agent(node, input_data)`:

1. Parses `node.config` into `AgentConfig` (raises if `name`/`prompt`/`model` are missing).
2. Builds the prompt: `config.prompt`, plus `"\n\nInput: {upstream_output}"` if the upstream
   node produced an `"output"` key in `input_data`.
3. Calls `app.gateway.generate(model=..., prompt=..., system_prompt=..., fallback_model=...)`.
4. Returns `{"output": <model text>, "agent": config.name, "model_used": ..., "used_fallback": ...}`.

## Tools

`config.tools` is a list of tool names (matching `TOOL_REGISTRY` keys from `app/tools`). Wiring
an agent up to actually call tools mid-generation (a tool-use loop) is not implemented yet —
this field is reserved for that, and is safe to leave empty for agents that don't need it.
