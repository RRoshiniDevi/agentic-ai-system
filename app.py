"""
app.py
------
Flask web application that provides a browser-based chat interface
for the Claude Agentic AI system.

Run with:
    python app.py

Then open: http://localhost:5000
"""

import os
import sys
import json
import queue
import threading
from pathlib import Path

from flask import Flask, render_template, request, jsonify, Response, stream_with_context

sys.path.insert(0, str(Path(__file__).parent))

from agent.agent_loop import AgentLoop

app = Flask(__name__)
app.secret_key = os.urandom(24)


def run_agent_streaming(goal: str, q: queue.Queue):
    """
    Run the agent in a background thread, pushing status updates
    into a queue that the SSE endpoint reads from.
    """
    import anthropic
    from agent.planner import Planner
    from agent.observer import Observer
    from memory.context_manager import ContextManager
    from tools.tool_registry import ToolRegistry
    from prompts.templates import SYSTEM_PROMPT, FINAL_ANSWER_PROMPT

    def push(event_type: str, data: dict):
        q.put({"type": event_type, "data": data})

    try:
        client = anthropic.Anthropic()
        model = "claude-sonnet-4-20250514"
        planner = Planner()
        observer = Observer()
        context = ContextManager()
        tools = ToolRegistry()
        max_iterations = 10

        context.set_goal(goal)
        push("status", {"message": f"🚀 Agent started. Goal received."})

        for iteration in range(1, max_iterations + 1):
            push("iteration", {"number": iteration, "max": max_iterations})

            # Plan
            push("thinking", {"message": "Claude is reasoning about the next step..."})
            messages = context.get_messages()
            plan_response = planner.plan(
                client=client,
                model=model,
                system_prompt=SYSTEM_PROMPT,
                messages=messages,
                tools=tools.get_tool_definitions(),
            )

            # Check for final answer
            if plan_response.stop_reason == "end_turn":
                final_text = ""
                for block in plan_response.content:
                    if block.type == "text":
                        final_text += block.text
                if final_text:
                    context.add_assistant_message(final_text)
                    push("final_answer", {"content": final_text})
                    push("done", {"message": "Agent completed successfully!"})
                    return

            # Extract tool uses
            tool_uses = [b for b in plan_response.content if b.type == "tool_use"]
            if not tool_uses:
                break

            context.add_raw_assistant_content(plan_response.content)

            tool_results = []
            for tool_use in tool_uses:
                push("tool_call", {
                    "tool": tool_use.name,
                    "input": tool_use.input,
                })

                observation = observer.observe(
                    tool_registry=tools,
                    tool_name=tool_use.name,
                    tool_input=tool_use.input,
                )

                push("tool_result", {
                    "tool": tool_use.name,
                    "result": str(observation)[:600],
                })

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(observation),
                })

            context.add_tool_results(tool_results)

        # Force final answer if max iterations hit
        messages = context.get_messages()
        messages.append({"role": "user", "content": FINAL_ANSWER_PROMPT})
        response = client.messages.create(
            model=model, max_tokens=2048,
            system=SYSTEM_PROMPT, messages=messages,
        )
        final_text = "".join(b.text for b in response.content if b.type == "text")
        push("final_answer", {"content": final_text or "Agent could not produce a final answer."})
        push("done", {"message": "Agent completed (max iterations reached)."})

    except Exception as exc:
        push("error", {"message": f"Agent error: {type(exc).__name__}: {exc}"})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_agent():
    data = request.get_json()
    goal = (data.get("goal") or "").strip()
    if not goal:
        return jsonify({"error": "No goal provided"}), 400

    q = queue.Queue()
    thread = threading.Thread(target=run_agent_streaming, args=(goal, q), daemon=True)
    thread.start()

    def generate():
        while True:
            try:
                item = q.get(timeout=60)
                yield f"data: {json.dumps(item)}\n\n"
                if item["type"] in ("done", "error"):
                    break
            except queue.Empty:
                yield f"data: {json.dumps({'type': 'error', 'data': {'message': 'Timeout'}})}\n\n"
                break

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.route("/check-key")
def check_key():
    has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
    has_tavily = bool(os.environ.get("TAVILY_API_KEY"))
    return jsonify({"anthropic": has_anthropic, "tavily": has_tavily})


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set.")
        print("Set it with: set ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)
    print("\n✅  Claude Agent Web UI starting...")
    print("📌  Open your browser at: http://localhost:5000\n")
    app.run(debug=False, threaded=True, port=5000)
