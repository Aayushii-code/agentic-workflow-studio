"""Scoring strategies for the eval harness.

exact_match: strict equality between the expected value and whatever the
node executor produced at `output_path`.

llm_judge: asks a model to grade the actual output against a natural
language rubric. When `judge_model` is "mock-llm" (the default, so the
harness is runnable with zero API keys) there is no real reasoning
available, so this falls back to a keyword-containment heuristic against a
comma-separated rubric -- a stand-in for real grading, not a substitute for
it. Point `judge_model` at a real provider (e.g. a Groq model, with
GROQ_API_KEY set) to get genuine LLM-as-judge behavior.
"""

from typing import Any

from app.gateway.gateway import generate


async def score_exact_match(expected: Any, actual: Any) -> tuple[bool, str]:
    passed = expected == actual
    return passed, f"expected={expected!r} actual={actual!r}"


async def score_llm_judge(rubric: str, actual: Any, judge_model: str = "mock-llm") -> tuple[bool, str]:
    if judge_model == "mock-llm":
        keywords = [word.strip().lower() for word in rubric.split(",") if word.strip()]
        actual_text = str(actual).lower()
        missing = [keyword for keyword in keywords if keyword not in actual_text]
        passed = not missing
        detail = "keyword-heuristic judge (no real judge model configured); " + (
            "all required keywords present" if passed else f"missing keywords: {missing}"
        )
        return passed, detail

    judge_prompt = (
        "You are grading an AI agent's output against a rubric.\n"
        f"Rubric: {rubric}\n"
        f"Output to grade: {actual}\n"
        "Respond with exactly one word: PASS or FAIL."
    )
    response = await generate(model=judge_model, prompt=judge_prompt)
    verdict = response.text.strip().upper()
    passed = verdict.startswith("PASS")
    return passed, f"judge_model={judge_model} verdict={response.text!r}"
