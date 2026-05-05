"""
summarizer_tool.py
------------------
Uses Claude itself (via a nested API call) to summarise a block
of text. Demonstrates tool chaining: one Claude call (the agent)
can invoke another Claude call (the summariser).
"""

import anthropic
from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger(__name__)


class SummarizerTool(BaseTool):
    """Summarises a long piece of text into concise bullet points."""

    @property
    def name(self) -> str:
        return "summarize_text"

    @property
    def description(self) -> str:
        return (
            "Summarise a long piece of text into concise, structured bullet points. "
            "Use this tool after gathering raw information (e.g. from web_search) "
            "to condense it before including it in the final answer. "
            "Input: the raw text to summarise and an optional focus topic. "
            "Output: a bullet-point summary."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text content to summarise.",
                },
                "focus": {
                    "type": "string",
                    "description": (
                        "Optional: a specific aspect or question to focus the "
                        "summary on (e.g. 'key advantages', 'how it works')."
                    ),
                },
            },
            "required": ["text"],
        }

    def execute(self, tool_input: dict) -> str:
        text = tool_input.get("text", "").strip()
        focus = tool_input.get("focus", "general overview")

        if not text:
            return "ERROR: No text provided to summarise."

        logger.info(f"SummarizerTool: summarising {len(text)} chars, focus='{focus}'")

        client = anthropic.Anthropic()
        prompt = (
            f"Please summarise the following text into clear bullet points. "
            f"Focus on: {focus}\n\n"
            f"TEXT:\n{text}\n\n"
            f"Provide 4-6 concise bullet points."
        )

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",   # fast + cheap for sub-tasks
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text
