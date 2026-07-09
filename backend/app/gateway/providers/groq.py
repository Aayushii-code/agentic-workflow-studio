"""Real provider backed by Groq's OpenAI-compatible chat completions API.

Requires the GROQ_API_KEY environment variable. If it isn't set, this
provider raises ProviderError immediately (before making any network call)
so the gateway's fallback logic can kick in -- teammates without a Groq key
can still run workflows by setting a fallback_model of "mock-llm".
"""

import os
from typing import Any

import httpx

from app.gateway.providers.base import ProviderError

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_TIMEOUT_SECONDS = 30.0


class GroqProvider:
    name = "groq"

    def __init__(self, api_key: str | None = None, timeout: float = DEFAULT_TIMEOUT_SECONDS):
        self._api_key = api_key
        self._timeout = timeout

    def _resolve_api_key(self) -> str:
        api_key = self._api_key or os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ProviderError(
                "GROQ_API_KEY is not set. Set it in the environment, or configure a "
                "fallback_model (e.g. 'mock-llm') on the agent node."
            )
        return api_key

    async def generate(
        self,
        *,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        api_key = self._resolve_api_key()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {"model": model, "messages": messages}
        payload.update(kwargs)

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                )
        except httpx.HTTPError as exc:
            raise ProviderError(f"Groq request failed: {exc}") from exc

        if response.status_code != 200:
            raise ProviderError(
                f"Groq request failed with status {response.status_code}: {response.text}"
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(f"Unexpected Groq response shape: {data}") from exc
