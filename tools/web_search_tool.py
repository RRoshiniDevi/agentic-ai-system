"""
web_search_tool.py
------------------
Real web search using the Tavily API (https://tavily.com).
Tavily is purpose-built for AI agents and returns clean,
structured results optimised for LLM consumption.

Free tier: 1,000 searches/month — more than enough for a student project.
Get your key at: https://app.tavily.com
"""

import os
from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger(__name__)


class WebSearchTool(BaseTool):
    """Searches the real web using the Tavily API."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Search the web for up-to-date information on any topic. "
            "Use this tool when you need current facts, recent news, "
            "technical explanations, or any information you don't already know. "
            "Input: a concise search query. Output: a list of real web results "
            "with titles, URLs, and content snippets."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (default: 3, max: 5).",
                    "default": 3,
                },
            },
            "required": ["query"],
        }

    def execute(self, tool_input: dict) -> str:
        query = tool_input.get("query", "").strip()
        num_results = min(tool_input.get("num_results", 3), 5)

        logger.info(f"WebSearchTool: searching Tavily for '{query}'")

        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return (
                "ERROR: TAVILY_API_KEY environment variable is not set. "
                "Get a free key at https://app.tavily.com and set it with: "
                "set TAVILY_API_KEY=tvly-your-key-here"
            )

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)

            response = client.search(
                query=query,
                max_results=num_results,
                search_depth="basic",        # use "advanced" for deeper results
                include_answer=True,         # Tavily's own AI summary of results
            )

            formatted = []

            # Include Tavily's own answer if available
            if response.get("answer"):
                formatted.append(f"Quick Answer: {response['answer']}\n")

            # Include individual results
            results = response.get("results", [])
            if not results:
                return f"No results found for query: '{query}'"

            for i, r in enumerate(results, 1):
                formatted.append(
                    f"Result {i}:\n"
                    f"  Title  : {r.get('title', 'N/A')}\n"
                    f"  URL    : {r.get('url', 'N/A')}\n"
                    f"  Snippet: {r.get('content', 'N/A')[:400]}"
                )

            return "\n\n".join(formatted)

        except ImportError:
            return (
                "ERROR: tavily-python package not installed. "
                "Run: pip install tavily-python"
            )
        except Exception as exc:
            return f"ERROR: Tavily search failed: {type(exc).__name__}: {exc}"
