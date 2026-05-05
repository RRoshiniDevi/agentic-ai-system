"""
context_manager.py
------------------
Manages the agent's working memory: the growing list of messages
that forms the conversation history sent to Claude on every iteration.

This is the agent's short-term memory. It maintains:
  - The original user goal
  - Every assistant reasoning step
  - Every tool result observation
"""

from typing import Any
from utils.logger import get_logger

logger = get_logger(__name__)


class ContextManager:
    """
    Maintains the full message history for the current agent run.

    Message format follows the Anthropic Messages API:
      { "role": "user" | "assistant", "content": str | list }
    """

    def __init__(self):
        self._messages: list[dict] = []
        self._goal: str = ""

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def set_goal(self, goal: str) -> None:
        """Initialise context with the user's top-level goal."""
        self._goal = goal
        self._messages = [
            {
                "role": "user",
                "content": (
                    f"Your goal is:\n\n{goal}\n\n"
                    "Think step-by-step. Use the available tools to gather "
                    "information, then produce a comprehensive final answer."
                ),
            }
        ]
        logger.debug(f"Context initialised with goal: {goal[:80]}...")

    # ------------------------------------------------------------------
    # Adding messages
    # ------------------------------------------------------------------

    def add_assistant_message(self, text: str) -> None:
        """Add a plain-text assistant message (used for final answer)."""
        self._messages.append({"role": "assistant", "content": text})

    def add_raw_assistant_content(self, content: list) -> None:
        """
        Add Claude's raw content block list as an assistant turn.
        This preserves tool_use blocks so the API can match tool_result IDs.
        """
        self._messages.append({"role": "assistant", "content": content})

    def add_tool_results(self, tool_results: list[dict]) -> None:
        """
        Add one or more tool results as a single user turn.
        The Anthropic API requires tool results in the user role.

        Args:
            tool_results: List of dicts with keys:
                          type, tool_use_id, content
        """
        self._messages.append({"role": "user", "content": tool_results})
        logger.debug(f"Added {len(tool_results)} tool result(s) to context.")

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def get_messages(self) -> list[dict]:
        """Return the full message history."""
        return list(self._messages)

    def get_goal(self) -> str:
        return self._goal

    def message_count(self) -> int:
        return len(self._messages)

    # ------------------------------------------------------------------
    # Persistence helpers (extend for long-term memory / vector stores)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise context to a dict (for saving/loading runs)."""
        return {"goal": self._goal, "messages": self._messages}

    def from_dict(self, data: dict) -> None:
        """Restore context from a previously serialised dict."""
        self._goal = data.get("goal", "")
        self._messages = data.get("messages", [])
