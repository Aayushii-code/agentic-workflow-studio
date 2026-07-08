import pytest

from app.tools.web_search import web_search_tool


@pytest.mark.asyncio
async def test_web_search_returns_deterministic_stub_results():
    result_1 = await web_search_tool.run({"query": "workflow studio"})
    result_2 = await web_search_tool.run({"query": "workflow studio"})
    assert result_1 == result_2
    assert len(result_1["results"]) == 3
    assert "workflow studio" in result_1["results"][0]["title"]


@pytest.mark.asyncio
async def test_web_search_respects_max_results():
    result = await web_search_tool.run({"query": "hi", "max_results": 1})
    assert len(result["results"]) == 1
