"""
planner.py
----------
The Planner is responsible for sending the current context to Claude
and receiving its reasoning + next action decision.

Claude acts as the *reasoning engine*: given the goal and what has
happened so far, it decides which tool to call next (or stops with
a final answer).
"""

import anthropic
from utils.logger import get_logger

logger = get_logger(__name__)


class Planner:
    """
    Wraps the Claude API call that drives reasoning.

    Claude uses the 'tools' parameter to select and invoke tools.
    When Claude is done, it responds with stop_reason='end_turn'
    and plain text containing the final answer.
    """

    def plan(
        self,
        client: anthropic.Anthropic,
        model: str,
        system_prompt: str,
        messages: list,
        tools: list,
    ) -> anthropic.types.Message:
        """
        Ask Claude what to do next.

        Args:
            client:        Authenticated Anthropic client.
            model:         Model identifier string.
            system_prompt: The agent's persona & instructions.
            messages:      Full conversation history (goal + prior observations).
            tools:         List of tool definitions Claude can choose from.

        Returns:
            A raw Anthropic Message object. The caller inspects
            stop_reason and content blocks.
        """
        logger.debug(f"Planner sending {len(messages)} messages to Claude.")

        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            tools=tools,
            messages=messages,
        )

        logger.debug(f"Claude stop_reason: {response.stop_reason}")
        return response
