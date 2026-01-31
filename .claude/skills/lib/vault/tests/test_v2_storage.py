"""Tests for BrseKit v2 storage modules."""
import gzip
import json
import shutil
import tempfile
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pytest

from lib.vault import (
    DirectoryManager,
    GlossaryEntry,
    KnowledgeStore,
    MemoryEntry,
    MemoryStore,
    MetadataDB,
    ProjectInfo,
    ProjectRegistry,
    ReadMarkerManager,
    SyncStateManager,
    UnreadDetector,
)


@pytest.fixture
def temp_base_path():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_project_key():
    """Test project key."""
    return "TEST-PROJECT"


# ==================== DirectoryManager Tests ====================


class TestDirectoryManager:
    """Tests for DirectoryManager."""

    def test_ensure_project_structure(self, temp_base_path, test_project_key):
        """Test project directory creation."""
        dm = DirectoryManager(temp_base_path)
        project_path = dm.ensure_project_structure(test_project_key)

        assert project_path.exists()
        assert (project_path / "knowledge").exists()
        assert (project_path / "knowledge" / "specs").exists()
        assert (project_path / "memory").exists()
        assert (project_path / "memory" / "backlog").exists()
        assert (project_path / "memory" / "slack").exists()
        assert (project_path / "memory" / "email").exists()
        assert (project_path / "memory" / "meetings").exists()
        assert (project_path / "templates").exists()
        assert (project_path / "archive").exists()

    def test_get_paths(self, temp_base_path, test_project_key):
        """Test path getters."""
        dm = DirectoryManager(temp_base_path)
        dm.ensure_project_structure(test_project_key)

        assert dm.get_knowledge_path(test_project_key).name == "knowledge"
        assert dm.get_memory_path(test_project_key).name == "memory"
        assert dm.get_memory_path(test_project_key, "backlog").name == "backlog"
        assert dm.get_templates_path(test_project_key).name == "templates"
        assert dm.get_archive_path(test_project_key).name == "archive"

    def test_list_projects(self, temp_base_path):
        """Test listing projects."""
        dm = DirectoryManager(temp_base_path)

        assert dm.list_projects() == []

        dm.ensure_project_structure("PROJECT-A")
        dm.ensure_project_structure("PROJECT-B")

        projects = dm.list_projects()
        assert len(projects) == 2
        assert "PROJECT-A" in projects
        assert "PROJECT-B" in projects

    def test_project_exists(self, temp_base_path, test_project_key):
        """Test project existence check."""
        dm = DirectoryManager(temp_base_path)

        assert not dm.project_exists(test_project_key)

        dm.ensure_project_structure(test_project_key)
        assert dm.project_exists(test_project_key)


# ==================== MetadataDB Tests ====================


class TestMetadataDB:
    """Tests for MetadataDB and related managers."""

    def test_initialize_and_connection(self, temp_base_path):
        """Test database initialization."""
        db_path = temp_base_path / "db" / "metadata.sqlite"
        MetadataDB.initialize(db_path)

        conn = MetadataDB.get_connection()
        assert conn is not None

        MetadataDB.close()

    def test_project_registry(self, temp_base_path, test_project_key):
        """Test project registry operations."""
        db_path = temp_base_path / "db" / "metadata.sqlite"
        MetadataDB.initialize(db_path)

        registry = ProjectRegistry()

        # Register project
        created = registry.register(test_project_key, name="Test Project")
        assert created

        # Get project
        project = registry.get(test_project_key)
        assert project is not None
        assert project.project_key == test_project_key
        assert project.name == "Test Project"

        # List projects
        projects = registry.list_all()
        assert test_project_key in projects

        # Update config
        registry.update_config(test_project_key, {"key": "value"})
        project = registry.get(test_project_key)
        assert project.config == {"key": "value"}

        MetadataDB.close()

    def test_sync_state_manager(self, temp_base_path, test_project_key):
        """Test sync state operations."""
        db_path = temp_base_path / "db" / "metadata.sqlite"
        MetadataDB.initialize(db_path)

        manager = SyncStateManager(test_project_key)

        # Initially no sync
        assert manager.get_last_sync("backlog") is None

        # Update sync
        now = datetime.now()
        manager.update_sync("backlog", now, last_item_id="item-123")

        assert manager.get_last_sync("backlog") is not None
        assert manager.get_last_item_id("backlog") == "item-123"

        # Get all sources
        sources = manager.get_all_sources()
        assert "backlog" in sources

        MetadataDB.close()

    def test_read_marker_manager(self, temp_base_path, test_project_key):
        """Test read marker operations."""
        db_path = temp_base_path / "db" / "metadata.sqlite"
        MetadataDB.initialize(db_path)

        manager = ReadMarkerManager(test_project_key)

        # Initially no markers
        assert manager.get_last_read("backlog") is None

        # Mark as read
        now = datetime.now()
        manager.mark_as_read("backlog", now)

        last_read = manager.get_last_read("backlog")
        assert last_read is not None

        # Get all markers
        markers = manager.get_all_read_markers()
        assert "backlog" in markers

        MetadataDB.close()


