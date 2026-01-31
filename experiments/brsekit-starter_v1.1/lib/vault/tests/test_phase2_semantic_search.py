"""Tests for BrseKit v2 Phase 2 - Semantic Search modules."""
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from lib.vault.embedding_store import EmbeddingStore
from lib.vault.hybrid_search import HybridSearch
from lib.vault.indexer import Indexer
from lib.vault.directory_manager import DirectoryManager

# Set up test environment
os.environ["GOOGLE_API_KEY"] = "test-key-for-unit-tests"


@pytest.fixture
def temp_base_path():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_embedder():
    """Create mock embedder that returns fake embeddings."""
    embedder = MagicMock()
    embedder.embed.return_value = [0.1] * 768
    embedder.embed_query.return_value = [0.1] * 768
    return embedder


class TestEmbeddingStore:
    """Tests for EmbeddingStore."""

    def test_init_creates_db(self, temp_base_path, mock_embedder):
        """Test EmbeddingStore creates database on init."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            store = EmbeddingStore("TEST-PROJECT", mock_embedder)
            db_path = temp_base_path / ".brsekit" / "db" / "embeddings" / "TEST-PROJECT.db"
            assert db_path.exists()
            store.close()

    def test_index_item(self, temp_base_path, mock_embedder):
        """Test indexing single item."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            store = EmbeddingStore("TEST-PROJECT", mock_embedder)
            result = store.index_item(
                item_id="test-1",
                content="Test content",
                source="backlog",
                layer="memory",
                metadata={"issue": "BKT-123"},
            )
            assert result is True
            mock_embedder.embed.assert_called_once()
            store.close()

    def test_search_returns_results(self, temp_base_path, mock_embedder):
        """Test search returns matching results."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            store = EmbeddingStore("TEST-PROJECT", mock_embedder)
            store.index_item("test-1", "Login bug fix", source="backlog", layer="memory")
            store.index_item("test-2", "Password reset", source="backlog", layer="memory")

            results = store.search("bug", top_k=10, min_score=0.0)
            # Both items have same embedding so both match
            assert len(results) == 2
            store.close()

    def test_search_filter_by_source(self, temp_base_path, mock_embedder):
        """Test search filters by source."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            store = EmbeddingStore("TEST-PROJECT", mock_embedder)
            store.index_item("test-1", "Content A", source="backlog", layer="memory")
            store.index_item("test-2", "Content B", source="slack", layer="memory")

            results = store.search("content", source="backlog", min_score=0.0)
            assert len(results) == 1
            assert results[0].source == "backlog"
            store.close()

    def test_search_filter_by_layer(self, temp_base_path, mock_embedder):
        """Test search filters by layer."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            store = EmbeddingStore("TEST-PROJECT", mock_embedder)
            store.index_item("test-1", "Content A", layer="knowledge")
            store.index_item("test-2", "Content B", layer="memory")

            results = store.search("content", layer="knowledge", min_score=0.0)
            assert len(results) == 1
            assert results[0].layer == "knowledge"
            store.close()

    def test_delete_item(self, temp_base_path, mock_embedder):
        """Test deleting item from index."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            store = EmbeddingStore("TEST-PROJECT", mock_embedder)
            store.index_item("test-1", "Content to delete")

            result = store.delete_item("test-1")
            assert result is True

            results = store.search("Content", min_score=0.0)
            assert len(results) == 0
            store.close()

    def test_get_stats(self, temp_base_path, mock_embedder):
        """Test getting index statistics."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            store = EmbeddingStore("TEST-PROJECT", mock_embedder)
            store.index_item("test-1", "Content A", source="backlog")
            store.index_item("test-2", "Content B", source="slack")

            stats = store.get_stats()
            assert stats["total_items"] == 2
            assert stats["items_with_embedding"] == 2
            assert "backlog" in stats["sources"]
            assert "slack" in stats["sources"]
            store.close()

    def test_keyword_search(self, temp_base_path, mock_embedder):
        """Test FTS5 keyword search."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            store = EmbeddingStore("TEST-PROJECT", mock_embedder)
            store.index_item("test-1", "Login authentication bug", source="backlog")
            store.index_item("test-2", "Password reset feature", source="backlog")

            results = store.keyword_search("authentication", top_k=10)
            assert len(results) >= 1
            assert any("authentication" in r.content.lower() for r in results)
            store.close()


