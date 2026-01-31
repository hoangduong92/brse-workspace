"""Unread detector - detect unread items using last_sync OR fixed cutoff time."""
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .directory_manager import DirectoryManager
from .memory_store import MemoryEntry, MemoryStore
from .metadata_db import MetadataDB, ReadMarkerManager, SyncStateManager


class UnreadDetector:
    """Detect unread items across memory sources.

    Uses cutoff time logic:
    - If last_sync exists and is after 18:00 yesterday → use last_sync
    - Otherwise → use 18:00 yesterday (local time)
    """

    DEFAULT_CUTOFF_HOUR = 18  # 18:00 (6 PM)

    def __init__(
        self,
        project_key: str,
        base_path: Optional[Path] = None,
        cutoff_hour: int = DEFAULT_CUTOFF_HOUR,
    ):
        """Initialize unread detector.

        Args:
            project_key: Unique project identifier
            base_path: Optional base path (default: ~/.brsekit)
            cutoff_hour: Hour for default cutoff (default: 18 = 6 PM)
        """
        self.project_key = project_key
        self.cutoff_hour = cutoff_hour

        # Initialize dependencies
        MetadataDB.initialize()
        self.sync_state = SyncStateManager(project_key)
        self.read_markers = ReadMarkerManager(project_key)
        self.memory_store = MemoryStore(project_key, base_path)
        self.dir_manager = DirectoryManager(base_path)

    def _get_default_cutoff(self) -> datetime:
        """Get default cutoff time (cutoff_hour yesterday)."""
        now = datetime.now()
        yesterday = now.date() - timedelta(days=1)
        return datetime.combine(yesterday, time(self.cutoff_hour, 0))

    def get_cutoff_time(self, source: str) -> datetime:
        """Get cutoff time for unread detection.

        Logic:
        1. Get last_sync timestamp for source
        2. Get default cutoff (18:00 yesterday)
        3. Return the later of the two

        Args:
            source: Source name (backlog, slack, email, meetings)

        Returns:
            Cutoff datetime - items after this are considered unread
        """
        # Get last sync time
        last_sync = self.sync_state.get_last_sync(source)

        # Get last read marker (user explicitly marked as read)
        last_read = self.read_markers.get_last_read(source)

        # Calculate default cutoff
        default_cutoff = self._get_default_cutoff()

        # Find the latest of all timestamps
        candidates = [default_cutoff]
        if last_sync:
            candidates.append(last_sync)
        if last_read:
            candidates.append(last_read)

        return max(candidates)

    def mark_as_read(self, source: str, read_at: Optional[datetime] = None) -> None:
        """Mark source as read.

        Args:
            source: Source name
            read_at: Optional timestamp (default: now)
        """
        self.read_markers.mark_as_read(source, read_at or datetime.now())

    def mark_all_as_read(self, read_at: Optional[datetime] = None) -> None:
        """Mark all sources as read."""
        read_at = read_at or datetime.now()
        for source in DirectoryManager.MEMORY_SOURCES:
            self.read_markers.mark_as_read(source, read_at)

    def get_unread_count(self, source: str) -> int:
        """Count unread entries for source.

        Args:
            source: Source name

        Returns:
            Number of unread entries
        """
        cutoff = self.get_cutoff_time(source)
        cutoff_date = cutoff.date()

        # Read entries from cutoff date to today
        entries = self.memory_store.read_entries(
            source,
            start_date=cutoff_date,
            end_date=date.today(),
        )

        # Count entries after cutoff
        return sum(1 for e in entries if e.timestamp > cutoff)

    def get_unread_entries(
        self,
        source: str,
        limit: int = 100,
    ) -> List[MemoryEntry]:
        """Get unread entries for source.

        Args:
            source: Source name
            limit: Maximum entries to return

        Returns:
            List of unread MemoryEntry, sorted by timestamp descending
        """
        cutoff = self.get_cutoff_time(source)
        cutoff_date = cutoff.date()

        # Read entries from cutoff date to today
        entries = self.memory_store.read_entries(
            source,
            start_date=cutoff_date,
            end_date=date.today(),
        )

        # Filter entries after cutoff
        unread = [e for e in entries if e.timestamp > cutoff]

        # Sort by timestamp descending (newest first)
        unread.sort(key=lambda e: e.timestamp, reverse=True)

        return unread[:limit]

    def get_unread_summary(self) -> Dict[str, int]:
        """Get unread counts per source.

        Returns:
            Dict mapping source to unread count, e.g., {'backlog': 5, 'slack': 12}
        """
        return {
            source: self.get_unread_count(source)
            for source in DirectoryManager.MEMORY_SOURCES
        }

    def get_all_unread_entries(
        self,
        limit_per_source: int = 50,
    ) -> Dict[str, List[MemoryEntry]]:
        """Get unread entries from all sources.

        Args:
            limit_per_source: Max entries per source

        Returns:
            Dict mapping source to list of unread entries
        """
        return {
            source: self.get_unread_entries(source, limit_per_source)
            for source in DirectoryManager.MEMORY_SOURCES
        }

    def has_unread(self, source: Optional[str] = None) -> bool:
        """Check if there are unread items.

        Args:
            source: Optional source to check (if None, check all)

        Returns:
            True if there are unread items
        """
        if source:
            return self.get_unread_count(source) > 0

        return any(
            self.get_unread_count(s) > 0
            for s in DirectoryManager.MEMORY_SOURCES
        )

    def get_cutoff_info(self) -> Dict[str, Dict]:
        """Get cutoff time info for all sources (for debugging).

        Returns:
            Dict with source -> {cutoff, last_sync, last_read, default_cutoff}
        """
        default_cutoff = self._get_default_cutoff()
        all_sync = self.sync_state.get_all_sources()
        all_read = self.read_markers.get_all_read_markers()

        result = {}
        for source in DirectoryManager.MEMORY_SOURCES:
            result[source] = {
                "cutoff": self.get_cutoff_time(source).isoformat(),
                "last_sync": all_sync.get(source, "").isoformat() if source in all_sync else None,
                "last_read": all_read.get(source, "").isoformat() if source in all_read else None,
                "default_cutoff": default_cutoff.isoformat(),
            }

        return result
