"""Unit tests for bk-recall search and summarizer modules."""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Setup paths for imports
test_dir = os.path.dirname(__file__)
scripts_dir = os.path.join(test_dir, "../scripts")
lib_dir = os.path.join(test_dir, "../../lib")
sys.path.insert(0, scripts_dir)
sys.path.insert(0, lib_dir)


class TestSearchHandler:
    """Tests for semantic search handler."""

    def test_init_creates_instance(self):
        """Test SearchHandler initialization."""
        from search_handler import SearchHandler
        handler = SearchHandler()
        assert handler.embedder is None
        assert handler.search is None

    @patch("search_handler.VaultSearch")
    @patch("search_handler.GeminiEmbedder")
    def test_ensure_initialized_creates_embedder(self, mock_embedder_class, mock_search_class):
        """Test lazy initialization creates embedder and search."""
        from search_handler import SearchHandler
        mock_embedder = MagicMock()
        mock_embedder_class.return_value = mock_embedder
        mock_search = MagicMock()
        mock_search_class.return_value = mock_search

        handler = SearchHandler()
        handler._ensure_initialized()

        assert handler.embedder == mock_embedder
        assert handler.search == mock_search
        mock_embedder_class.assert_called_once()
        mock_search_class.assert_called_once_with(mock_embedder)

    @patch("search_handler.VaultSearch")
    @patch("search_handler.GeminiEmbedder")
    def test_ensure_initialized_not_repeated(self, mock_embedder_class, mock_search_class):
        """Test lazy initialization happens only once."""
        from search_handler import SearchHandler
        mock_embedder = MagicMock()
        mock_embedder_class.return_value = mock_embedder
        mock_search = MagicMock()
        mock_search_class.return_value = mock_search

        handler = SearchHandler()
        handler._ensure_initialized()
        handler._ensure_initialized()

        assert mock_embedder_class.call_count == 1

    @patch("search_handler.VaultSearch")
    @patch("search_handler.GeminiEmbedder")
    def test_query_searches_all_sources(self, mock_embedder_class, mock_search_class):
        """Test query searches across all sources."""
        from search_handler import SearchHandler
        mock_embedder = MagicMock()
        mock_embedder_class.return_value = mock_embedder
        mock_search = MagicMock()
        mock_search_class.return_value = mock_search

        mock_results = [MagicMock(), MagicMock()]
        mock_search.query.return_value = mock_results

        handler = SearchHandler()
        results = handler.query("test query", top_k=5, min_score=0.5)

        assert results == mock_results
        mock_search.query.assert_called_once_with("test query", 5, 0.5)

    @patch("search_handler.VaultSearch")
    @patch("search_handler.GeminiEmbedder")
    def test_query_with_source_filter(self, mock_embedder_class, mock_search_class):
        """Test query with source filter."""
        from search_handler import SearchHandler
        mock_embedder = MagicMock()
        mock_embedder_class.return_value = mock_embedder
        mock_search = MagicMock()
        mock_search_class.return_value = mock_search

        mock_results = [MagicMock()]
        mock_search.query_by_source.return_value = mock_results

        handler = SearchHandler()
        results = handler.query("test", source="email", top_k=10)

        assert results == mock_results
        mock_search.query_by_source.assert_called_once_with("test", "email", 10, 0.3)

    def test_format_results_empty_list(self):
        """Test formatting empty search results."""
        from search_handler import SearchHandler
        handler = SearchHandler()
        output = handler.format_results([])

        assert "No results found" in output

    def test_format_results_single_result(self):
        """Test formatting single search result."""
        from search_handler import SearchHandler
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="test-1",
            source="email",
            title="Test Subject",
            content="This is test content"
        )
        result = SearchResult(item=item, score=0.85)

        handler = SearchHandler()
        output = handler.format_results([result])

        assert "Search Results (1 found)" in output
        assert "Test Subject" in output
        assert "email" in output
        assert "0.85" in output
        assert "This is test" in output

    def test_format_results_multiple_results(self):
        """Test formatting multiple search results."""
        from search_handler import SearchHandler
        from vault import VaultItem, SearchResult
        items = [
            VaultItem(
                id="test-1",
                source="email",
                title="Email Subject",
                content="Email content"
            ),
            VaultItem(
                id="test-2",
                source="backlog",
                title="Task Title",
                content="Task description"
            )
        ]
        results = [
            SearchResult(item=items[0], score=0.95),
            SearchResult(item=items[1], score=0.75)
        ]

        handler = SearchHandler()
        output = handler.format_results(results)

        assert "Search Results (2 found)" in output
        assert "Email Subject" in output
        assert "Task Title" in output
        assert "0.95" in output
        assert "0.75" in output

    def test_format_results_with_metadata(self):
        """Test formatting results includes metadata."""
        from search_handler import SearchHandler
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="email-123",
            source="email",
            title="Subject",
            content="Content",
            metadata={
                "from": "sender@example.com",
                "date": "2026-01-30"
            }
        )
        result = SearchResult(item=item, score=0.85)

        handler = SearchHandler()
        output = handler.format_results([result])

        assert "Meta:" in output
        assert "sender@example.com" in output

    def test_format_results_verbose_mode(self):
        """Test verbose mode includes full content."""
        from search_handler import SearchHandler
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="test-1",
            source="email",
            title="Subject",
            content="x" * 300
        )
        result = SearchResult(item=item, score=0.85)

        handler = SearchHandler()
        output = handler.format_results([result], verbose=True)

        assert "```" in output
        assert "..." in output

    def test_format_results_preview_mode(self):
        """Test preview mode truncates content."""
        from search_handler import SearchHandler
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="test-1",
            source="email",
            title="Subject",
            content="This is a very long content that should be truncated in preview mode"
        )
        result = SearchResult(item=item, score=0.85)

        handler = SearchHandler()
        output = handler.format_results([result], verbose=False)

        assert "Preview:" in output
        assert "..." in output

    def test_format_results_handles_none_title(self):
        """Test formatting handles items without title."""
        from search_handler import SearchHandler
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="test-1",
            source="email",
            title=None,
            content="Content without title"
        )
        result = SearchResult(item=item, score=0.85)

        handler = SearchHandler()
        output = handler.format_results([result])

        assert "(No title)" in output


