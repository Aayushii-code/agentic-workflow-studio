"""Executor for the "agent" node type: an LLM with a role, system prompt,
memory scope, and bound tools, per the shared workflow JSON contract.

Config shape (see AgentConfig):
    {"name": "Analyzer", "prompt": "Analyze the input", "model": "mock-llm"}
"""

from typing import Any

from app.schemas.workflow import WorkflowNode
from app.executors.registry import register_executor
from app.agents.schemas import AgentConfig
from app.gateway.gateway import generate


def _render_prompt(config: AgentConfig, input_data: dict[str, Any]) -> str:
    upstream_output = input_data.get("output")
    if upstream_output is None:
        return config.prompt
    return f"{config.prompt}\n\nInput: {upstream_output}"


@register_executor("agent")
async def execute_agent(node: WorkflowNode, input_data: dict[str, Any]) -> dict[str, Any]:
    config = AgentConfig.model_validate(node.config)

    response = await generate(
        model=config.model,
        prompt=_render_prompt(config, input_data),
        system_prompt=config.system_prompt,
        fallback_model=config.fallback_model,
    )

    return {
        "output": response.text,
        "agent": config.name,
        "model_used": response.model_used,
        "used_fallback": response.used_fallback,
    }
