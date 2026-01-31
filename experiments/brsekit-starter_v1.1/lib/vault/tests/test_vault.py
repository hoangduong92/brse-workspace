"""Unit tests for Vault Infrastructure Phase 0."""
import json
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch, Mock

import pytest

from ..db import VaultDB
from ..store import VaultStore, VaultItem
from ..search import VaultSearch, SearchResult
from ..sync_tracker import SyncTracker


# Test data fixtures
SAMPLE_EMBEDDING = [0.1] * 768  # 768-dimensional vector


@pytest.fixture(autouse=True)
def reset_vault_db():
    """Reset VaultDB state before and after each test."""
    import threading
    VaultDB._db_path = None
    VaultDB._sqlite_vec_available = None
    VaultDB._local = threading.local()
    yield
    # Cleanup
    VaultDB.close()
    VaultDB._db_path = None
    VaultDB._sqlite_vec_available = None
    VaultDB._local = threading.local()


@pytest.fixture
def temp_db() -> Generator[Path, None, None]:
    """Provide temporary database file."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / "test_vault.db"
        yield db_path


@pytest.fixture
def vault_db(temp_db) -> VaultDB:
    """Initialize VaultDB with temporary database."""
    VaultDB.initialize(db_path=temp_db)
    yield VaultDB
    VaultDB.close()


@pytest.fixture
def mock_embedder() -> MagicMock:
    """Create mock embedder that doesn't call real API."""
    embedder = MagicMock()
    embedder.embed = MagicMock(return_value=SAMPLE_EMBEDDING)
    embedder.embed_query = MagicMock(return_value=SAMPLE_EMBEDDING)
    embedder.embed_batch = MagicMock(return_value=[SAMPLE_EMBEDDING] * 3)
    return embedder


@pytest.fixture
def vault_store(vault_db, mock_embedder) -> VaultStore:
    """Initialize VaultStore with mock embedder."""
    return VaultStore(embedder=mock_embedder)


@pytest.fixture
def sync_tracker(vault_db) -> SyncTracker:
    """Initialize SyncTracker with temporary database."""
    return SyncTracker()


# ==============================================================================
# Test Database Initialization
# ==============================================================================

class TestVaultDBInitialization:
    """Tests for VaultDB initialization and schema creation."""

    def test_initialize_creates_database(self, temp_db):
        """Test that initialize creates database file."""
        VaultDB.initialize(db_path=temp_db)
        assert temp_db.exists()
        VaultDB.close()

    def test_initialize_creates_tables(self, temp_db):
        """Test that initialize creates required tables."""
        VaultDB.initialize(db_path=temp_db)
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        # Check vault_items table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='vault_items'"
        )
        assert cursor.fetchone() is not None

        # Check sync_state table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sync_state'"
        )
        assert cursor.fetchone() is not None

    def test_initialize_creates_indexes(self, temp_db):
        """Test that initialize creates required indexes."""
        VaultDB.initialize(db_path=temp_db)
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_vault_source'"
        )
        assert cursor.fetchone() is not None

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_vault_updated'"
        )
        assert cursor.fetchone() is not None

    def test_get_connection_returns_same_connection(self, vault_db):
        """Test that get_connection returns same connection in same thread."""
        conn1 = VaultDB.get_connection()
        conn2 = VaultDB.get_connection()
        assert conn1 is conn2

    def test_connection_has_row_factory(self, vault_db):
        """Test that connection has Row factory enabled."""
        conn = VaultDB.get_connection()
        assert conn.row_factory == sqlite3.Row

    def test_close_closes_connection(self, vault_db):
        """Test that close properly closes database connection."""
        conn = VaultDB.get_connection()
        VaultDB.close()
        assert not hasattr(VaultDB._local, "conn") or VaultDB._local.conn is None


# ==============================================================================
# Test VaultStore - Add Operations
# ==============================================================================

