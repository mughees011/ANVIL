"""Tools for the research_agent."""

import json
import re
import urllib.request
import urllib.parse
from pydantic import BaseModel
from anvil.tools.registry import tool, Tool


class WikipediaSearchParams(BaseModel):
    query: str


@tool(params_schema=WikipediaSearchParams)
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for the given query and return a summary of the top results."""
    encoded_query = urllib.parse.quote(query)
    url = (
        f"https://en.wikipedia.org/w/api.php"
        f"?action=query&list=search&srsearch={encoded_query}&utf8=&format=json"
    )

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AnvilAgent/1.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            results = data.get("query", {}).get("search", [])

            if not results:
                return "No results found."

            # Extract top 3 snippets, stripping HTML tags
            summaries = []
            for i, res in enumerate(results[:3]):
                clean_snippet = re.sub("<[^<]+>", "", res["snippet"])
                summaries.append(f"{i+1}. {res['title']}: {clean_snippet}")

            return "\n\n".join(summaries)
    except Exception as e:
        return f"Error performing Wikipedia search: {str(e)}"


MY_TOOLS: list[Tool] = [wikipedia_search]  # type: ignore[list-item]
