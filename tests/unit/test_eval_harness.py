import pytest

from tests.eval.harness import EvalCase, run_case
from tests.eval.scoring import score_exact_match, score_llm_judge


@pytest.mark.asyncio
async def test_exact_match_case_pass():
    case = EvalCase(
        id="t1",
        node_type="tool",
        config={"tool_name": "calculator", "input": {"expression": "2 + 2"}},
        input_data={},
        scoring="exact_match",
        output_path="output.result",
        expected_output=4,
    )
    result = await run_case(case)
    assert result.passed is True


@pytest.mark.asyncio
async def test_exact_match_case_fail():
    case = EvalCase(
        id="t2",
        node_type="tool",
        config={"tool_name": "calculator", "input": {"expression": "2 + 2"}},
        input_data={},
        scoring="exact_match",
        output_path="output.result",
        expected_output=5,
    )
    result = await run_case(case)
    assert result.passed is False


@pytest.mark.asyncio
async def test_executor_exception_is_a_failed_case_not_a_crash():
    case = EvalCase(
        id="t3",
        node_type="tool",
        config={"tool_name": "unknown_tool"},
        input_data={},
        scoring="exact_match",
        expected_output="anything",
    )
    result = await run_case(case)
    assert result.passed is False
    assert "raised" in result.detail


@pytest.mark.asyncio
async def test_score_llm_judge_mock_keyword_heuristic():
    passed, detail = await score_llm_judge("hpe, workflow", "HPE Workflow Studio")
    assert passed is True

    passed, detail = await score_llm_judge("nonexistent_keyword", "HPE Workflow Studio")
    assert passed is False
    assert "missing keywords" in detail


@pytest.mark.asyncio
async def test_score_exact_match_direct():
    passed, _ = await score_exact_match("a", "a")
    assert passed is True
    passed, _ = await score_exact_match("a", "b")
    assert passed is False
