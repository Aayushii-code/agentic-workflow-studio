"""Golden-case eval harness for agent/tool node executors.

Deliberately separate from pytest: this scores *behavior quality* against
golden examples (exact-match or LLM-as-judge), not code correctness. Unit
tests should keep passing even if a model's phrasing drifts; eval cases are
what tell you the drift happened.

Case file schema (JSON, a list of objects), see tests/eval/cases/*.json:

    {
      "id": "unique-case-id",
      "node_type": "agent" | "tool",
      "config": {...node config, same shape as workflow JSON node.config...},
      "input_data": {...whatever the node's upstream would have produced...},
      "output_path": "output",           # dot path into the executor's return dict
      "scoring": "exact_match" | "llm_judge",
      "expected_output": ...,            # required for exact_match
      "rubric": "...",                   # required for llm_judge
      "judge_model": "mock-llm"          # optional, defaults to mock-llm
    }
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.schemas.workflow import WorkflowNode
from app.executors.registry import get_executor
from tests.eval.scoring import score_exact_match, score_llm_judge


@dataclass
class EvalCase:
    id: str
    node_type: str
    config: dict[str, Any]
    input_data: dict[str, Any]
    scoring: str
    output_path: str = "output"
    expected_output: Any = None
    rubric: str | None = None
    judge_model: str = "mock-llm"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvalCase":
        return cls(
            id=data["id"],
            node_type=data["node_type"],
            config=data["config"],
            input_data=data.get("input_data", {}),
            scoring=data["scoring"],
            output_path=data.get("output_path", "output"),
            expected_output=data.get("expected_output"),
            rubric=data.get("rubric"),
            judge_model=data.get("judge_model", "mock-llm"),
        )


@dataclass
class EvalResult:
    case_id: str
    passed: bool
    detail: str


def _get_path(data: Any, path: str) -> Any:
    current = data
    for part in path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def load_cases(cases_dir: Path) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for path in sorted(cases_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        cases.extend(EvalCase.from_dict(item) for item in raw)
    return cases


async def run_case(case: EvalCase) -> EvalResult:
    node = WorkflowNode(id=case.id, type=case.node_type, position={"x": 0, "y": 0}, config=case.config)
    executor = get_executor(case.node_type)

    try:
        result = await executor(node, case.input_data)
        actual = _get_path(result, case.output_path)
    except Exception as exc:  # noqa: BLE001 - a case that crashes the executor is a failed case
        return EvalResult(case_id=case.id, passed=False, detail=f"executor raised: {exc!r}")

    if case.scoring == "exact_match":
        passed, detail = await score_exact_match(case.expected_output, actual)
    elif case.scoring == "llm_judge":
        passed, detail = await score_llm_judge(case.rubric or "", actual, case.judge_model)
    else:
        return EvalResult(case_id=case.id, passed=False, detail=f"unknown scoring strategy: {case.scoring}")

    return EvalResult(case_id=case.id, passed=passed, detail=detail)


async def run_suite(cases_dir: Path) -> list[EvalResult]:
    cases = load_cases(cases_dir)
    return [await run_case(case) for case in cases]
