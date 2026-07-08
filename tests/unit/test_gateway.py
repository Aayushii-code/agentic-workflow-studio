import pytest

from app.gateway.gateway import generate
from app.gateway.providers.base import ProviderError
from app.gateway.providers.groq import GroqProvider
import app.gateway.gateway as gateway_module


@pytest.mark.asyncio
async def test_mock_llm_is_deterministic_and_needs_no_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    response_1 = await generate(model="mock-llm", prompt="Analyze the input")
    response_2 = await generate(model="mock-llm", prompt="Analyze the input")

    assert response_1.text == response_2.text
    assert response_1.model_used == "mock-llm"
    assert response_1.provider == "mock"
    assert response_1.used_fallback is False


@pytest.mark.asyncio
async def test_mock_llm_includes_system_prompt():
    response = await generate(model="mock-llm", prompt="hello", system_prompt="You are terse.")
    assert "You are terse." in response.text
    assert "hello" in response.text


@pytest.mark.asyncio
async def test_groq_without_api_key_raises_provider_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    provider = GroqProvider()
    with pytest.raises(ProviderError, match="GROQ_API_KEY"):
        await provider.generate(prompt="hi", model="llama-3.3-70b-versatile")


@pytest.mark.asyncio
async def test_falls_back_to_mock_llm_when_real_provider_unavailable(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    response = await generate(
        model="llama-3.3-70b-versatile",
        prompt="Analyze the input",
        fallback_model="mock-llm",
    )

    assert response.used_fallback is True
    assert response.model_used == "mock-llm"
    assert response.provider == "mock"


@pytest.mark.asyncio
async def test_no_fallback_configured_propagates_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ProviderError):
        await generate(model="llama-3.3-70b-versatile", prompt="hi")


@pytest.mark.asyncio
async def test_groq_success_path_hits_expected_endpoint(monkeypatch):
    captured = {}

    class _FakeResponse:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": "Groq says hi"}}]}

        text = "irrelevant"

    class _FakeAsyncClient:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc_info):
            return False

        async def post(self, url, headers, json):
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return _FakeResponse()

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(
        "app.gateway.providers.groq.httpx.AsyncClient", _FakeAsyncClient
    )

    response = await generate(model="llama-3.3-70b-versatile", prompt="Analyze the input")

    assert response.text == "Groq says hi"
    assert response.provider == "groq"
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["json"]["model"] == "llama-3.3-70b-versatile"
    assert captured["json"]["messages"] == [{"role": "user", "content": "Analyze the input"}]


def test_reload_note():
    # gateway module caches provider singletons at import time; ensure the
    # module-level singletons exist for the routing tests above.
    assert gateway_module._provider_for_model("mock-llm").name == "mock"
    assert gateway_module._provider_for_model("anything-else").name == "groq"
