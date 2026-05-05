"""
agent_loop.py
-------------
Core agent loop implementing the Plan → Act → Observe → Iterate cycle.
This is the main orchestration engine of the Claude-based Agentic AI system.
"""

import json
import time
from typing import Optional

import anthropic

from agent.planner import Planner
from agent.observer import Observer
from memory.context_manager import ContextManager
from tools.tool_registry import ToolRegistry
from prompts.templates import SYSTEM_PROMPT, FINAL_ANSWER_PROMPT
from utils.logger import get_logger

logger = get_logger(__name__)


class AgentLoop:
    """
    Implements the core ReAct-style agentic loop:
      1. PLAN   – Claude reasons about the goal and decides the next action.
      2. ACT    – The chosen tool is executed with Claude-provided arguments.
      3. OBSERVE– The tool result is captured and fed back to Claude.
      4. ITERATE– Steps 1-3 repeat until Claude produces a Final Answer.
    """

    def __init__(
        self,
        max_iterations: int = 10,
        verbose: bool = True,
    ):
        self.client = anthropic.Anthropic()          # reads ANTHROPIC_API_KEY from env
        self.model = "claude-sonnet-4-20250514"

        self.planner = Planner()
        self.observer = Observer()
        self.context = ContextManager()
        self.tools = ToolRegistry()

        self.max_iterations = max_iterations
        self.verbose = verbose

    # ------------------------------------------------------------------
    # Public entry-point
    # ------------------------------------------------------------------

    def run(self, goal: str) -> str:
        """
        Run the agent loop for a given user goal.

        Args:
            goal: Natural-language description of what the user wants.

        Returns:
            The agent's final answer as a plain string.
        """
        logger.info(f"🚀  Agent started. Goal: {goal}")
        self.context.set_goal(goal)

        for iteration in range(1, self.max_iterations + 1):
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"  ITERATION {iteration}/{self.max_iterations}")
                print(f"{'='*60}")

            # ── PLAN ──────────────────────────────────────────────────
            messages = self.context.get_messages()
            plan_response = self.planner.plan(
                client=self.client,
                model=self.model,
                system_prompt=SYSTEM_PROMPT,
                messages=messages,
                tools=self.tools.get_tool_definitions(),
            )

            # ── CHECK FOR FINAL ANSWER ────────────────────────────────
            if plan_response.stop_reason == "end_turn":
                final_text = self._extract_text(plan_response)
                if final_text:
                    logger.info("✅  Agent produced final answer.")
                    self.context.add_assistant_message(final_text)
                    return self._format_final_answer(final_text)

            # ── ACT ───────────────────────────────────────────────────
            tool_uses = self._extract_tool_uses(plan_response)
            if not tool_uses:
                # Claude stopped without tool use and without text – safety fallback
                logger.warning("No tool use and no text. Breaking loop.")
                break

            # Add Claude's full response (may contain text + tool_use blocks)
            self.context.add_raw_assistant_content(plan_response.content)

            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use.name
                tool_input = tool_use.input
                tool_use_id = tool_use.id

                if self.verbose:
                    print(f"\n  🔧  ACTION  → {tool_name}")
                    print(f"      Input   : {json.dumps(tool_input, indent=6)}")

                # ── OBSERVE ───────────────────────────────────────────
                observation = self.observer.observe(
                    tool_registry=self.tools,
                    tool_name=tool_name,
                    tool_input=tool_input,
                )

                if self.verbose:
                    preview = str(observation)[:300]
                    print(f"      Result  : {preview}{'...' if len(str(observation)) > 300 else ''}")

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": str(observation),
                })

            # Feed all tool results back into context in one user turn
            self.context.add_tool_results(tool_results)

        logger.warning("⚠️  Max iterations reached. Requesting final answer.")
        return self._force_final_answer()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_text(self, response) -> Optional[str]:
        """Pull plain text blocks out of a Claude response."""
        parts = [b.text for b in response.content if b.type == "text"]
        return "\n".join(parts).strip() or None

    def _extract_tool_uses(self, response) -> list:
        """Pull tool_use blocks out of a Claude response."""
        return [b for b in response.content if b.type == "tool_use"]

    def _format_final_answer(self, text: str) -> str:
        """Wrap the final answer in a clear display format."""
        border = "═" * 60
        return f"\n{border}\n  FINAL ANSWER\n{border}\n{text}\n{border}\n"

    def _force_final_answer(self) -> str:
        """
        Ask Claude to produce a final answer when max iterations are hit.
        Uses the accumulated context so far.
        """
        messages = self.context.get_messages()
        messages.append({"role": "user", "content": FINAL_ANSWER_PROMPT})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        final_text = self._extract_text(response) or "Agent could not produce a final answer."
        return self._format_final_answer(final_text)
