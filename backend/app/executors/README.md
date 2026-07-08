# Executor registry

Maps a workflow node's `type` string to an async `execute(node, input_data)`
function. This is the extension point for new node types.

```python
EXECUTOR_REGISTRY: dict[str, execute_fn]
```

- `node`: the `WorkflowNode` (from `app.schemas.workflow`, owned by the schema team) being run.
- `input_data`: whatever the node's single predecessor returned (or `{"inputs": [...]}` for fan-in).
- return value: a `dict` that becomes this node's output, and the next node's `input_data`.

## How to add a new node type

1. Write an async function `execute(node, input_data) -> dict`.
2. Decorate it: `@register_executor("your-type")` (see `builtin.py` for the simplest examples,
   `app/agents/executor.py` and `app/tools/executor.py` for richer ones).
3. Make sure the module gets imported somewhere before you dispatch on that type — either add
   it to `app/executors/bootstrap.py`, or import it directly. Registration is just an import-time
   side effect; nothing else needs to know which package owns which node type.
4. If the DAG engine's `ALLOWED_NODE_TYPES` (in `app/engine/validator.py`, owned by the engine
   team) doesn't already list your type, it also needs to be added there — that's a separate
   allowlist for workflow *validation*, this registry is for *execution*.

## What lives here vs. `app/engine`

This package only answers "how do I run one node of type X". It does not do graph traversal,
ordering, or parallel execution — that's the DAG compiler in `app/engine` (owned by the
workflow-engine team). `runner.py` in this package is a minimal Kahn's-algorithm topological
runner that exists **only** so node executors can be integration-tested in isolation
(see `tests/integration/test_three_node_workflow.py`); it is not the production execution path.

## Files

- `registry.py` — `EXECUTOR_REGISTRY`, `register_executor`, `get_executor`.
- `builtin.py` — the `"input"` and `"output"` node types from the shared JSON contract.
- `runner.py` — test-only topological runner (see above).
- `bootstrap.py` — import this once to register every known node type (`input`, `output`,
  `agent`, `tool`).
