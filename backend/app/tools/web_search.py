"""Web search tool -- stub implementation.

Returns deterministic canned results instead of calling a real search API.
This proves the Tool-node SDK's shape (input/output schema, execute(),
auth_config) for an "external API" style tool without requiring API keys or
network access. Swap ``_execute`` for a real HTTP call to a search provider
and set ``auth_config`` accordingly when one is available -- the schema and
calling convention won't need to change.
"""

from typing import Any

from app.tools.base import Tool, register_tool


async def _execute(data: dict[str, Any]) -> dict[str, Any]:
    query = data["query"]
    max_results = data.get("max_results", 3)
    stub_results = [
        {
            "title": f"Result {i + 1} for '{query}'",
            "url": f"https://example.com/search?q={query.replace(' ', '+')}&result={i + 1}",
            "snippet": f"This is a stub search result #{i + 1} for the query '{query}'.",
        }
        for i in range(max_results)
    ]
    return {"results": stub_results}


web_search_tool = register_tool(
    Tool(
        name="web_search",
        description="Stub web search: returns deterministic canned results for a query.",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "max_results": {"type": "integer", "minimum": 1, "maximum": 10},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        output_schema={
            "type": "object",
            "properties": {
                "results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "url": {"type": "string"},
                            "snippet": {"type": "string"},
                        },
                        "required": ["title", "url", "snippet"],
                    },
                }
            },
            "required": ["results"],
        },
        execute=_execute,
        auth_config={"type": "none", "note": "stub -- replace with a real provider + api_key auth"},
    )
)
