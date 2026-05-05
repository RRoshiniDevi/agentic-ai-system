"""
wikipedia_tool.py
-----------------
Fetches a concise summary from Wikipedia for a given topic.
Uses the wikipedia-api package — no API key required.
"""

from tools.base_tool import BaseTool
from utils.logger import get_logger

logger = get_logger(__name__)


class WikipediaTool(BaseTool):
    """Fetches a summary article from Wikipedia on any topic."""

    @property
    def name(self) -> str:
        return "wikipedia_search"

    @property
    def description(self) -> str:
        return (
            "Look up a topic on Wikipedia and get a structured summary. "
            "Use this tool when you need reliable encyclopedic background "
            "information on a concept, person, place, technology, or event. "
            "Better than web_search for well-established factual topics. "
            "Input: a topic name. Output: Wikipedia summary with key sections."
        )

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic to look up on Wikipedia (e.g. 'Artificial Intelligence').",
                },
                "sentences": {
                    "type": "integer",
                    "description": "Number of summary sentences to return (default: 5).",
                    "default": 5,
                },
            },
            "required": ["topic"],
        }

    def execute(self, tool_input: dict) -> str:
        topic = tool_input.get("topic", "").strip()
        sentences = tool_input.get("sentences", 5)

        logger.info(f"WikipediaTool: looking up '{topic}'")

        try:
            import wikipedia
            wikipedia.set_lang("en")

            # Search for the best matching page
            search_results = wikipedia.search(topic, results=3)
            if not search_results:
                return f"No Wikipedia article found for '{topic}'."

            # Try to get the page summary
            try:
                summary = wikipedia.summary(
                    search_results[0],
                    sentences=sentences,
                    auto_suggest=False,
                )
                page = wikipedia.page(search_results[0], auto_suggest=False)
                return (
                    f"Wikipedia: {page.title}\n"
                    f"URL: {page.url}\n\n"
                    f"Summary:\n{summary}"
                )
            except wikipedia.DisambiguationError as e:
                # If ambiguous, try the first option
                summary = wikipedia.summary(e.options[0], sentences=sentences)
                return f"Wikipedia ('{e.options[0]}'):\n\n{summary}"

        except ImportError:
            return "ERROR: wikipedia package not installed. Run: pip install wikipedia"
        except Exception as exc:
            return f"ERROR: Wikipedia lookup failed: {type(exc).__name__}: {exc}"
