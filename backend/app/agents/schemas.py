"""Agent node config shape.

This mirrors/validates ``WorkflowNode.config`` for nodes of type "agent". It
is intentionally separate from ``app.schemas.workflow`` (owned by a
teammate) -- ``config`` there is a free-form dict by design, and this model
is how *this* node type interprets it.
"""

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    name: str = Field(min_length=1)
    prompt: str = Field(min_length=1, description="Role/task instructions for the agent.")
    model: str = Field(min_length=1)
    system_prompt: str | None = Field(
        default=None, description="Optional system prompt; defaults to none."
    )
    memory_scope: str = Field(
        default="none",
        description='How much conversation history this agent sees: "none" or "session".',
    )
    tools: list[str] = Field(
        default_factory=list, description="Names of tools (from TOOL_REGISTRY) this agent may call."
    )
    fallback_model: str | None = Field(
        default=None, description="Model to retry with if the primary model/provider fails."
    )
