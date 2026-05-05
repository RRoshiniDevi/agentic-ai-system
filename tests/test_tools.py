"""
tests/test_tools.py
-------------------
Unit tests for individual tool implementations.
Run with: pytest tests/
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from tools.calculator_tool import CalculatorTool
from tools.file_writer_tool import FileWriterTool
from tools.tool_registry import ToolRegistry


class TestCalculatorTool:
    def setup_method(self):
        self.tool = CalculatorTool()

    def test_addition(self):
        result = self.tool.execute({"expression": "2 + 3"})
        assert "5" in result

    def test_multiplication(self):
        result = self.tool.execute({"expression": "6 * 7"})
        assert "42" in result

    def test_division(self):
        result = self.tool.execute({"expression": "10 / 4"})
        assert "2.5" in result

    def test_power(self):
        result = self.tool.execute({"expression": "2 ** 10"})
        assert "1024" in result

    def test_division_by_zero(self):
        result = self.tool.execute({"expression": "1 / 0"})
        assert "ERROR" in result

    def test_complex_expression(self):
        result = self.tool.execute({"expression": "(100 + 50) * 2 / 3"})
        assert "100" in result

    def test_name(self):
        assert self.tool.name == "calculator"

    def test_parameters_schema(self):
        params = self.tool.parameters
        assert params["type"] == "object"
        assert "expression" in params["properties"]


class TestFileWriterTool:
    def setup_method(self):
        self.tool = FileWriterTool()

    def test_write_file(self, tmp_path, monkeypatch):
        from tools import file_writer_tool
        monkeypatch.setattr(file_writer_tool, "OUTPUT_DIR", tmp_path)
        result = self.tool.execute({"filename": "test.txt", "content": "hello world"})
        assert "Written" in result
        assert (tmp_path / "test.txt").read_text() == "hello world"

    def test_name(self):
        assert self.tool.name == "write_file"


class TestToolRegistry:
    def setup_method(self):
        self.registry = ToolRegistry()

    def test_default_tools_registered(self):
        tools = self.registry.list_tools()
        assert "web_search" in tools
        assert "summarize_text" in tools
        assert "write_file" in tools
        assert "calculator" in tools

    def test_get_tool_definitions(self):
        defs = self.registry.get_tool_definitions()
        assert isinstance(defs, list)
        assert len(defs) >= 4
        for d in defs:
            assert "name" in d
            assert "description" in d
            assert "input_schema" in d

    def test_execute_calculator(self):
        result = self.registry.execute("calculator", {"expression": "3 + 3"})
        assert "6" in result

    def test_execute_unknown_tool(self):
        with pytest.raises(KeyError):
            self.registry.execute("nonexistent_tool", {})