class TestVaultStoreAdd:
    """Tests for VaultStore.add() method."""

    def test_add_basic_item(self, vault_store):
        """Test adding basic vault item without embedding."""
        item = VaultItem(
            id="test-1",
            source="test_source",
            content="Test content",
            title="Test Title"
        )
        result_id = vault_store.add(item)
        assert result_id == "test-1"

    def test_add_item_with_embedding(self, vault_store, mock_embedder):
        """Test adding item with embedding."""
        item = VaultItem(
            id="test-2",
            source="test_source",
            content="Test content for embedding",
            title="Test"
        )
        vault_store.add(item)

        # Verify embedder was called
        mock_embedder.embed.assert_called_with("Test content for embedding")

    def test_add_item_without_embedder(self, vault_db):
        """Test adding item without embedder (no auto-embedding)."""
        store = VaultStore(embedder=None)
        item = VaultItem(
            id="test-3",
            source="test_source",
            content="Content without embedding",
            title="Test"
        )
        result_id = store.add(item)
        assert result_id == "test-3"

    def test_add_item_with_metadata(self, vault_store):
        """Test adding item with metadata."""
        metadata = {"key": "value", "nested": {"data": 123}}
        item = VaultItem(
            id="test-4",
            source="test_source",
            content="Content with metadata",
            metadata=metadata
        )
        vault_store.add(item)

        # Retrieve and verify metadata
        retrieved = vault_store.get("test-4")
        assert retrieved.metadata == metadata

    def test_add_item_without_title(self, vault_store):
        """Test adding item without optional title."""
        item = VaultItem(
            id="test-5",
            source="test_source",
            content="Content without title"
        )
        vault_store.add(item)

        retrieved = vault_store.get("test-5")
        assert retrieved.title is None

    def test_add_item_sets_timestamps(self, vault_store):
        """Test that add sets created_at and updated_at timestamps."""
        item = VaultItem(
            id="test-6",
            source="test_source",
            content="Content with timestamps"
        )
        before_add = datetime.now()
        vault_store.add(item)
        after_add = datetime.now()

        retrieved = vault_store.get("test-6")
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None
        assert before_add <= retrieved.created_at <= after_add

    def test_add_multiple_items(self, vault_store):
        """Test adding multiple items."""
        for i in range(5):
            item = VaultItem(
                id=f"test-{i}",
                source="test_source",
                content=f"Content {i}"
            )
            vault_store.add(item)

        # Verify all items exist
        for i in range(5):
            assert vault_store.get(f"test-{i}") is not None

    def test_add_empty_content_still_added(self, vault_store):
        """Test that item with empty content is added."""
        item = VaultItem(
            id="test-empty",
            source="test_source",
            content=""
        )
        result_id = vault_store.add(item)
        assert result_id == "test-empty"

    def test_add_handles_embedding_failure_gracefully(self, vault_store, mock_embedder):
        """Test that embedding failure doesn't prevent item from being added."""
        mock_embedder.embed.side_effect = Exception("API Error")

        item = VaultItem(
            id="test-embedding-fail",
            source="test_source",
            content="Content that fails embedding"
        )
        result_id = vault_store.add(item)

        # Item should still be added despite embedding failure
        assert result_id == "test-embedding-fail"
        retrieved = vault_store.get("test-embedding-fail")
        assert retrieved is not None
        assert retrieved.embedding is None


# ==============================================================================
# Test VaultStore - Retrieve Operations
# ==============================================================================

class TestVaultStoreGet:
    """Tests for VaultStore.get() method."""

    def test_get_existing_item(self, vault_store):
        """Test retrieving existing item."""
        original = VaultItem(
            id="get-1",
            source="test_source",
            content="Content to retrieve",
            title="Test Title"
        )
        vault_store.add(original)

        retrieved = vault_store.get("get-1")
        assert retrieved is not None
        assert retrieved.id == "get-1"
        assert retrieved.content == "Content to retrieve"
        assert retrieved.title == "Test Title"

    def test_get_nonexistent_item(self, vault_store):
        """Test retrieving non-existent item returns None."""
        result = vault_store.get("nonexistent")
        assert result is None

    def test_get_preserves_all_fields(self, vault_store):
        """Test that get preserves all item fields."""
        metadata = {"key": "value"}
        original = VaultItem(
            id="get-2",
            source="test_source",
            content="Full content",
            title="Full Title",
            metadata=metadata
        )
        vault_store.add(original)

        retrieved = vault_store.get("get-2")
        assert retrieved.id == original.id
        assert retrieved.source == original.source
        assert retrieved.content == original.content
        assert retrieved.title == original.title
        assert retrieved.metadata == metadata


# ==============================================================================
# Test VaultStore - Update Operations
# ==============================================================================

