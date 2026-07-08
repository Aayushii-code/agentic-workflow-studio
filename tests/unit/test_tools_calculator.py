import pytest

from app.tools.base import ToolError
from app.tools.calculator import calculator_tool


@pytest.mark.asyncio
async def test_calculator_basic_arithmetic():
    result = await calculator_tool.run({"expression": "2 + 2 * 3"})
    assert result == {"result": 8}


@pytest.mark.asyncio
async def test_calculator_division_by_zero_raises_tool_error():
    with pytest.raises(ToolError, match="Division by zero"):
        await calculator_tool.run({"expression": "1 / 0"})


@pytest.mark.asyncio
async def test_calculator_rejects_non_arithmetic_input():
    with pytest.raises(ToolError):
        await calculator_tool.run({"expression": "__import__('os').system('echo hi')"})


@pytest.mark.asyncio
async def test_calculator_input_schema_validation():
    with pytest.raises(ToolError, match="failed validation"):
        await calculator_tool.run({"not_expression": "2+2"})
