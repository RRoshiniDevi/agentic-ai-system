"""
examples/research_task.py
--------------------------
Demonstrates using the AgentLoop programmatically for a
technical research task — the primary showcase example.

Run:
    python examples/research_task.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.agent_loop import AgentLoop


def run_research_example():
    """
    Example: Agent researches 'Agentic AI' and writes a report.

    This showcases the full Plan → Act → Observe → Iterate loop:
      Iteration 1: web_search for background on Agentic AI
      Iteration 2: web_search for real-world applications
      Iteration 3: summarize_text to condense the findings
      Iteration 4: write_file to save the report
      Iteration 5: Return final answer
    """

    goal = (
        "Research the concept of Agentic AI systems: "
        "(1) define what an Agentic AI is, "
        "(2) explain the ReAct reasoning pattern, "
        "(3) list 3 real-world applications, "
        "(4) describe current limitations. "
        "Finally, save a concise markdown report to 'agentic_ai_research.md'."
    )

    print("=" * 65)
    print("  EXAMPLE: Technical Research Task")
    print("=" * 65)
    print(f"  Goal: {goal}\n")

    agent = AgentLoop(max_iterations=8, verbose=True)
    result = agent.run(goal=goal)

    print("\n" + "=" * 65)
    print("  AGENT RUN COMPLETE")
    print("=" * 65)
    print(result)


if __name__ == "__main__":
    run_research_example()
