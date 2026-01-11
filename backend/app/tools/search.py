"""
Internet search tool using DuckDuckGo.

Provides search functionality for the agent to access current information.
"""
from typing import List, Dict
from ddgs import DDGS


def search_internet(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo and return formatted results.

    Args:
        query: Search query string
        max_results: Maximum number of results (default 5)

    Returns:
        List of search results with title, snippet, link
        Returns empty list on error (graceful failure)

    Example:
        >>> results = search_internet("Python tutorial")
        >>> print(results[0]["title"])
        "Learn Python - Free Interactive Python Tutorial"
    """
    try:
        print("start searching internet")
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

        return formatted

    except Exception as e:
        # Silent failure - return empty results
        # LLM can handle missing data gracefully
        print(f"Search failed: {e}")
        return []
