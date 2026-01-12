"""
Tests for search tool functionality.

Minimal tests to verify search integration works with Tavily and DuckDuckGo fallback.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.tools.search import search_internet, _search_with_ddgs


class TestSearchTool:
    """Tests for search_internet function."""

    @patch('app.tools.search.settings')
    @patch('app.tools.search.TavilyClient')
    def test_tavily_returns_ai_answer(self, mock_tavily_client, mock_settings):
        """Tavily should return AI-generated answer as single result."""
        # Mock Tavily API key configured
        mock_settings.TAVILY_API_KEY = "tvly-test-key"

        # Mock Tavily response with AI answer
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "answer": "The weather in San Francisco today is sunny with temperatures around 65°F.",
            "results": []
        }
        mock_tavily_client.return_value = mock_client

        results = search_internet("weather in SF today")

        # Should return single result with AI answer
        assert len(results) == 1
        assert results[0]["title"] == "AI Search Summary"
        assert "San Francisco" in results[0]["snippet"]
        assert results[0]["link"] == ""

        # Verify Tavily was called
        mock_client.search.assert_called_once()

    @patch('app.tools.search.settings')
    @patch('app.tools.search.TavilyClient')
    @patch('app.tools.search.DDGS')
    def test_tavily_failure_falls_back_to_ddgs(self, mock_ddgs, mock_tavily_client, mock_settings):
        """When Tavily fails, should fallback to DuckDuckGo."""
        # Mock Tavily API key configured
        mock_settings.TAVILY_API_KEY = "tvly-test-key"

        # Mock Tavily failure
        mock_tavily_client.side_effect = Exception("Tavily API error")

        # Mock DuckDuckGo success
        mock_ddgs_results = [
            {"title": "DDG Result", "body": "DDG snippet", "href": "https://example.com"}
        ]
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_ddgs_results)
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        results = search_internet("test query")

        # Should return DuckDuckGo results
        assert len(results) == 1
        assert results[0]["title"] == "DDG Result"
        assert results[0]["snippet"] == "DDG snippet"

    @patch('app.tools.search.settings')
    @patch('app.tools.search.TavilyClient')
    @patch('app.tools.search.DDGS')
    def test_tavily_no_answer_falls_back_to_ddgs(self, mock_ddgs, mock_tavily_client, mock_settings):
        """When Tavily returns no answer, should fallback to DuckDuckGo."""
        # Mock Tavily API key configured
        mock_settings.TAVILY_API_KEY = "tvly-test-key"

        # Mock Tavily response without answer
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "answer": None,
            "results": []
        }
        mock_tavily_client.return_value = mock_client

        # Mock DuckDuckGo success
        mock_ddgs_results = [
            {"title": "DDG Result", "body": "DDG snippet", "href": "https://example.com"}
        ]
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_ddgs_results)
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        results = search_internet("test query")

        # Should return DuckDuckGo results
        assert len(results) == 1
        assert results[0]["title"] == "DDG Result"

    @patch('app.tools.search.settings')
    @patch('app.tools.search.DDGS')
    def test_no_api_key_uses_ddgs_directly(self, mock_ddgs, mock_settings):
        """When no Tavily API key, should use DuckDuckGo directly."""
        # Mock no Tavily API key
        mock_settings.TAVILY_API_KEY = ""

        # Mock DuckDuckGo success
        mock_ddgs_results = [
            {"title": "DDG Result", "body": "DDG snippet", "href": "https://example.com"}
        ]
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_ddgs_results)
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        results = search_internet("test query")

        # Should return DuckDuckGo results
        assert len(results) == 1
        assert results[0]["title"] == "DDG Result"


class TestDuckDuckGoSearch:
    """Tests for _search_with_ddgs function."""

    @patch('app.tools.search.DDGS')
    def test_ddgs_returns_formatted_results(self, mock_ddgs):
        """DuckDuckGo should return formatted results with title, snippet, link."""
        mock_results = [
            {
                "title": "Test Result 1",
                "body": "This is a test snippet 1",
                "href": "https://example.com/1"
            },
            {
                "title": "Test Result 2",
                "body": "This is a test snippet 2",
                "href": "https://example.com/2"
            }
        ]

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_results)
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        results = _search_with_ddgs("test query")

        assert len(results) == 2
        assert results[0]["title"] == "Test Result 1"
        assert results[0]["snippet"] == "This is a test snippet 1"
        assert results[0]["link"] == "https://example.com/1"
        assert results[1]["title"] == "Test Result 2"

    @patch('app.tools.search.DDGS')
    def test_ddgs_respects_max_results(self, mock_ddgs):
        """DuckDuckGo should respect max_results parameter."""
        mock_results = [{"title": f"Result {i}", "body": f"Snippet {i}", "href": f"https://example.com/{i}"} for i in range(10)]

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_results[:3])
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        results = _search_with_ddgs("test query", max_results=3)

        mock_ddgs_instance.text.assert_called_once_with("test query", max_results=3)
        assert len(results) == 3

    @patch('app.tools.search.DDGS')
    def test_ddgs_handles_errors_gracefully(self, mock_ddgs):
        """DuckDuckGo should return empty list on error (silent failure)."""
        mock_ddgs.return_value.__enter__.side_effect = Exception("Network error")

        results = _search_with_ddgs("test query")

        assert results == []

    @patch('app.tools.search.DDGS')
    def test_ddgs_handles_missing_fields(self, mock_ddgs):
        """DuckDuckGo should handle missing fields in results."""
        mock_results = [
            {
                "title": "Complete Result",
                "body": "Has all fields",
                "href": "https://example.com"
            },
            {}  # Missing fields
        ]

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_results)
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        results = _search_with_ddgs("test query")

        assert len(results) == 2
        assert results[0]["title"] == "Complete Result"
        assert results[1]["title"] == ""
        assert results[1]["snippet"] == ""
        assert results[1]["link"] == ""
