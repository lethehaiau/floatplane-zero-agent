"""
Internet search tool using Tavily (AI-powered) with DuckDuckGo fallback.

Provides search functionality for the agent to access current information.
"""
import logging
from typing import List, Dict
from ddgs import DDGS
from tavily import TavilyClient
from app.config import settings

logger = logging.getLogger(__name__)


def search_internet(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search internet using Tavily (AI summary) or DuckDuckGo (raw results).

    Tries Tavily first for AI-generated answer summary. Falls back to
    DuckDuckGo if Tavily is unavailable or fails.

    Args:
        query: Search query string
        max_results: Maximum number of results (default 5)

    Returns:
        List of search results with title, snippet, link
        - Tavily: Single result with AI-generated answer summary
        - DuckDuckGo: Multiple raw search results
        Returns empty list on error (graceful failure)

    Example:
        >>> results = search_internet("Python tutorial")
        >>> print(results[0]["title"])
        "AI Search Summary" or "Learn Python - Free Interactive Python Tutorial"
    """
    # Try Tavily first (AI-powered search with answer summary)
    if settings.TAVILY_API_KEY:
        try:
            logger.info(f"Using Tavily search for query: '{query}'")
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
                include_answer=True
            )

            # Return AI-generated answer as single result
            if response.get("answer"):
                logger.info(f"Tavily returned AI answer for query: '{query}'", extra={"answer_preview": response['answer'][:100]})
                return [{
                    "title": "AI Search Summary",
                    "snippet": response["answer"],
                    "link": ""
                }]

            logger.info("Tavily returned no answer, falling back to DuckDuckGo", extra={"query": query})

        except Exception as e:
            logger.warning(f"Tavily search failed: {e}, falling back to DuckDuckGo", exc_info=True, extra={"query": query})

    # Fallback to DuckDuckGo
    return _search_with_ddgs(query, max_results)


def _search_with_ddgs(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo and return formatted results.

    Args:
        query: Search query string
        max_results: Maximum number of results

    Returns:
        List of search results with title, snippet, link
        Returns empty list on error
    """
    try:
        logger.info(f"Using DuckDuckGo search for query: '{query}'")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        # Format for LLM consumption
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "link": r.get("href", "")
            })

        logger.info(f"DuckDuckGo returned {len(formatted)} results for query: '{query}'")
        return formatted

    except Exception as e:
        # Silent failure - return empty results
        # LLM can handle missing data gracefully
        logger.error(f"DuckDuckGo search failed: {e}", exc_info=True, extra={"query": query})
        return []