# ==================== MemoryStore Tests ====================


class TestMemoryStore:
    """Tests for MemoryStore."""

    def test_append_and_read(self, temp_base_path, test_project_key):
        """Test appending and reading entries."""
        store = MemoryStore(test_project_key, temp_base_path)

        entry = MemoryEntry(
            id="test-001",
            source="backlog",
            timestamp=datetime.now(),
            content="Test content",
            metadata={"key": "value"},
        )

        result = store.append("backlog", entry)
        assert result

        entries = store.read_today("backlog")
        assert len(entries) == 1
        assert entries[0].id == "test-001"
        assert entries[0].content == "Test content"

    def test_append_batch(self, temp_base_path, test_project_key):
        """Test batch append."""
        store = MemoryStore(test_project_key, temp_base_path)

        entries = [
            MemoryEntry(
                id=f"test-{i}",
                source="backlog",
                timestamp=datetime.now(),
                content=f"Content {i}",
            )
            for i in range(5)
        ]

        count = store.append_batch("backlog", entries)
        assert count == 5

        read_entries = store.read_today("backlog")
        assert len(read_entries) == 5

    def test_read_date_range(self, temp_base_path, test_project_key):
        """Test reading entries from date range."""
        store = MemoryStore(test_project_key, temp_base_path)

        # Add entries for today
        entry = MemoryEntry(
            id="today-001",
            source="backlog",
            timestamp=datetime.now(),
            content="Today entry",
        )
        store.append("backlog", entry)

        # Read with date range
        entries = store.read_entries(
            "backlog",
            start_date=date.today() - timedelta(days=1),
            end_date=date.today(),
        )
        assert len(entries) >= 1

    def test_compress_old_files(self, temp_base_path, test_project_key):
        """Test gzip compression of old files."""
        store = MemoryStore(test_project_key, temp_base_path)

        # Create entry for 10 days ago
        old_date = date.today() - timedelta(days=10)
        old_timestamp = datetime.combine(old_date, time(12, 0))

        entry = MemoryEntry(
            id="old-001",
            source="backlog",
            timestamp=old_timestamp,
            content="Old entry",
        )
        store.append("backlog", entry)

        # Compress files older than 7 days
        compressed = store.compress_old_files(days_threshold=7)
        assert compressed == 1

        # Verify gzipped file exists
        gzip_path = store._get_gzip_path("backlog", old_date)
        assert gzip_path.exists()

        # Verify original file removed
        jsonl_path = store._get_file_path("backlog", old_date)
        assert not jsonl_path.exists()

        # Verify we can still read the entry
        entries = store._read_date("backlog", old_date)
        assert len(entries) == 1

    def test_archive_old_files(self, temp_base_path, test_project_key):
        """Test archiving old files."""
        store = MemoryStore(test_project_key, temp_base_path)
        dm = DirectoryManager(temp_base_path)

        # Create entry for 35 days ago
        old_date = date.today() - timedelta(days=35)
        old_timestamp = datetime.combine(old_date, time(12, 0))

        entry = MemoryEntry(
            id="archive-001",
            source="backlog",
            timestamp=old_timestamp,
            content="Archive entry",
        )
        store.append("backlog", entry)

        # Archive files older than 30 days
        archived = store.archive_old_files(days_threshold=30)
        assert archived == 1

        # Verify file moved to archive
        archive_path = dm.get_archive_path(test_project_key) / "backlog"
        assert archive_path.exists()
        assert len(list(archive_path.glob("*.jsonl"))) == 1


# ==================== KnowledgeStore Tests ====================


