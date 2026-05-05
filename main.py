"""
main.py
-------
Entry point for the Claude Agentic AI system.

Usage:
    python main.py
    python main.py --goal "Explain how transformers work in deep learning"
    python main.py --goal "..." --max-iterations 5 --quiet
"""

import argparse
import os
import sys
from pathlib import Path

# Make sure project root is on the path
sys.path.insert(0, str(Path(__file__).parent))

from agent.agent_loop import AgentLoop


DEFAULT_GOAL = (
    "Research the concept of Agentic AI: what it is, how it works, "
    "its key components, real-world applications, and current limitations. "
    "Then write a comprehensive summary report and save it to a file called "
    "'agentic_ai_report.md'."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Claude-based Agentic AI System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--goal",
        type=str,
        default=DEFAULT_GOAL,
        help="The goal for the agent to accomplish.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum number of Plan→Act→Observe cycles (default: 10).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose iteration output.",
    )
    return parser.parse_args()


def check_api_key() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable is not set.")
        print("Set it with: export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)


def main() -> None:
    args = parse_args()
    check_api_key()

    print("\n" + "━" * 60)
    print("  Claude Agentic AI System")
    print("━" * 60)
    print(f"  Goal          : {args.goal[:80]}{'...' if len(args.goal) > 80 else ''}")
    print(f"  Max iterations: {args.max_iterations}")
    print("━" * 60 + "\n")

    agent = AgentLoop(
        max_iterations=args.max_iterations,
        verbose=not args.quiet,
    )

    result = agent.run(goal=args.goal)
    print(result)


if __name__ == "__main__":
    main()