class TestVaultStoreUpdate:
    """Tests for VaultStore.update() method."""

    def test_update_title(self, vault_store):
        """Test updating item title."""
        item = VaultItem(
            id="update-1",
            source="test_source",
            content="Original content",
            title="Original Title"
        )
        vault_store.add(item)

        vault_store.update("update-1", title="Updated Title")

        retrieved = vault_store.get("update-1")
        assert retrieved.title == "Updated Title"
        assert retrieved.content == "Original content"

    def test_update_content(self, vault_store):
        """Test updating item content."""
        item = VaultItem(
            id="update-2",
            source="test_source",
            content="Original content"
        )
        vault_store.add(item)

        vault_store.update("update-2", content="Updated content")

        retrieved = vault_store.get("update-2")
        assert retrieved.content == "Updated content"

    def test_update_metadata(self, vault_store):
        """Test updating item metadata."""
        original_metadata = {"key": "value"}
        item = VaultItem(
            id="update-3",
            source="test_source",
            content="Content",
            metadata=original_metadata
        )
        vault_store.add(item)

        new_metadata = {"key": "new_value", "extra": "data"}
        vault_store.update("update-3", metadata=new_metadata)

        retrieved = vault_store.get("update-3")
        assert retrieved.metadata == new_metadata

    def test_update_sets_updated_at(self, vault_store):
        """Test that update sets updated_at timestamp."""
        item = VaultItem(
            id="update-4",
            source="test_source",
            content="Content"
        )
        vault_store.add(item)

        original = vault_store.get("update-4")

        # Wait a tiny bit to ensure timestamp difference
        import time
        time.sleep(0.01)

        vault_store.update("update-4", title="New Title")

        updated = vault_store.get("update-4")
        assert updated.updated_at > original.updated_at

    def test_update_nonexistent_item(self, vault_store):
        """Test updating non-existent item returns False."""
        result = vault_store.update("nonexistent", title="New Title")
        assert result is False

    def test_update_with_empty_kwargs(self, vault_store):
        """Test update with no fields returns False."""
        item = VaultItem(
            id="update-5",
            source="test_source",
            content="Content"
        )
        vault_store.add(item)

        result = vault_store.update("update-5")
        assert result is False


# ==============================================================================
# Test VaultStore - Delete Operations
# ==============================================================================

class TestVaultStoreDelete:
    """Tests for VaultStore.delete() method."""

    def test_delete_existing_item(self, vault_store):
        """Test deleting existing item."""
        item = VaultItem(
            id="delete-1",
            source="test_source",
            content="Content to delete"
        )
        vault_store.add(item)

        result = vault_store.delete("delete-1")
        assert result is True

        # Verify item is deleted
        assert vault_store.get("delete-1") is None

    def test_delete_nonexistent_item(self, vault_store):
        """Test deleting non-existent item returns False."""
        result = vault_store.delete("nonexistent")
        assert result is False

    def test_delete_multiple_items(self, vault_store):
        """Test deleting multiple items."""
        for i in range(3):
            item = VaultItem(
                id=f"delete-{i}",
                source="test_source",
                content=f"Content {i}"
            )
            vault_store.add(item)

        for i in range(3):
            vault_store.delete(f"delete-{i}")

        for i in range(3):
            assert vault_store.get(f"delete-{i}") is None


# ==============================================================================
# Test VaultStore - List Operations
# ==============================================================================

