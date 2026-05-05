# How to Add a New Tool

Adding a tool to the agent takes about 5 minutes. Follow these steps.

---

## Step 1 — Create the tool file

Create `tools/my_tool.py`:

```python
from tools.base_tool import BaseTool

class MyTool(BaseTool):

    @property
    def name(self) -> str:
        return "my_tool"          # snake_case, unique

    @property
    def description(self) -> str:
        return (
            "One clear paragraph explaining what this tool does, "
            "WHEN Claude should use it, and what its output looks like."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "input_field": {
                    "type": "string",
                    "description": "What this field means.",
                }
            },
            "required": ["input_field"],
        }

    def execute(self, tool_input: dict) -> str:
        value = tool_input.get("input_field", "")
        # ... your logic here ...
        return f"Result: {value}"
```

## Step 2 — Register it

In `tools/tool_registry.py`, add to `_register_defaults()`:

```python
from tools.my_tool import MyTool

for tool in [..., MyTool()]:
    self.register(tool)
```

## Step 3 — Write a test

In `tests/test_tools.py`:

```python
from tools.my_tool import MyTool

class TestMyTool:
    def test_basic(self):
        tool = MyTool()
        result = tool.execute({"input_field": "hello"})
        assert "Result" in result
```

## Step 4 — Run tests

```bash
pytest tests/ -v
```

That's it. Claude will automatically see and use your new tool.

---

## Tips for Great Tool Descriptions

Claude picks tools based entirely on their `description` string. Write it like
you are writing documentation for a smart colleague who will decide whether to
use this tool:

✅ **Good**: "Search the web for up-to-date factual information. Use this when
you need data you don't already know, such as recent events, technical
explanations, or statistics. Returns titles, URLs, and snippets."

❌ **Bad**: "Does a web search."

The more specific the description, the better Claude's tool selection accuracy.
