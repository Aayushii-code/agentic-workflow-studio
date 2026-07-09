"""Provider interface every model backend must implement.

A provider is deliberately small: given a prompt (and optional system
prompt/model name/kwargs), return generated text or raise ``ProviderError``.
The gateway (``app.gateway.gateway``) is the only thing that knows about
per-node overrides, fallback chains, and model->provider routing.
"""

from typing import Any, Protocol


class ProviderError(Exception):
    """Raised when a provider cannot fulfil a generation request.

    The gateway catches this to decide whether to retry against a
    fallback model/provider.
    """


class Provider(Protocol):
    name: str

    async def generate(
        self,
        *,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        ...
