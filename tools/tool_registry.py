"""
tool_registry.py
----------------
Central registry that maps tool names to their implementations
and exposes tool definitions in the Anthropic tool-use format.

Adding a new tool is a one-liner:
    registry.register(MyNewTool())
"""

from typing import Any
from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """
    Maintains a catalogue of all tools available to the agent.

    Tools must subclass BaseTool and implement:
      - name        (str property)
      - description (str property)
      - parameters  (dict property – JSON Schema)
      - execute(input_dict) -> str
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Auto-register the built-in tools."""
        from tools.web_search_tool import WebSearchTool
        from tools.summarizer_tool import SummarizerTool
        from tools.file_writer_tool import FileWriterTool
        from tools.calculator_tool import CalculatorTool
        from tools.wikipedia_tool import WikipediaTool
        from tools.weather_tool import WeatherTool
        from tools.code_executor_tool import CodeExecutorTool

        for tool in [
            WebSearchTool(),
            SummarizerTool(),
            FileWriterTool(),
            CalculatorTool(),
            WikipediaTool(),
            WeatherTool(),
            CodeExecutorTool(),
        ]:
            self.register(tool)

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: '{tool.name}'")

    def execute(self, tool_name: str, tool_input: dict) -> str:
        """
        Execute a tool by name.

        Raises KeyError if the tool is not registered.
        """
        if tool_name not in self._tools:
            raise KeyError(tool_name)
        return self._tools[tool_name].execute(tool_input)

    def get_tool_definitions(self) -> list[dict]:
        """
        Return tool definitions in the Anthropic API format.

        Each definition has: name, description, input_schema.
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters,
            }
            for tool in self._tools.values()
        ]

    def list_tools(self) -> list[str]:
        """Return the names of all registered tools."""
        return list(self._tools.keys())
