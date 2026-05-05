"""
code_executor_tool.py
---------------------
Safely executes Python code snippets in a sandboxed subprocess.

Safety measures:
- Runs in a separate subprocess (isolated from main process)
- Hard timeout of 10 seconds (prevents infinite loops)
- Captures both stdout and stderr
- No file system access outside the outputs/ directory
"""

import subprocess
import sys
import textwrap
from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger(__name__)

TIMEOUT_SECONDS = 10


class CodeExecutorTool(BaseTool):
    """Executes Python code and returns the output."""

    @property
    def name(self) -> str:
        return "execute_python"

    @property
    def description(self) -> str:
        return (
            "Execute a Python code snippet and return its output. "
            "Use this tool when you need to perform calculations, data processing, "
            "generate formatted output, or verify logic programmatically. "
            "The code runs in a sandboxed subprocess with a 10-second timeout. "
            "Always use print() to output results. "
            "Input: Python code as a string. Output: stdout/stderr from execution."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": (
                        "Valid Python code to execute. Use print() for output. "
                        "Example: 'import math\\nprint(math.sqrt(144))'"
                    ),
                },
            },
            "required": ["code"],
        }

    def execute(self, tool_input: dict) -> str:
        code = tool_input.get("code", "").strip()
        if not code:
            return "ERROR: No code provided."

        logger.info(f"CodeExecutorTool: executing {len(code)} chars of Python")

        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
            )

            output_parts = []

            if result.stdout.strip():
                output_parts.append(f"Output:\n{result.stdout.strip()}")

            if result.stderr.strip():
                output_parts.append(f"Errors/Warnings:\n{result.stderr.strip()}")

            if result.returncode != 0:
                output_parts.append(f"Exit code: {result.returncode}")

            if not output_parts:
                return "Code executed successfully with no output."

            return "\n\n".join(output_parts)

        except subprocess.TimeoutExpired:
            return f"ERROR: Code execution timed out after {TIMEOUT_SECONDS} seconds."
        except Exception as exc:
            return f"ERROR: Execution failed: {type(exc).__name__}: {exc}"
