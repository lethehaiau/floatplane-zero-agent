"""
Tests for search tool functionality.

Minimal tests to verify search integration works.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.tools.search import search_internet


class TestSearchTool:
    """Tests for search_internet function."""

    @patch('app.tools.search.DDGS')
    def test_search_returns_formatted_results(self, mock_ddgs):
        """Search should return formatted results with title, snippet, link."""
        # Mock search results
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

        # Configure mock
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_results)
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        # Execute search
        results = search_internet("test query")

        # Verify results
        assert len(results) == 2
        assert results[0]["title"] == "Test Result 1"
        assert results[0]["snippet"] == "This is a test snippet 1"
        assert results[0]["link"] == "https://example.com/1"
        assert results[1]["title"] == "Test Result 2"

    @patch('app.tools.search.DDGS')
    def test_search_respects_max_results(self, mock_ddgs):
        """Search should respect max_results parameter."""
        mock_results = [{"title": f"Result {i}", "body": f"Snippet {i}", "href": f"https://example.com/{i}"} for i in range(10)]

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_results[:3])
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        results = search_internet("test query", max_results=3)

        # Should call with max_results
        mock_ddgs_instance.text.assert_called_once_with("test query", max_results=3)
        assert len(results) == 3

    @patch('app.tools.search.DDGS')
    def test_search_handles_errors_gracefully(self, mock_ddgs):
        """Search should return empty list on error (silent failure)."""
        # Mock search that raises exception
        mock_ddgs.return_value.__enter__.side_effect = Exception("Network error")

        # Should not raise, returns empty list
        results = search_internet("test query")

        assert results == []

    @patch('app.tools.search.DDGS')
    def test_search_handles_missing_fields(self, mock_ddgs):
        """Search should handle missing fields in results."""
        # Mock results with missing fields
        mock_results = [
            {
                "title": "Complete Result",
                "body": "Has all fields",
                "href": "https://example.com"
            },
            {
                # Missing fields
            }
        ]

        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = iter(mock_results)
        mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

        results = search_internet("test query")

        # Should handle missing fields with empty strings
        assert len(results) == 2
        assert results[0]["title"] == "Complete Result"
        assert results[1]["title"] == ""
        assert results[1]["snippet"] == ""
        assert results[1]["link"] == ""
