# Model gateway

Provider-agnostic abstraction over LLM backends. An agent node's `config.model` (and optional
`config.fallback_model`) is all a caller needs to know; the gateway decides which provider
actually handles the request.

```python
from app.gateway import generate

response = await generate(
    model="mock-llm",          # or e.g. "llama-3.3-70b-versatile"
    prompt="Analyze the input",
    system_prompt=None,        # optional
    fallback_model="mock-llm", # optional: retried if the primary provider raises ProviderError
)
# response.text, response.model_used, response.provider, response.used_fallback
```

## Providers

- **`mock-llm`** (`providers/mock.py`) — deterministic, zero-dependency, zero-API-key. Any model
  name equal to `"mock-llm"` or starting with `"mock"` routes here. This is what the shared
  workflow JSON contract's `"model": "mock-llm"` resolves to, and what makes the 3-node
  integration test and the eval harness runnable without credentials.
- **Groq** (`providers/groq.py`) — real provider, OpenAI-compatible chat completions API. Requires
  `GROQ_API_KEY` in the environment. Any model name that isn't the mock model routes here. If the
  key is missing, it raises `ProviderError` immediately (no network call) so a configured
  `fallback_model` can take over.

## Adding another real provider

Implement the `Provider` protocol in `providers/base.py` (`async generate(*, prompt, model,
system_prompt=None, **kwargs) -> str`, raise `ProviderError` on failure), then extend
`_provider_for_model` in `gateway.py` to route to it.

## Fallback behavior

`generate()` tries `model` first. If that provider raises `ProviderError`, and `fallback_model`
was given, it retries once against whatever provider owns `fallback_model` and marks
`response.used_fallback = True`. If there's no fallback configured, the error propagates. A
teammate without a Groq key can still run any workflow by setting the agent node's
`fallback_model` to `"mock-llm"`.
