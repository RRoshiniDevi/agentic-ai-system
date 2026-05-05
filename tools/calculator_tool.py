"""
calculator_tool.py
------------------
A safe arithmetic evaluator. Demonstrates that tools don't have
to be API calls – simple utilities count too.

Uses Python's ast module for safe evaluation (no exec/eval on raw strings).
"""

import ast
import operator
from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger(__name__)

# Whitelist of allowed operations
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}


def _safe_eval(node):
    """Recursively evaluate an AST node using only safe operators."""
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Operator {op_type.__name__} is not allowed.")
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
        return SAFE_OPERATORS[type(node.op)](_safe_eval(node.operand))
    else:
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")


class CalculatorTool(BaseTool):
    """Evaluates a mathematical expression and returns the result."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Evaluate a mathematical expression and return the numeric result. "
            "Supports +, -, *, /, **, % and // operators. "
            "Use this tool whenever the user's goal requires arithmetic calculations. "
            "Input: a math expression as a string (e.g. '(100 * 3.14) / 2'). "
            "Output: the computed result."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression to evaluate (e.g. '42 * 1.5').",
                }
            },
            "required": ["expression"],
        }

    def execute(self, tool_input: dict) -> str:
        expression = tool_input.get("expression", "").strip()
        logger.info(f"CalculatorTool: evaluating '{expression}'")

        try:
            tree = ast.parse(expression, mode="eval")
            result = _safe_eval(tree.body)
            return f"{expression} = {result}"
        except ZeroDivisionError:
            return "ERROR: Division by zero."
        except Exception as exc:
            return f"ERROR: Could not evaluate '{expression}': {exc}"