class TestSummarizer:
    """Tests for context summarizer."""

    def test_init_creates_search_handler(self):
        """Test Summarizer initialization."""
        from summarizer import Summarizer
        summarizer = Summarizer()
        assert summarizer.search is not None

    @patch("summarizer.SearchHandler.query")
    def test_summarize_with_topic(self, mock_query):
        """Test summarize with specific topic."""
        from summarizer import Summarizer
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="test-1",
            source="email",
            title="Test",
            content="Content"
        )
        mock_query.return_value = [SearchResult(item=item, score=0.85)]

        summarizer = Summarizer()
        summary = summarizer.summarize(topic="test topic", source="email", top_k=10)

        assert "test topic" in summary
        assert "Context Summary" in summary

    @patch("summarizer.SearchHandler.query")
    def test_summarize_without_topic(self, mock_query):
        """Test summarize without topic uses default."""
        from summarizer import Summarizer
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="test-1",
            source="backlog",
            title="Status Update",
            content="Project status"
        )
        mock_query.return_value = [SearchResult(item=item, score=0.75)]

        summarizer = Summarizer()
        summary = summarizer.summarize()

        assert "Project Context Summary" in summary

    @patch("summarizer.SearchHandler.query")
    def test_summarize_no_results(self, mock_query):
        """Test summarize with no results."""
        from summarizer import Summarizer
        mock_query.return_value = []

        summarizer = Summarizer()
        summary = summarizer.summarize(topic="nonexistent")

        assert "No relevant context found" in summary

    @patch("summarizer.SearchHandler.query")
    def test_build_summary_groups_by_source(self, mock_query):
        """Test summary groups items by source."""
        from summarizer import Summarizer
        from vault import VaultItem, SearchResult
        items = [
            VaultItem(
                id="email-1",
                source="email",
                title="Email 1",
                content="Email content 1"
            ),
            VaultItem(
                id="email-2",
                source="email",
                title="Email 2",
                content="Email content 2"
            ),
            VaultItem(
                id="backlog-1",
                source="backlog",
                title="Task 1",
                content="Task content"
            )
        ]
        results = [
            SearchResult(item=items[0], score=0.9),
            SearchResult(item=items[1], score=0.85),
            SearchResult(item=items[2], score=0.8)
        ]
        mock_query.return_value = results

        summarizer = Summarizer()
        summary = summarizer.summarize(topic="test")

        assert "Email (2 items)" in summary
        assert "Backlog (1 items)" in summary

    @patch("summarizer.SearchHandler.query")
    def test_build_summary_truncates_content(self, mock_query):
        """Test summary truncates content to 150 chars."""
        from summarizer import Summarizer
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="test-1",
            source="email",
            title="Subject",
            content="x" * 300
        )
        mock_query.return_value = [SearchResult(item=item, score=0.85)]

        summarizer = Summarizer()
        summary = summarizer.summarize(topic="test")

        # Content is truncated to 150 chars and "..." is appended
        assert "x" * 151 not in summary
        assert "..." in summary

    @patch("summarizer.SearchHandler.query")
    def test_build_summary_includes_stats(self, mock_query):
        """Test summary includes statistics."""
        from summarizer import Summarizer
        from vault import VaultItem, SearchResult
        items = [
            VaultItem(
                id="email-1",
                source="email",
                title="Email",
                content="Content"
            ),
            VaultItem(
                id="backlog-1",
                source="backlog",
                title="Task",
                content="Content"
            )
        ]
        results = [
            SearchResult(item=items[0], score=0.9),
            SearchResult(item=items[1], score=0.8)
        ]
        mock_query.return_value = results

        summarizer = Summarizer()
        summary = summarizer.summarize(topic="test")

        assert "**Total items:** 2" in summary
        assert "**Sources:**" in summary

    @patch("summarizer.SearchHandler.query")
    def test_build_summary_with_many_items(self, mock_query):
        """Test summary limits items per source to 5."""
        from summarizer import Summarizer
        from vault import VaultItem, SearchResult
        items = [
            VaultItem(
                id=f"email-{i}",
                source="email",
                title=f"Email {i}",
                content=f"Content {i}"
            )
            for i in range(10)
        ]
        results = [SearchResult(item=items[i], score=0.9 - (i * 0.01)) for i in range(10)]
        mock_query.return_value = results

        summarizer = Summarizer()
        summary = summarizer.summarize(topic="test")

        assert "Email 0" in summary
        assert "Email 4" in summary
        assert "Email 9" not in summary

    def test_build_summary_handles_missing_title(self):
        """Test summary handles items without title."""
        from summarizer import Summarizer
        item_dict = {
            "source": "email",
            "title": None,
            "content": "Content",
            "score": 0.85
        }

        summarizer = Summarizer()
        summary = summarizer._build_summary("test", [item_dict])

        assert "(No title)" in summary

    @patch("summarizer.SearchHandler.query")
    def test_summarize_with_explicit_top_k(self, mock_query):
        """Test summarize respects top_k parameter."""
        from summarizer import Summarizer
        from vault import VaultItem, SearchResult
        items = [
            VaultItem(
                id=f"test-{i}",
                source="email",
                title=f"Item {i}",
                content="Content"
            )
            for i in range(5)
        ]
        results = [SearchResult(item=items[i], score=0.9 - (i * 0.01)) for i in range(5)]
        mock_query.return_value = results

        summarizer = Summarizer()
        summarizer.summarize(topic="test", top_k=5)

        call_args = mock_query.call_args
        assert call_args[1]["top_k"] == 5

    @patch("summarizer.SearchHandler.query")
    def test_summarize_with_source_filter(self, mock_query):
        """Test summarize with source filter."""
        from summarizer import Summarizer
        from vault import VaultItem, SearchResult
        item = VaultItem(
            id="email-1",
            source="email",
            title="Email",
            content="Content"
        )
        mock_query.return_value = [SearchResult(item=item, score=0.85)]

        summarizer = Summarizer()
        summarizer.summarize(topic="test", source="email")

        call_args = mock_query.call_args
        assert call_args[1]["source"] == "email"
