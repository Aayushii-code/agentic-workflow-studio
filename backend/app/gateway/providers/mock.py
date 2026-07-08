"""Deterministic, zero-dependency, zero-API-key provider.

Used for local development, CI, teammate integration testing, and the eval
harness's exact-match golden cases -- anywhere a real API key isn't
available or determinism is required. This is what "model": "mock-llm" in
the shared workflow JSON contract resolves to.
"""

from typing import Any


class MockProvider:
    name = "mock"

    async def generate(
        self,
        *,
        prompt: str,
        model: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        body = f"{system_prompt.strip()}\n{prompt.strip()}" if system_prompt else prompt.strip()
        return f"[mock-llm response] {body}"
