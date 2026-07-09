import pytest

from app.tools.base import ToolError
from app.tools.code_exec import code_exec_tool


@pytest.mark.asyncio
async def test_code_exec_runs_snippet_and_captures_stdout():
    result = await code_exec_tool.run({"code": "print(1 + 1)"})
    assert result["stdout"].strip() == "2"
    assert result["exit_code"] == 0


@pytest.mark.asyncio
async def test_code_exec_captures_stderr_on_failure():
    result = await code_exec_tool.run({"code": "import sys; sys.exit(3)"})
    assert result["exit_code"] == 3


@pytest.mark.asyncio
async def test_code_exec_times_out_on_infinite_loop():
    with pytest.raises(ToolError, match="timed out"):
        await code_exec_tool.run({"code": "while True: pass"})
