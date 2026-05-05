"""
file_writer_tool.py
-------------------
Writes content to a local file. Useful when the agent's goal
involves producing a report, saving research findings, or
creating output artefacts.
"""

import os
from pathlib import Path
from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = Path("outputs")


class FileWriterTool(BaseTool):
    """Writes text content to a file in the outputs/ directory."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return (
            "Write text content to a file. Use this tool to save research "
            "findings, reports, or any output that should be persisted to disk. "
            "Files are saved inside the 'outputs/' directory. "
            "Input: filename and content. Output: confirmation message."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": (
                        "Name of the file to write (e.g. 'report.md'). "
                        "Do not include directory paths."
                    ),
                },
                "content": {
                    "type": "string",
                    "description": "The text content to write into the file.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["write", "append"],
                    "description": "Write mode: 'write' (default) replaces, 'append' adds.",
                    "default": "write",
                },
            },
            "required": ["filename", "content"],
        }

    def execute(self, tool_input: dict) -> str:
        filename = tool_input.get("filename", "output.txt").strip()
        content = tool_input.get("content", "")
        mode = tool_input.get("mode", "write")

        # Safety: strip any path separators so the tool can't escape OUTPUT_DIR
        filename = Path(filename).name
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        filepath = OUTPUT_DIR / filename

        file_mode = "a" if mode == "append" else "w"

        with open(filepath, file_mode, encoding="utf-8") as f:
            f.write(content)

        action = "Appended to" if mode == "append" else "Written"
        logger.info(f"FileWriterTool: {action} '{filepath}'")
        return f"{action} {len(content)} characters to '{filepath}'."
