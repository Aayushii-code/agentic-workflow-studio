"""HTTP call tool: performs a real outbound GET request with a hard timeout.

Demonstrates the Tool-node SDK for an I/O-bound tool that talks to the
outside world (as opposed to calculator's pure computation or web_search's
canned stub). Bounded by a short timeout so a hanging endpoint can't stall a
workflow run.
"""

from typing import Any

import httpx

from app.tools.base import Tool, ToolError, register_tool

_TIMEOUT_SECONDS = 10.0


async def _execute(data: dict[str, Any]) -> dict[str, Any]:
    url = data["url"]
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
    except httpx.HTTPError as exc:
        raise ToolError(f"HTTP GET to '{url}' failed: {exc}") from exc

    return {
        "status_code": response.status_code,
        "body": response.text[:5000],
    }


http_call_tool = register_tool(
    Tool(
        name="http_call",
        description="Performs an HTTP GET request against a URL with a 10s timeout.",
        input_schema={
            "type": "object",
            "properties": {"url": {"type": "string", "format": "uri"}},
            "required": ["url"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "status_code": {"type": "integer"},
                "body": {"type": "string"},
            },
            "required": ["status_code", "body"],
        },
        execute=_execute,
        auth_config={"type": "none", "note": "add 'bearer_env_var' style auth_config if a target API needs it"},
    )
)
