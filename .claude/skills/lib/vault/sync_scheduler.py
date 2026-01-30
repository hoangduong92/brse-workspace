"""Sync scheduler - manage periodic syncs across sources."""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .directory_manager import DirectoryManager
from .metadata_db import MetadataDB, SyncStateManager


class SyncStatus:
    """Sync status constants."""
    IDLE = "idle"
    SYNCING = "syncing"
    SUCCESS = "success"
    ERROR = "error"
    STALE = "stale"  # Not synced in a while


class SyncScheduler:
    """Schedule and manage periodic syncs.

    Tracks sync state per source and provides:
    - Sync status reporting
    - Stale detection
    - Auto-sync configuration
    """

    DEFAULT_STALE_MINUTES = 60  # Consider stale if not synced in 60 minutes

    def __init__(
        self,
        project_key: str,
        base_path: Optional[Path] = None,
        stale_minutes: int = DEFAULT_STALE_MINUTES,
    ):
        """Initialize sync scheduler.

        Args:
            project_key: Unique project identifier
            base_path: Optional base path (default: ~/.brsekit)
            stale_minutes: Minutes until sync is considered stale
        """
        self.project_key = project_key
        self.stale_minutes = stale_minutes

        # Initialize dependencies
        MetadataDB.initialize()
        self.sync_state = SyncStateManager(project_key)

    def get_sync_status(self, source: str) -> Dict[str, Any]:
        """Get sync status for a source.

        Args:
            source: Source name (backlog, slack, email, meetings)

        Returns:
            Dict with keys: source, last_sync, items_count, status, stale
        """
        last_sync = self.sync_state.get_last_sync(source)
        last_item_id = self.sync_state.get_last_item_id(source)

        # Determine status
        if last_sync is None:
            status = SyncStatus.IDLE
            stale = True
        else:
            stale_cutoff = datetime.now() - timedelta(minutes=self.stale_minutes)
            stale = last_sync < stale_cutoff
            status = SyncStatus.STALE if stale else SyncStatus.SUCCESS

        return {
            "source": source,
            "last_sync": last_sync.isoformat() if last_sync else None,
            "last_item_id": last_item_id,
            "status": status,
            "stale": stale,
            "stale_minutes": self.stale_minutes,
        }

    def get_all_sync_status(self) -> Dict[str, Dict[str, Any]]:
        """Get sync status for all sources.

        Returns:
            Dict mapping source to status dict
        """
        return {
            source: self.get_sync_status(source)
            for source in DirectoryManager.MEMORY_SOURCES
        }

    def is_stale(self, source: str) -> bool:
        """Check if source sync is stale.

        Args:
            source: Source name

        Returns:
            True if last sync was more than stale_minutes ago
        """
        return self.get_sync_status(source)["stale"]

    def get_stale_sources(self) -> List[str]:
        """Get list of sources that need syncing.

        Returns:
            List of source names that are stale
        """
        return [
            source for source in DirectoryManager.MEMORY_SOURCES
            if self.is_stale(source)
        ]

    def needs_sync(self) -> bool:
        """Check if any source needs syncing.

        Returns:
            True if at least one source is stale
        """
        return len(self.get_stale_sources()) > 0

    def record_sync_start(self, source: str) -> None:
        """Record that a sync has started.

        This can be used to prevent concurrent syncs.

        Args:
            source: Source name
        """
        # Currently just updates the timestamp; could add locking
        pass

    def record_sync_complete(
        self,
        source: str,
        items_synced: int = 0,
        last_item_id: Optional[str] = None,
    ) -> None:
        """Record successful sync completion.

        Args:
            source: Source name
            items_synced: Number of items synced
            last_item_id: Optional ID of last synced item (for incremental sync)
        """
        self.sync_state.update_sync(source, datetime.now(), last_item_id)

    def record_sync_error(self, source: str, error: str) -> None:
        """Record sync error.

        Args:
            source: Source name
            error: Error message
        """
        # Could store error in metadata_db for debugging
        pass

    def get_sync_summary(self) -> Dict[str, Any]:
        """Get summary of all sync states.

        Returns:
            Dict with counts and overall status
        """
        all_status = self.get_all_sync_status()

        stale_count = sum(1 for s in all_status.values() if s["stale"])
        synced_count = sum(1 for s in all_status.values() if s["last_sync"])

        # Find oldest sync
        sync_times = [
            datetime.fromisoformat(s["last_sync"])
            for s in all_status.values()
            if s["last_sync"]
        ]
        oldest_sync = min(sync_times).isoformat() if sync_times else None

        return {
            "project_key": self.project_key,
            "total_sources": len(DirectoryManager.MEMORY_SOURCES),
            "synced_sources": synced_count,
            "stale_sources": stale_count,
            "oldest_sync": oldest_sync,
            "needs_sync": stale_count > 0,
            "sources": all_status,
        }

    def format_status_table(self) -> str:
        """Format sync status as ASCII table.

        Returns:
            Formatted string table
        """
        all_status = self.get_all_sync_status()

        lines = [
            "┌─────────────┬────────────────────┬──────────┬─────────┐",
            "│ Source      │ Last Sync          │ Status   │ Stale   │",
            "├─────────────┼────────────────────┼──────────┼─────────┤",
        ]

        for source, status in all_status.items():
            last_sync = status["last_sync"][:16] if status["last_sync"] else "Never"
            sync_status = status["status"][:8].ljust(8)
            stale = "Yes" if status["stale"] else "No"

            lines.append(
                f"│ {source:<11} │ {last_sync:<18} │ {sync_status} │ {stale:<7} │"
            )

        lines.append("└─────────────┴────────────────────┴──────────┴─────────┘")

        return "\n".join(lines)
