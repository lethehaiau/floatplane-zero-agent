"""
Tool definitions for LLM function calling.

Defines the schemas for tools that the agent can use.
"""

# Search tool definition for LLM function calling
SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_internet",
        "description": (
            "Search the internet for current information, news, weather, or recent events. "
            "Use this when you need up-to-date information that you don't have in your knowledge. "
            "Examples: current weather, recent news, live scores, current prices."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific and concise. Example: 'San Francisco weather today'"
                }
            },
            "required": ["query"]
        }
    }
}

# List of all available tools
AVAILABLE_TOOLS = [SEARCH_TOOL]
