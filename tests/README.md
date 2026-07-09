# Tests

Two separate things live here, on purpose:

## 1. pytest (`tests/unit/`, `tests/integration/`)

Ordinary correctness tests — do the executor registry, gateway, agent executor, and tool SDK
behave the way the code says they should. Run from the repo root:

```
backend/venv/Scripts/python.exe -m pytest tests/ -v
```

(`pytest.ini` at the repo root points `testpaths` at `tests/`, sets `asyncio_mode = auto` so
`async def test_...` functions just work, and `tests/conftest.py` puts `backend/` on `sys.path`
and imports `app.executors.bootstrap` so every node type is registered before any test runs.)

`tests/integration/test_three_node_workflow.py` is the most important file here for the rest of
the team: it runs the exact 3-node sample from the shared workflow JSON contract
(`input -> agent -> output`) end to end using `mock-llm`, and asserts the data actually flows
correctly between nodes.

## 2. Eval harness (`tests/eval/`)

Golden-case scoring — does an agent/tool node's *output quality* still match expectations. This
is intentionally not pytest: model output can legitimately drift in ways that aren't "bugs" (a
prompt tweak changes phrasing), and you want a report of what changed, not a red X. Run
independently:

```
backend/venv/Scripts/python.exe tests/eval/run_eval.py
```

Golden cases live in `tests/eval/cases/*.json` (see that directory's files for the schema).
Each case names a node type + config + input, and scores the executor's output either by
`exact_match` (strict equality) or `llm_judge` (a rubric graded by a model — see
`tests/eval/scoring.py` for how this degrades gracefully to a keyword heuristic when no real
judge model is configured, so the harness stays runnable with zero API keys).

`run_eval.py` exits non-zero if any case fails, so it can be wired into CI as its own gate,
separately from the pytest suite.
