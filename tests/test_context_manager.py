"""
tests/test_context_manager.py
-----------------------------
Unit tests for the ContextManager (agent's short-term memory).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from memory.context_manager import ContextManager


class TestContextManager:
    def setup_method(self):
        self.ctx = ContextManager()

    def test_set_goal_creates_first_user_message(self):
        self.ctx.set_goal("Test goal")
        messages = self.ctx.get_messages()
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert "Test goal" in messages[0]["content"]

    def test_add_assistant_message(self):
        self.ctx.set_goal("Goal")
        self.ctx.add_assistant_message("I will help you.")
        messages = self.ctx.get_messages()
        assert len(messages) == 2
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "I will help you."

    def test_add_tool_results(self):
        self.ctx.set_goal("Goal")
        tool_results = [
            {"type": "tool_result", "tool_use_id": "abc123", "content": "Result text"}
        ]
        self.ctx.add_tool_results(tool_results)
        messages = self.ctx.get_messages()
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == tool_results

    def test_serialisation_round_trip(self):
        self.ctx.set_goal("Round-trip test")
        self.ctx.add_assistant_message("Assistant says hi")
        data = self.ctx.to_dict()

        new_ctx = ContextManager()
        new_ctx.from_dict(data)

        assert new_ctx.get_goal() == "Round-trip test"
        assert new_ctx.message_count() == 2

    def test_message_count(self):
        self.ctx.set_goal("Count test")
        assert self.ctx.message_count() == 1
        self.ctx.add_assistant_message("One")
        assert self.ctx.message_count() == 2