class TestHybridSearch:
    """Tests for HybridSearch."""

    def test_hybrid_search_combines_results(self, temp_base_path, mock_embedder):
        """Test hybrid search combines semantic and keyword results."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            hs = HybridSearch("TEST-PROJECT", mock_embedder)
            hs.embedding_store.index_item("test-1", "Login bug fix")
            hs.embedding_store.index_item("test-2", "Password reset")

            results = hs.search("bug", min_score=0.0)
            assert len(results) >= 1
            hs.embedding_store.close()

    def test_search_knowledge_filters_layer(self, temp_base_path, mock_embedder):
        """Test search_knowledge filters to knowledge layer."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            hs = HybridSearch("TEST-PROJECT", mock_embedder)
            hs.embedding_store.index_item("test-1", "Glossary term", layer="knowledge")
            hs.embedding_store.index_item("test-2", "Memory entry", layer="memory")

            results = hs.search_knowledge("term", min_score=0.0)
            assert all(r.layer == "knowledge" for r in results)
            hs.embedding_store.close()

    def test_search_memory_filters_layer(self, temp_base_path, mock_embedder):
        """Test search_memory filters to memory layer."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            hs = HybridSearch("TEST-PROJECT", mock_embedder)
            hs.embedding_store.index_item("test-1", "Glossary term", layer="knowledge")
            hs.embedding_store.index_item("test-2", "Memory entry", layer="memory")

            results = hs.search_memory("entry", min_score=0.0)
            assert all(r.layer == "memory" for r in results)
            hs.embedding_store.close()

    def test_format_results_markdown(self, temp_base_path, mock_embedder):
        """Test format_results produces markdown."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            hs = HybridSearch("TEST-PROJECT", mock_embedder)
            hs.embedding_store.index_item("test-1", "Test content", source="backlog")

            results = hs.search("test", min_score=0.0)
            output = hs.format_results(results)

            assert "Search Results" in output
            assert "backlog" in output
            hs.embedding_store.close()


class TestIndexer:
    """Tests for Indexer."""

    def test_index_glossary(self, temp_base_path, mock_embedder):
        """Test indexing glossary.json."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            # Set up directory structure
            dm = DirectoryManager()
            dm.ensure_project_structure("TEST-PROJECT")
            knowledge_path = dm.get_knowledge_path("TEST-PROJECT")

            # Create glossary file
            glossary = {
                "API": {"definition": "Application Programming Interface", "aliases": []},
                "BrSE": {"definition": "Bridge Software Engineer", "aliases": ["BSE"]},
            }
            with open(knowledge_path / "glossary.json", "w") as f:
                json.dump(glossary, f)

            # Index
            indexer = Indexer("TEST-PROJECT", mock_embedder)
            counts = indexer.index_knowledge()

            assert counts["glossary"] == 2
            indexer.embedding_store.close()

    def test_index_markdown(self, temp_base_path, mock_embedder):
        """Test indexing markdown files."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            dm = DirectoryManager()
            dm.ensure_project_structure("TEST-PROJECT")
            knowledge_path = dm.get_knowledge_path("TEST-PROJECT")

            # Create FAQ file
            faq_content = """# FAQ

## What is BrseKit?
BrseKit is an AI toolkit for BrSE.

## How to use?
Run /bk-recall search to search.
"""
            with open(knowledge_path / "faq.md", "w") as f:
                f.write(faq_content)

            indexer = Indexer("TEST-PROJECT", mock_embedder)
            counts = indexer.index_knowledge()

            assert counts["faq"] >= 1
            indexer.embedding_store.close()

    def test_index_memory_jsonl(self, temp_base_path, mock_embedder):
        """Test indexing memory JSONL files."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            dm = DirectoryManager()
            dm.ensure_project_structure("TEST-PROJECT")
            memory_path = dm.get_memory_path("TEST-PROJECT", "backlog")

            # Create JSONL file
            entries = [
                {"id": "1", "issueKey": "BKT-123", "summary": "Login bug"},
                {"id": "2", "issueKey": "BKT-124", "summary": "Dashboard fix"},
            ]
            with open(memory_path / "2026-01-30.jsonl", "w") as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")

            indexer = Indexer("TEST-PROJECT", mock_embedder)
            counts = indexer.index_memory(source="backlog")

            assert counts.get("backlog", 0) == 2
            indexer.embedding_store.close()

    def test_get_index_status(self, temp_base_path, mock_embedder):
        """Test getting index status."""
        with patch("pathlib.Path.home", return_value=temp_base_path):
            indexer = Indexer("TEST-PROJECT", mock_embedder)
            indexer.embedding_store.index_item("test-1", "Content", source="backlog")

            status = indexer.get_index_status()
            assert status["project_key"] == "TEST-PROJECT"
            assert status["total_items"] == 1
            indexer.embedding_store.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