class TestVaultStoreList:
    """Tests for VaultStore.list_by_source() method."""

    def test_list_by_source_returns_items(self, vault_store):
        """Test listing items by source."""
        for i in range(3):
            item = VaultItem(
                id=f"list-{i}",
                source="source_a",
                content=f"Content {i}"
            )
            vault_store.add(item)

        items = vault_store.list_by_source("source_a")
        assert len(items) == 3

    def test_list_by_source_filters_correctly(self, vault_store):
        """Test that list_by_source filters by source."""
        for i in range(2):
            item = VaultItem(
                id=f"list-a-{i}",
                source="source_a",
                content=f"Content A {i}"
            )
            vault_store.add(item)

        for i in range(3):
            item = VaultItem(
                id=f"list-b-{i}",
                source="source_b",
                content=f"Content B {i}"
            )
            vault_store.add(item)

        items_a = vault_store.list_by_source("source_a")
        items_b = vault_store.list_by_source("source_b")

        assert len(items_a) == 2
        assert len(items_b) == 3

    def test_list_by_source_respects_limit(self, vault_store):
        """Test that list_by_source respects limit parameter."""
        for i in range(10):
            item = VaultItem(
                id=f"list-limit-{i}",
                source="test_source",
                content=f"Content {i}"
            )
            vault_store.add(item)

        items = vault_store.list_by_source("test_source", limit=5)
        assert len(items) == 5

    def test_list_by_source_respects_offset(self, vault_store):
        """Test that list_by_source respects offset parameter."""
        for i in range(10):
            item = VaultItem(
                id=f"list-offset-{i}",
                source="test_source",
                content=f"Content {i}"
            )
            vault_store.add(item)

        items_first = vault_store.list_by_source("test_source", limit=3, offset=0)
        items_second = vault_store.list_by_source("test_source", limit=3, offset=3)

        assert len(items_first) == 3
        assert len(items_second) == 3
        assert items_first[0].id != items_second[0].id

    def test_list_empty_source(self, vault_store):
        """Test listing items from empty source returns empty list."""
        items = vault_store.list_by_source("empty_source")
        assert items == []

    def test_list_ordered_by_updated_at(self, vault_store):
        """Test that list results are ordered by updated_at descending."""
        import time

        ids = []
        for i in range(3):
            item = VaultItem(
                id=f"list-order-{i}",
                source="test_source",
                content=f"Content {i}"
            )
            vault_store.add(item)
            ids.append(f"list-order-{i}")
            time.sleep(0.01)

        items = vault_store.list_by_source("test_source")

        # Most recent first
        assert items[0].updated_at >= items[1].updated_at >= items[2].updated_at


# ==============================================================================
# Test VaultSearch with Mocked Embeddings
# ==============================================================================

