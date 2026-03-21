from langchain_core.tools import tool
from config import settings


@tool
def web_search(query: str) -> str:
    """Search the web for current information on any topic.
    Use this when you need up-to-date facts or recent information.
    """
    if settings.has_tavily:
        return _tavily_search(query)
    return _duckduckgo_search(query)


def _tavily_search(query: str) -> str:
    from tavily import TavilyClient
    client = TavilyClient(api_key=settings.tavily_api_key)
    response = client.search(query=query, max_results=settings.max_search_results)
    results = []
    for i, r in enumerate(response.get("results", []), 1):
        results.append(f"[{i}] {r['title']}\nURL: {r['url']}\n{r['content']}")
    return "\n\n---\n\n".join(results)


def _duckduckgo_search(query: str) -> str:
    from ddgs import DDGS
    results = []
    with DDGS() as ddgs:
        for i, r in enumerate(ddgs.text(query, max_results=settings.max_search_results), 1):
            results.append(f"[{i}] {r['title']}\nURL: {r['href']}\n{r['body']}")
    return "\n\n---\n\n".join(results)


SEARCH_TOOLS = [web_search]