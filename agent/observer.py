"""
observer.py
-----------
The Observer executes the tool chosen by the Planner and returns
the result as a structured observation string.

This keeps tool dispatch completely separate from planning logic.
"""

from tools.tool_registry import ToolRegistry
from utils.logger import get_logger

logger = get_logger(__name__)


class Observer:
    """
    Bridges the Planner's tool-use decision and the ToolRegistry.

    Responsibilities:
    - Call the right tool with the right arguments.
    - Catch and surface errors gracefully (the agent can recover).
    - Return a consistent string observation to be fed back to Claude.
    """

    def observe(
        self,
        tool_registry: ToolRegistry,
        tool_name: str,
        tool_input: dict,
    ) -> str:
        """
        Execute a tool and return its output as a string.

        Args:
            tool_registry: Registry containing all available tools.
            tool_name:     Name of the tool Claude chose.
            tool_input:    Arguments dict Claude provided.

        Returns:
            String observation to be added to the conversation context.
        """
        logger.info(f"Observer executing tool: '{tool_name}' with input: {tool_input}")

        try:
            result = tool_registry.execute(tool_name, tool_input)
            observation = f"Tool '{tool_name}' returned:\n{result}"
            logger.debug(f"Observation (first 200 chars): {observation[:200]}")
            return observation

        except KeyError:
            error_msg = f"ERROR: Tool '{tool_name}' is not registered. Available tools: {tool_registry.list_tools()}"
            logger.error(error_msg)
            return error_msg

        except Exception as exc:
            error_msg = f"ERROR: Tool '{tool_name}' failed with exception: {type(exc).__name__}: {exc}"
            logger.error(error_msg)
            return error_msg
