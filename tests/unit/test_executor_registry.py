import pytest

from app.executors.registry import EXECUTOR_REGISTRY, get_executor, register_executor


def test_builtin_types_registered():
    assert "input" in EXECUTOR_REGISTRY
    assert "output" in EXECUTOR_REGISTRY
    assert "agent" in EXECUTOR_REGISTRY
    assert "tool" in EXECUTOR_REGISTRY


def test_get_executor_unknown_type_raises():
    with pytest.raises(ValueError, match="No executor registered"):
        get_executor("logic.branch")


def test_register_executor_adds_new_type():
    @register_executor("__test_type__")
    async def _dummy(node, input_data):
        return {"output": "dummy"}

    try:
        assert get_executor("__test_type__") is _dummy
    finally:
        del EXECUTOR_REGISTRY["__test_type__"]
