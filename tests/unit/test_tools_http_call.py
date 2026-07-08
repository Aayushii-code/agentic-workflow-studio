import httpx
import pytest

import app.tools.http_call as http_call_module
from app.tools.http_call import http_call_tool


@pytest.mark.asyncio
async def test_http_call_returns_status_and_body(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("https://example.com/data")
        return httpx.Response(200, text="ok body")

    class _FakeAsyncClient(httpx.AsyncClient):
        def __init__(self, timeout):
            super().__init__(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(http_call_module.httpx, "AsyncClient", _FakeAsyncClient)

    result = await http_call_tool.run({"url": "https://example.com/data"})

    assert result == {"status_code": 200, "body": "ok body"}
