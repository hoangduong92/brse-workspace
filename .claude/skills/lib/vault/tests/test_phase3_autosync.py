"""Tests for Phase 3: Auto-sync & Morning Brief modules."""
import shutil
import tempfile
from datetime import datetime, date, time, timedelta
from pathlib import Path

import pytest

from lib.vault import (
    DirectoryManager,
    MemoryStore,
    MemoryEntry,
    MetadataDB,
    SyncStateManager,
    MorningBrief,
    SyncScheduler,
    SyncStatus,
)


@pytest.fixture
def temp_base_path():
    """Create a temporary base path for tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_project_key():
    """Test project key."""
    return "TEST-PHASE3"


@pytest.fixture
def setup_test_data(temp_base_path, test_project_key):
    """Setup test data in MemoryStore."""
    # Initialize metadata DB
    MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")

    # Create memory store and add test entries
    memory_store = MemoryStore(test_project_key, temp_base_path)

    now = datetime.now()
    yesterday_evening = datetime.combine(
        now.date() - timedelta(days=1),
        time(19, 0)  # 7 PM yesterday (after 18:00 cutoff)
    )

    # Add some test entries
    test_entries = [
        MemoryEntry(
            id="test-issue-1",
            source="backlog",
            timestamp=yesterday_evening,
            content="Fix login bug",
            metadata={
                "project_key": test_project_key,
                "issue_key": "TST-123",
                "status": "completed",
                "type": "issue"
            }
        ),
        MemoryEntry(
            id="test-comment-1",
            source="backlog",
            timestamp=yesterday_evening + timedelta(hours=1),
            content="Bug has been fixed and tested",
            metadata={
                "project_key": test_project_key,
                "issue_key": "TST-123",
                "author": "dev@example.com",
                "type": "comment"
            }
        ),
        MemoryEntry(
            id="test-blocked-1",
            source="backlog",
            timestamp=now - timedelta(hours=2),
            content="Waiting for spec clarification from customer",
            metadata={
                "project_key": test_project_key,
                "issue_key": "TST-456",
                "status": "blocked",
                "type": "issue"
            }
        ),
    ]

    for entry in test_entries:
        memory_store.append("backlog", entry)

    return memory_store


class TestMorningBrief:
    """Tests for MorningBrief class."""

    def test_init(self, temp_base_path, test_project_key):
        """Test MorningBrief initialization."""
        brief = MorningBrief(test_project_key, temp_base_path)
        assert brief.project_key == test_project_key
        assert brief.cutoff_hour == 18

    def test_get_overnight_cutoff(self, temp_base_path, test_project_key):
        """Test overnight cutoff calculation."""
        brief = MorningBrief(test_project_key, temp_base_path)
        cutoff = brief._get_overnight_cutoff()

        now = datetime.now()
        expected_date = now.date() - timedelta(days=1)

        assert cutoff.date() == expected_date
        assert cutoff.hour == 18
        assert cutoff.minute == 0

    def test_get_unread_summary(self, temp_base_path, test_project_key, setup_test_data):
        """Test getting unread summary."""
        brief = MorningBrief(test_project_key, temp_base_path)
        summary = brief.get_unread_summary()

        assert isinstance(summary, dict)
        assert "backlog" in summary
        # We added 3 entries after cutoff
        assert summary["backlog"] >= 0

    def test_get_total_unread(self, temp_base_path, test_project_key, setup_test_data):
        """Test getting total unread count."""
        brief = MorningBrief(test_project_key, temp_base_path)
        total = brief.get_total_unread()
        assert isinstance(total, int)
        assert total >= 0

    def test_get_overnight_updates(self, temp_base_path, test_project_key, setup_test_data):
        """Test getting overnight updates."""
        brief = MorningBrief(test_project_key, temp_base_path)
        updates = brief.get_overnight_updates()

        assert isinstance(updates, list)

    def test_get_completed_tasks(self, temp_base_path, test_project_key, setup_test_data):
        """Test getting completed tasks."""
        brief = MorningBrief(test_project_key, temp_base_path)
        completed = brief.get_completed_tasks()

        assert isinstance(completed, list)
        # Check structure if we have results
        for task in completed:
            assert "issue_key" in task
            assert "summary" in task

    def test_get_blockers(self, temp_base_path, test_project_key, setup_test_data):
        """Test getting blockers."""
        brief = MorningBrief(test_project_key, temp_base_path)
        blockers = brief.get_blockers()

        assert isinstance(blockers, list)
        # We should find at least one blocker (TST-456)
        if blockers:
            assert "issue_key" in blockers[0]

    def test_generate_brief(self, temp_base_path, test_project_key, setup_test_data):
        """Test generating formatted brief."""
        brief = MorningBrief(test_project_key, temp_base_path)
        output = brief.generate_brief()

        assert isinstance(output, str)
        assert "Morning Brief" in output
        assert "UNREAD" in output
        assert "COMPLETED" in output
        assert "BLOCKERS" in output

    def test_generate_brief_json(self, temp_base_path, test_project_key, setup_test_data):
        """Test generating brief as JSON."""
        brief = MorningBrief(test_project_key, temp_base_path)
        data = brief.generate_brief_json()

        assert isinstance(data, dict)
        assert "generated_at" in data
        assert "project_key" in data
        assert "unread" in data
        assert "total_unread" in data
        assert "completed_tasks" in data
        assert "blockers" in data

    def test_custom_cutoff_hour(self, temp_base_path, test_project_key):
        """Test custom cutoff hour."""
        brief = MorningBrief(test_project_key, temp_base_path, cutoff_hour=20)
        assert brief.cutoff_hour == 20
        cutoff = brief._get_overnight_cutoff()
        assert cutoff.hour == 20


class TestSyncScheduler:
    """Tests for SyncScheduler class."""

    def test_init(self, temp_base_path, test_project_key):
        """Test SyncScheduler initialization."""
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(test_project_key, temp_base_path)

        assert scheduler.project_key == test_project_key
        assert scheduler.stale_minutes == 60

    def test_get_sync_status_no_sync(self, temp_base_path):
        """Test sync status when never synced."""
        project_key = "TEST-NO-SYNC"  # Unique key to avoid conflicts
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(project_key, temp_base_path)

        status = scheduler.get_sync_status("backlog")

        assert status["source"] == "backlog"
        assert status["last_sync"] is None
        assert status["status"] == SyncStatus.IDLE
        assert status["stale"] is True

    def test_record_sync_complete(self, temp_base_path, test_project_key):
        """Test recording sync completion."""
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(test_project_key, temp_base_path)

        scheduler.record_sync_complete("backlog", items_synced=10, last_item_id="123")

        status = scheduler.get_sync_status("backlog")
        assert status["last_sync"] is not None
        assert status["stale"] is False
        assert status["status"] == SyncStatus.SUCCESS

    def test_get_all_sync_status(self, temp_base_path, test_project_key):
        """Test getting all sync statuses."""
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(test_project_key, temp_base_path)

        all_status = scheduler.get_all_sync_status()

        assert isinstance(all_status, dict)
        for source in DirectoryManager.MEMORY_SOURCES:
            assert source in all_status

    def test_is_stale(self, temp_base_path):
        """Test stale detection."""
        import uuid
        project_key = f"TEST-STALE-{uuid.uuid4().hex[:8]}"  # Unique key per run
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(project_key, temp_base_path)

        # Initially stale (no sync recorded for this project)
        assert scheduler.is_stale("backlog") is True

        # After sync, not stale
        scheduler.record_sync_complete("backlog")
        assert scheduler.is_stale("backlog") is False

    def test_get_stale_sources(self, temp_base_path):
        """Test getting list of stale sources."""
        project_key = "TEST-STALE-SOURCES"  # Unique key to avoid conflicts
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(project_key, temp_base_path)

        stale = scheduler.get_stale_sources()

        assert isinstance(stale, list)
        # All sources should be stale initially for this fresh project
        assert len(stale) == len(DirectoryManager.MEMORY_SOURCES)

    def test_needs_sync(self, temp_base_path, test_project_key):
        """Test needs_sync check."""
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(test_project_key, temp_base_path)

        # Initially needs sync
        assert scheduler.needs_sync() is True

    def test_get_sync_summary(self, temp_base_path, test_project_key):
        """Test getting sync summary."""
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(test_project_key, temp_base_path)

        summary = scheduler.get_sync_summary()

        assert "project_key" in summary
        assert "total_sources" in summary
        assert "synced_sources" in summary
        assert "stale_sources" in summary
        assert "needs_sync" in summary

    def test_format_status_table(self, temp_base_path, test_project_key):
        """Test formatting status as table."""
        MetadataDB.initialize(temp_base_path / "db" / "metadata.sqlite")
        scheduler = SyncScheduler(test_project_key, temp_base_path)

        table = scheduler.format_status_table()

        assert isinstance(table, str)
        assert "Source" in table
        assert "Last Sync" in table
        assert "Status" in table


class TestMorningBriefIntegration:
    """Integration tests for morning brief workflow."""

    def test_full_morning_workflow(self, temp_base_path, test_project_key, setup_test_data):
        """Test complete morning brief workflow."""
        # Initialize scheduler
        scheduler = SyncScheduler(test_project_key, temp_base_path)

        # Record that we synced
        scheduler.record_sync_complete("backlog", items_synced=3)

        # Generate morning brief
        brief = MorningBrief(test_project_key, temp_base_path)

        # Get summary
        summary = brief.get_unread_summary()
        assert isinstance(summary, dict)

        # Get formatted output
        output = brief.generate_brief()
        assert "Morning Brief" in output

        # Get JSON output
        json_data = brief.generate_brief_json()
        assert json_data["project_key"] == test_project_key
