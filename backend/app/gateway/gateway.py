"""Provider-agnostic model gateway.

Routes a ``model`` name to a ``Provider`` instance, and optionally retries
against a ``fallback_model`` if the primary provider raises ``ProviderError``
(e.g. missing API key, network failure, non-200 response). This is what lets
an agent node say ``"model": "mock-llm"`` and get a deterministic response
with zero credentials, or say ``"model": "llama-3.3-70b-versatile"`` with
``fallback_model="mock-llm"`` and degrade gracefully when no Groq key is
configured.

Model -> provider routing: "mock-llm" (and anything starting with "mock")
always goes to MockProvider. Everything else goes to the default real
provider (Groq). Add more real providers by extending ``_provider_for_model``.
"""

from typing import Any

from app.gateway.providers.base import Provider, ProviderError
from app.gateway.providers.groq import GroqProvider
from app.gateway.providers.mock import MockProvider
from app.gateway.schemas import GatewayResponse

_mock_provider = MockProvider()
_groq_provider = GroqProvider()


def _provider_for_model(model: str) -> Provider:
    if model == "mock-llm" or model.startswith("mock"):
        return _mock_provider
    return _groq_provider


async def generate(
    *,
    model: str,
    prompt: str,
    system_prompt: str | None = None,
    fallback_model: str | None = None,
    **kwargs: Any,
) -> GatewayResponse:
    provider = _provider_for_model(model)
    try:
        text = await provider.generate(
            prompt=prompt, model=model, system_prompt=system_prompt, **kwargs
        )
        return GatewayResponse(text=text, model_used=model, provider=provider.name)
    except ProviderError:
        if not fallback_model:
            raise
        fallback_provider = _provider_for_model(fallback_model)
        text = await fallback_provider.generate(
            prompt=prompt, model=fallback_model, system_prompt=system_prompt, **kwargs
        )
        return GatewayResponse(
            text=text,
            model_used=fallback_model,
            provider=fallback_provider.name,
            used_fallback=True,
        )
