# Agent/Tool Backend + Testing — Role Plan

Owner: Neha (branch `neha-agent-tool-backend`)

Scope boundary: I do NOT touch `backend/app/api`, `backend/app/engine`, `backend/app/schemas`
(owned by teammates). All new code lives in `backend/app/agents/`, `backend/app/tools/`,
`backend/app/gateway/`, `backend/app/executors/` (new, node-type dispatch used by the
executors below — not the DAG compiler in `engine/`), and top-level `tests/`.

## Deliverables (priority order per session brief)

1. Executor registry (`input`/`agent`/`output`, extensible) + 3-node integration test w/ mock-llm
2. Model gateway: provider-agnostic, `mock-llm` (zero API key) + Groq (real), per-node override, fallback
3. Tool-node SDK + example tools (calculator, web search stub, mock HTTP call, sandboxed code exec)
4. Pytest unit tests
5. Eval harness (separate from pytest): golden cases, exact-match + LLM-as-judge
6. Sandboxing note/example for code-execution tools
7. READMEs explaining the contracts

## Status log

- [x] Explored existing repo (`schemas/workflow.py`, `engine/validator.py`, `api/workflow.py`, `main.py`).
      Noted `ALLOWED_NODE_TYPES` already includes `"tool"` — teammate anticipated it.
- [x] Set up `backend/venv/` (gitignored) with pinned deps installed.
- [x] Appended new deps to end of `backend/requirements.txt` (UTF-16LE encoding preserved,
      matched existing style): httpx, jsonschema(+deps), pytest, pytest-asyncio, python-dotenv.
- [x] Executor registry (`backend/app/executors/`: registry.py, builtin.py, runner.py, bootstrap.py).
- [x] Model gateway (`backend/app/gateway/`): mock provider + Groq provider (httpx), fallback_model retry.
- [x] Agent node executor (`backend/app/agents/`): AgentConfig + execute_agent using the gateway.
- [x] Tool-node SDK (`backend/app/tools/base.py`): Tool dataclass w/ JSON-schema input/output
      validation (jsonschema), TOOL_REGISTRY. Example tools: calculator (ast-based, no eval()),
      web_search (deterministic stub), http_call (real httpx GET, 10s timeout), code_exec
      (subprocess + timeout, POSIX resource limits where available — sandboxing note in its
      module docstring). "tool" node executor bridges the SDK into EXECUTOR_REGISTRY.
- [x] 3-node integration test (`tests/integration/test_three_node_workflow.py`) — passes.
- [x] 30 pytest unit tests across registry/runner/gateway/agent/tools — all passing.
      Run with: `backend/venv/Scripts/python.exe -m pytest tests/ -v` (repo root `pytest.ini`
      adds `tests/` to `testpaths`, `asyncio_mode = auto`; `tests/conftest.py` puts
      `backend/` on `sys.path` and imports `app.executors.bootstrap`).
- [x] Eval harness (`tests/eval/`): `harness.py` (EvalCase/run_case/run_suite),
      `scoring.py` (exact_match, llm_judge — llm_judge degrades to a keyword heuristic when
      judge_model is "mock-llm", so it's runnable with zero API keys; point judge_model at a
      real Groq model + GROQ_API_KEY for genuine LLM-as-judge grading), golden cases in
      `tests/eval/cases/*.json` for both agent and tool node types. Run standalone with
      `backend/venv/Scripts/python.exe tests/eval/run_eval.py` (exits nonzero on any failure,
      separate from pytest). 5 pytest tests added for the harness itself
      (`tests/unit/test_eval_harness.py`).
- [x] READMEs written: `backend/app/executors/README.md`, `backend/app/gateway/README.md`,
      `backend/app/agents/README.md`, `backend/app/tools/README.md` (includes the sandboxing
      rule + documented residual risk for code_exec), `tests/README.md` (pytest vs eval harness).

## Final state

35 pytest tests passing (`pytest tests/ -v`), 6/6 eval golden cases passing
(`tests/eval/run_eval.py`). All deliverables from the session brief are complete. Verified
`git diff --stat` against `backend/app/api`, `backend/app/engine`, `backend/app/schemas` is
empty — no teammate files touched.

## Design notes (read before resuming)

- **Executor registry** lives in `backend/app/executors/` (new folder, sibling to `engine/`).
  `EXECUTOR_REGISTRY: dict[str, execute_fn]`, `register_executor(type)` decorator.
  A minimal `runner.py` does topological execution purely so I can integration-test node
  executors in isolation — it is NOT the real DAG compiler; Aayushi's `engine/` owns that.
- **Agent executor** (`backend/app/agents/`) reads `node.config` (name, prompt, model,
  optional system_prompt/fallback_model/memory_scope/tools), calls the gateway, returns
  `{"output": text, "agent": name, "model_used": ...}`.
- **Gateway** (`backend/app/gateway/`): `generate(model, prompt, ...)` dispatches to a
  provider keyed by model name; `mock-llm` -> deterministic `MockProvider` (no key needed);
  anything else -> `GroqProvider` (httpx, needs `GROQ_API_KEY`). `fallback_model` retried on
  `ProviderError`.
- **Tool SDK** (`backend/app/tools/`): `Tool` dataclass (name, input_schema, output_schema
  as JSON Schema, `execute()`, `auth_config`). `TOOL_REGISTRY`. A `"tool"` node executor
  bridges this into the executor registry (since `ALLOWED_NODE_TYPES` already allows it).
- **Sandboxing**: any code-exec tool must use `subprocess` + timeout, never `exec()`. On
  Windows there's no cgroup/rlimit equivalent in scope — document that residual risk.
- **Encoding gotcha**: `backend/requirements.txt` is UTF-16LE with BOM + CRLF — always
  read/write it via `open(path, 'rb').decode('utf-16')`, never plain text edit.