class TestKnowledgeStore:
    """Tests for KnowledgeStore."""

    def test_glossary_operations(self, temp_base_path, test_project_key):
        """Test glossary CRUD."""
        store = KnowledgeStore(test_project_key, temp_base_path)

        # Initially empty
        assert store.get_glossary() == {}

        # Add term
        created = store.add_term("BrSE", "Bridge System Engineer", aliases=["BSE"])
        assert created

        # Get glossary
        glossary = store.get_glossary()
        assert "BrSE" in glossary
        assert "BSE" in glossary  # alias
        assert glossary["BrSE"].definition == "Bridge System Engineer"

        # Update term
        updated = store.add_term("BrSE", "Updated Bridge definition")
        assert not updated  # False = updated, not created

        # Search - should find by term name
        results = store.search_glossary("BrSE")
        assert len(results) == 1

        # Remove term
        removed = store.remove_term("BrSE")
        assert removed
        assert store.get_glossary() == {}

    def test_faq_operations(self, temp_base_path, test_project_key):
        """Test FAQ operations."""
        store = KnowledgeStore(test_project_key, temp_base_path)

        # Initially empty
        assert store.get_faq() == ""

        # Update FAQ
        store.update_faq("# FAQ\n\nTest content")
        assert "Test content" in store.get_faq()

        # Append Q&A
        store.append_faq("What is BrSE?", "Bridge System Engineer")
        faq = store.get_faq()
        assert "What is BrSE?" in faq

    def test_rules_operations(self, temp_base_path, test_project_key):
        """Test rules operations."""
        store = KnowledgeStore(test_project_key, temp_base_path)

        # Initially empty
        assert store.get_rules() == ""

        # Update rules
        store.update_rules("# Rules\n\n1. Rule one")
        assert "Rule one" in store.get_rules()

    def test_specs_operations(self, temp_base_path, test_project_key):
        """Test specs operations."""
        store = KnowledgeStore(test_project_key, temp_base_path)

        # Initially empty
        assert store.list_specs() == []

        # Save spec
        store.save_spec("login-feature", "# Login Feature\n\nSpec content")

        # List specs
        specs = store.list_specs()
        assert "login-feature" in specs

        # Get spec
        content = store.get_spec("login-feature")
        assert "Spec content" in content

        # Search specs
        results = store.search_specs("Login")
        assert "login-feature" in results

        # Delete spec
        deleted = store.delete_spec("login-feature")
        assert deleted
        assert store.list_specs() == []


# ==================== UnreadDetector Tests ====================


class TestUnreadDetector:
    """Tests for UnreadDetector."""

    def test_cutoff_time_default(self, temp_base_path, test_project_key):
        """Test default cutoff time (18:00 yesterday)."""
        detector = UnreadDetector(test_project_key, temp_base_path)

        cutoff = detector.get_cutoff_time("backlog")

        # Should be 18:00 yesterday or later
        yesterday = date.today() - timedelta(days=1)
        expected_default = datetime.combine(yesterday, time(18, 0))

        assert cutoff >= expected_default

    def test_cutoff_time_with_sync(self, temp_base_path, test_project_key):
        """Test cutoff time uses last_sync if later."""
        db_path = temp_base_path / "db" / "metadata.sqlite"
        MetadataDB.initialize(db_path)

        detector = UnreadDetector(test_project_key, temp_base_path)

        # Set last sync to now
        now = datetime.now()
        detector.sync_state.update_sync("backlog", now)

        cutoff = detector.get_cutoff_time("backlog")

        # Should use last_sync since it's more recent
        assert cutoff >= now - timedelta(seconds=1)

        MetadataDB.close()

    def test_unread_count(self, temp_base_path, test_project_key):
        """Test unread count."""
        db_path = temp_base_path / "db" / "metadata.sqlite"
        MetadataDB.initialize(db_path)

        detector = UnreadDetector(test_project_key, temp_base_path)
        store = MemoryStore(test_project_key, temp_base_path)

        # Add entry now (should be unread)
        entry = MemoryEntry(
            id="unread-001",
            source="backlog",
            timestamp=datetime.now(),
            content="Unread entry",
        )
        store.append("backlog", entry)

        # Count should be 1
        count = detector.get_unread_count("backlog")
        assert count == 1

        # Mark as read
        detector.mark_as_read("backlog")

        # Count should be 0
        count = detector.get_unread_count("backlog")
        assert count == 0

        MetadataDB.close()

    def test_unread_summary(self, temp_base_path, test_project_key):
        """Test unread summary across sources."""
        db_path = temp_base_path / "db" / "metadata.sqlite"
        MetadataDB.initialize(db_path)

        detector = UnreadDetector(test_project_key, temp_base_path)

        summary = detector.get_unread_summary()

        # Should have all sources
        assert "backlog" in summary
        assert "slack" in summary
        assert "email" in summary
        assert "meetings" in summary

        MetadataDB.close()

    def test_has_unread(self, temp_base_path, test_project_key):
        """Test has_unread check."""
        db_path = temp_base_path / "db" / "metadata.sqlite"
        MetadataDB.initialize(db_path)

        detector = UnreadDetector(test_project_key, temp_base_path)
        store = MemoryStore(test_project_key, temp_base_path)

        # Initially no unread
        assert not detector.has_unread("backlog")

        # Add unread entry
        entry = MemoryEntry(
            id="unread-002",
            source="backlog",
            timestamp=datetime.now(),
            content="Unread entry",
        )
        store.append("backlog", entry)

        assert detector.has_unread("backlog")
        assert detector.has_unread()  # Check all sources

        MetadataDB.close()
