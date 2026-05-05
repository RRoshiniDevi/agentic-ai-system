# Architecture Deep-Dive

This document explains every design decision in the Claude Agentic AI system.

---

## 1. Why the ReAct Pattern?

ReAct (**Re**ason + **Act**) interleaves reasoning steps with tool calls. This is
superior to pure chain-of-thought (CoT) because:

- The model can **update its beliefs** after seeing real tool output.
- Errors in early steps are recoverable — the model observes the failure and
  tries a different approach.
- The reasoning trace is fully transparent and debuggable.

**Alternative patterns not used here:**
- Plan-and-Execute: generates the full plan upfront, then executes blindly.
  Less flexible when early steps produce unexpected results.
- Self-Ask: only for question decomposition, not general tool use.

---

## 2. Message Protocol

The Anthropic Messages API uses a strict alternating `user / assistant` turn
structure. Our `ContextManager` enforces this:

```
Turn 1 (user):      Goal statement
Turn 2 (assistant): [text block] + [tool_use block(s)]
Turn 3 (user):      [tool_result block(s)]
Turn 4 (assistant): [text block] + [tool_use block(s)]   ← next iteration
Turn 5 (user):      [tool_result block(s)]
...
Turn N (assistant): [text block — final answer]
```

When multiple tools are called in one turn, ALL tool results must be returned
in a single user message. This is why `add_tool_results()` takes a list.

---

## 3. Tool Definition Schema

Tools are described using JSON Schema (a subset). Claude reads these at
inference time and decides which tool to call. Good descriptions are critical:

```python
{
    "name": "web_search",
    "description": "Search the web for ...",   # ← Claude reads this to decide
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"  # ← Claude uses this to format args
            }
        },
        "required": ["query"]
    }
}
```

**Prompt engineering tips for tool descriptions:**
- Lead with WHAT the tool does (not HOW).
- Say explicitly WHEN to use it (and when not to).
- Describe the output format so Claude knows what to expect.

---

## 4. Error Handling Strategy

The `Observer` wraps every tool call in try/except and returns errors as
observation strings rather than crashing the loop. This means:

- Claude sees the error message as an observation.
- Claude can decide to retry with different arguments, use a different tool,
  or proceed with partial information.
- The agent is **self-healing** within the iteration budget.

---

## 5. Memory Architecture

This implementation uses **short-term (in-context) memory** only:

```
ContextManager
└── _messages: list[dict]   ← grows each iteration; sent to Claude every call
```

For production systems, extend this with:

| Memory Type | Use Case | Implementation |
|-------------|----------|---------------|
| Short-term  | Current run | ContextManager (this project) |
| Episodic    | Past runs | SQLite / JSON file store |
| Semantic    | Long-term facts | Vector DB (Chroma, Pinecone) |
| Procedural  | How to do things | Fine-tuning / system prompt |

---

## 6. Model Routing

The system uses two Claude models intentionally:

| Model | Used For | Why |
|-------|----------|-----|
| `claude-sonnet-4-20250514` | Main agent loop | Best reasoning; worth the cost |
| `claude-haiku-4-5-20251001` | `summarize_text` tool | Fast + cheap for sub-tasks |

This pattern — routing simpler sub-tasks to cheaper models — is called
**model cascading** and significantly reduces cost in production.

---

## 7. Extending the System

### Adding long-term memory
Replace `ContextManager.get_messages()` to inject relevant past memories
retrieved from a vector store before sending to Claude.

### Adding a real search API
In `web_search_tool.py`, replace `_mock_search()` with:
```python
from tavily import TavilyClient
client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
results = client.search(query)["results"]
```

### Adding a code execution tool
Subclass `BaseTool`, implement `execute()` to run Python in a sandbox
(e.g., using `subprocess` with a timeout and resource limits).

### Streaming output
Replace `client.messages.create()` in `Planner.plan()` with
`client.messages.stream()` to print Claude's reasoning as it generates.
