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

<<<<<<< HEAD

SEARCH_TOOLS = [web_search]
=======
@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the local knowledge base for previously researched topics.
    Use this FIRST before searching the web — if relevant information
    exists locally, always prefer it. Only use web_search if this
    returns no relevant results.
    """
    from rag.ingestion import query_knowledge_base
    results = query_knowledge_base(query, n_results=3)
    if results == "No relevant documents found.":
        return "No relevant information in local knowledge base. Use web_search instead."
    return f"From local knowledge base:\n\n{results}"


# Update the export list
SEARCH_TOOLS = [search_knowledge_base, web_search]
>>>>>>> d1fcc8d (RAG + Memory Integration)