class TestVaultSearch:
    """Tests for VaultSearch semantic search functionality."""

    @pytest.fixture
    def vault_search(self, vault_store, mock_embedder):
        """Initialize VaultSearch with mock embedder."""
        search = VaultSearch(embedder=mock_embedder)
        search.store = vault_store
        return search

    def test_search_returns_results(self, vault_store, vault_search):
        """Test that search returns matching items."""
        # Add items with embeddings
        for i in range(3):
            item = VaultItem(
                id=f"search-{i}",
                source="test_source",
                content=f"Content about testing {i}",
                embedding=SAMPLE_EMBEDDING
            )
            vault_store.add(item)

        results = vault_search.query("testing")
        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)

    def test_search_result_has_score(self, vault_store, vault_search):
        """Test that search results include similarity scores."""
        item = VaultItem(
            id="search-score",
            source="test_source",
            content="Test content",
            embedding=SAMPLE_EMBEDDING
        )
        vault_store.add(item)

        results = vault_search.query("test")
        assert len(results) > 0
        assert hasattr(results[0], "score")
        assert 0.0 <= results[0].score <= 1.0

    def test_search_by_source_filters(self, vault_store, vault_search):
        """Test that search_by_source filters results."""
        for i in range(2):
            item = VaultItem(
                id=f"search-src-a-{i}",
                source="source_a",
                content="Test content",
                embedding=SAMPLE_EMBEDDING
            )
            vault_store.add(item)

        for i in range(3):
            item = VaultItem(
                id=f"search-src-b-{i}",
                source="source_b",
                content="Test content",
                embedding=SAMPLE_EMBEDDING
            )
            vault_store.add(item)

        results = vault_search.query_by_source("test", source="source_a")
        assert all(r.item.source == "source_a" for r in results)

    def test_search_respects_top_k(self, vault_store, vault_search):
        """Test that search respects top_k limit."""
        for i in range(10):
            item = VaultItem(
                id=f"search-topk-{i}",
                source="test_source",
                content="Test content",
                embedding=SAMPLE_EMBEDDING
            )
            vault_store.add(item)

        results = vault_search.query("test", top_k=5)
        assert len(results) <= 5

    def test_search_respects_min_score(self, vault_store, vault_search):
        """Test that search respects min_score threshold."""
        # Create embeddings with varying similarity
        low_similarity = [0.1] * 768
        high_similarity = [0.9] * 768

        item_low = VaultItem(
            id="search-low",
            source="test_source",
            content="Low similarity content",
            embedding=low_similarity
        )
        item_high = VaultItem(
            id="search-high",
            source="test_source",
            content="High similarity content",
            embedding=high_similarity
        )
        vault_store.add(item_low)
        vault_store.add(item_high)

        # Search with high min_score should return fewer or zero results
        results = vault_search.query("test", min_score=0.9)
        # Results depend on cosine similarity calculation
        assert all(r.score >= 0.9 for r in results)

    def test_search_empty_vault(self, vault_search):
        """Test searching empty vault returns empty results."""
        results = vault_search.query("anything")
        assert results == []

    def test_search_items_without_embeddings_ignored(self, vault_store, vault_search):
        """Test that items without embeddings are ignored in search."""
        # Add item without embedding
        item = VaultItem(
            id="search-no-embedding",
            source="test_source",
            content="Content without embedding"
        )
        vault_store.add(item)

        results = vault_search.query("test")
        assert all(r.item.embedding is not None for r in results)

    def test_cosine_similarity_calculation(self, vault_search):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        # Identical vectors have similarity 1.0
        score = vault_search._cosine_similarity(vec1, vec2)
        assert abs(score - 1.0) < 0.0001

        # Orthogonal vectors have similarity 0.0
        score = vault_search._cosine_similarity(vec1, vec3)
        assert abs(score) < 0.0001

    def test_cosine_similarity_different_dimensions_raises(self, vault_search):
        """Test that cosine similarity raises on dimension mismatch."""
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        with pytest.raises(ValueError, match="same dimension"):
            vault_search._cosine_similarity(vec1, vec2)

    def test_cosine_similarity_zero_magnitude_vectors(self, vault_search):
        """Test cosine similarity with zero magnitude vectors."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        score = vault_search._cosine_similarity(vec1, vec2)
        assert score == 0.0


# ==============================================================================
# Test SyncTracker
# ==============================================================================

class TestSyncTracker:
    """Tests for SyncTracker sync state management."""

    def test_update_sync_stores_timestamp(self, sync_tracker):
        """Test that update_sync stores timestamp."""
        now = datetime.now()
        sync_tracker.update_sync("source_a", now)

        retrieved = sync_tracker.get_last_sync("source_a")
        assert retrieved is not None
        # Allow small time difference due to ISO format conversion
        assert abs((retrieved - now).total_seconds()) < 1

    def test_get_last_sync_returns_none_for_unknown_source(self, sync_tracker):
        """Test that get_last_sync returns None for unknown source."""
        result = sync_tracker.get_last_sync("unknown_source")
        assert result is None

    def test_update_sync_overwrites_previous(self, sync_tracker):
        """Test that update_sync overwrites previous timestamp."""
        time1 = datetime.now()
        sync_tracker.update_sync("source_a", time1)

        import time
        time.sleep(0.01)

        time2 = datetime.now()
        sync_tracker.update_sync("source_a", time2)

        retrieved = sync_tracker.get_last_sync("source_a")
        # Should be closer to time2
        assert abs((retrieved - time2).total_seconds()) < abs((retrieved - time1).total_seconds())

    def test_update_sync_with_last_item_id(self, sync_tracker):
        """Test that update_sync stores last_item_id."""
        now = datetime.now()
        sync_tracker.update_sync("source_a", now, last_item_id="item-123")

        retrieved_id = sync_tracker.get_last_item_id("source_a")
        assert retrieved_id == "item-123"

    def test_get_last_item_id_returns_none_for_unknown_source(self, sync_tracker):
        """Test that get_last_item_id returns None for unknown source."""
        result = sync_tracker.get_last_item_id("unknown_source")
        assert result is None

    def test_update_sync_config_stores_config(self, sync_tracker):
        """Test that update_sync_config stores configuration."""
        config = {"key": "value", "nested": {"data": 123}}
        sync_tracker.update_sync_config("source_a", config)

        retrieved = sync_tracker.get_sync_config("source_a")
        assert retrieved == config

    def test_get_sync_config_returns_empty_dict_for_unknown_source(self, sync_tracker):
        """Test that get_sync_config returns empty dict for unknown source."""
        result = sync_tracker.get_sync_config("unknown_source")
        assert result == {}

    def test_update_sync_config_overwrites_previous(self, sync_tracker):
        """Test that update_sync_config overwrites previous config."""
        config1 = {"version": 1}
        sync_tracker.update_sync_config("source_a", config1)

        config2 = {"version": 2, "extra": "data"}
        sync_tracker.update_sync_config("source_a", config2)

        retrieved = sync_tracker.get_sync_config("source_a")
        assert retrieved == config2

    def test_multiple_sources_isolated(self, sync_tracker):
        """Test that multiple sources maintain separate state."""
        time1 = datetime.now()
        time2 = datetime.now() + timedelta(hours=1)

        sync_tracker.update_sync("source_a", time1)
        sync_tracker.update_sync("source_b", time2)

        sync1 = sync_tracker.get_last_sync("source_a")
        sync2 = sync_tracker.get_last_sync("source_b")

        assert abs((sync1 - time1).total_seconds()) < 1
        assert abs((sync2 - time2).total_seconds()) < 1


# ==============================================================================
# Integration Tests
# ==============================================================================

class TestVaultIntegration:
    """Integration tests across vault components."""

    def test_full_workflow(self, vault_store, sync_tracker, mock_embedder):
        """Test complete vault workflow: add, search, update, delete."""
        # Add items
        items = []
        for i in range(3):
            item = VaultItem(
                id=f"workflow-{i}",
                source="integration_test",
                content=f"Content about testing {i}",
                title=f"Test {i}",
                metadata={"index": i}
            )
            vault_store.add(item)
            items.append(item)

        # Verify items exist
        for item in items:
            retrieved = vault_store.get(item.id)
            assert retrieved is not None

        # Update sync tracker
        now = datetime.now()
        sync_tracker.update_sync("integration_test", now, last_item_id="workflow-2")
        assert sync_tracker.get_last_sync("integration_test") is not None
        assert sync_tracker.get_last_item_id("integration_test") == "workflow-2"

        # List items
        listed = vault_store.list_by_source("integration_test")
        assert len(listed) >= 3

        # Update an item
        vault_store.update("workflow-0", title="Updated Test 0")
        updated = vault_store.get("workflow-0")
        assert updated.title == "Updated Test 0"

        # Delete an item
        vault_store.delete("workflow-1")
        assert vault_store.get("workflow-1") is None

    def test_embedding_packing_unpacking(self, vault_db):
        """Test embedding packing and unpacking through store internals."""
        store = VaultStore(embedder=None)

        # Create test embedding
        embedding = [0.5 + i * 0.001 for i in range(768)]

        # Test packing and unpacking
        packed = store._pack_embedding(embedding)
        unpacked = store._unpack_embedding(packed)

        assert len(unpacked) == len(embedding)
        # Verify values match within float32 precision
        assert abs(embedding[0] - unpacked[0]) < 0.0001
        assert abs(embedding[len(embedding)//2] - unpacked[len(embedding)//2]) < 0.0001
        assert abs(embedding[-1] - unpacked[-1]) < 0.0001

    def test_metadata_json_serialization(self, vault_store):
        """Test that metadata is correctly JSON serialized/deserialized."""
        metadata = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"deep": "value"}
        }

        item = VaultItem(
            id="metadata-test",
            source="test_source",
            content="Test",
            metadata=metadata
        )
        vault_store.add(item)

        retrieved = vault_store.get("metadata-test")
        assert retrieved.metadata == metadata

    def test_concurrent_sources_no_interference(self, vault_store):
        """Test that operations on different sources don't interfere."""
        # Add to source A
        for i in range(3):
            item = VaultItem(
                id=f"concurrent-a-{i}",
                source="source_a",
                content=f"Content A {i}"
            )
            vault_store.add(item)

        # Add to source B
        for i in range(2):
            item = VaultItem(
                id=f"concurrent-b-{i}",
                source="source_b",
                content=f"Content B {i}"
            )
            vault_store.add(item)

        # Delete from source A
        vault_store.delete("concurrent-a-0")

        # Verify source B unaffected
        assert len(vault_store.list_by_source("source_b")) == 2
        assert vault_store.get("concurrent-b-0") is not None

        # Verify source A is affected
        assert vault_store.get("concurrent-a-0") is None
        assert len(vault_store.list_by_source("source_a")) == 2
