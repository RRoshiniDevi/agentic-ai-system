"""
base_tool.py
------------
Abstract base class that every tool must implement.
This enforces a consistent interface across all tools.
"""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Contract that all agent tools must satisfy.

    Subclasses must implement:
      - name        → unique identifier string (snake_case)
      - description → clear natural-language description for Claude
      - parameters  → JSON Schema dict describing the input
      - execute()   → runs the tool and returns a result string
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique snake_case tool name (e.g. 'web_search')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """
        One-paragraph description that tells Claude WHEN and HOW
        to use this tool. Be specific – Claude uses this to decide.
        """
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """
        JSON Schema object describing the tool's input.

        Example:
        {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "..."}
            },
            "required": ["query"]
        }
        """
        ...

    @abstractmethod
    def execute(self, tool_input: dict) -> str:
        """
        Run the tool with the given input dict.

        Args:
            tool_input: Dict matching the parameters schema.

        Returns:
            String result to be fed back to the agent as an observation.
        """
        ...
