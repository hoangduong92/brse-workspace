"""Morning brief generator - daily summary for BrSE."""
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .directory_manager import DirectoryManager
from .memory_store import MemoryEntry, MemoryStore
from .unread_detector import UnreadDetector


class MorningBrief:
    """Generate morning summary for BrSE.

    Provides:
    - Unread counts per source
    - Overnight updates (since 18:00 yesterday)
    - Completed tasks by offshore
    - Current blockers
    """

    DEFAULT_CUTOFF_HOUR = 18  # 18:00 (6 PM)

    def __init__(
        self,
        project_key: str,
        base_path: Optional[Path] = None,
        cutoff_hour: int = DEFAULT_CUTOFF_HOUR,
    ):
        """Initialize morning brief generator.

        Args:
            project_key: Unique project identifier
            base_path: Optional base path (default: ~/.brsekit)
            cutoff_hour: Hour for overnight cutoff (default: 18 = 6 PM)
        """
        self.project_key = project_key
        self.cutoff_hour = cutoff_hour
        self.base_path = base_path

        # Initialize dependencies
        self.memory_store = MemoryStore(project_key, base_path)
        self.unread_detector = UnreadDetector(project_key, base_path, cutoff_hour)
        self.dir_manager = DirectoryManager(base_path)

    def _get_overnight_cutoff(self) -> datetime:
        """Get overnight cutoff time (cutoff_hour yesterday)."""
        now = datetime.now()
        yesterday = now.date() - timedelta(days=1)
        return datetime.combine(yesterday, time(self.cutoff_hour, 0))

    def get_unread_summary(self) -> Dict[str, int]:
        """Get unread counts per source.

        Returns:
            Dict mapping source to unread count, e.g., {'backlog': 5, 'slack': 3}
        """
        return self.unread_detector.get_unread_summary()

    def get_total_unread(self) -> int:
        """Get total unread count across all sources."""
        return sum(self.get_unread_summary().values())

    def get_overnight_updates(self, limit: int = 50) -> List[MemoryEntry]:
        """Get items since overnight cutoff.

        Args:
            limit: Maximum entries to return

        Returns:
            List of MemoryEntry since cutoff, sorted by timestamp descending
        """
        cutoff = self._get_overnight_cutoff()
        cutoff_date = cutoff.date()

        all_entries = []
        for source in DirectoryManager.MEMORY_SOURCES:
            entries = self.memory_store.read_entries(
                source,
                start_date=cutoff_date,
                end_date=date.today(),
            )
            for entry in entries:
                if entry.timestamp > cutoff:
                    all_entries.append(entry)

        # Sort by timestamp descending
        all_entries.sort(key=lambda e: e.timestamp, reverse=True)
        return all_entries[:limit]

    def get_completed_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get tasks completed overnight (from Backlog updates).

        Args:
            limit: Maximum tasks to return

        Returns:
            List of completed task dicts with keys: issue_key, summary, completed_by, completed_at
        """
        cutoff = self._get_overnight_cutoff()
        cutoff_date = cutoff.date()

        # Read backlog entries
        entries = self.memory_store.read_entries(
            "backlog",
            start_date=cutoff_date,
            end_date=date.today(),
        )

        completed = []
        for entry in entries:
            if entry.timestamp <= cutoff:
                continue

            metadata = entry.metadata or {}
            # Check if this is a status change to "Completed" or "Done"
            status = metadata.get("status", "").lower()
            if status in ("completed", "done", "closed", "resolved", "完了"):
                completed.append({
                    "issue_key": metadata.get("issue_key", ""),
                    "summary": entry.content[:100] if entry.content else "",
                    "completed_by": metadata.get("author") or metadata.get("assignee", ""),
                    "completed_at": entry.timestamp,
                    "type": metadata.get("type", "issue"),
                })

        # Sort by completion time descending
        completed.sort(key=lambda t: t["completed_at"], reverse=True)
        return completed[:limit]

    def get_blockers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tasks marked as blocked.

        Args:
            limit: Maximum blockers to return

        Returns:
            List of blocker dicts with keys: issue_key, summary, reason, reported_by
        """
        cutoff = self._get_overnight_cutoff()
        cutoff_date = cutoff.date()

        # Read backlog entries
        entries = self.memory_store.read_entries(
            "backlog",
            start_date=cutoff_date - timedelta(days=7),  # Look back a week for blockers
            end_date=date.today(),
        )

        blockers = []
        seen_keys = set()

        for entry in entries:
            metadata = entry.metadata or {}
            status = metadata.get("status", "").lower()
            issue_key = metadata.get("issue_key", "")

            # Check if blocked status or content mentions blocker
            is_blocked = (
                status in ("blocked", "waiting", "pending", "保留", "待ち")
                or "blocker" in entry.content.lower()
                or "blocked" in entry.content.lower()
                or "待ち" in entry.content
            )

            if is_blocked and issue_key and issue_key not in seen_keys:
                seen_keys.add(issue_key)
                blockers.append({
                    "issue_key": issue_key,
                    "summary": entry.content[:100] if entry.content else "",
                    "reason": metadata.get("reason", "Status marked as blocked"),
                    "reported_by": metadata.get("author", ""),
                    "reported_at": entry.timestamp,
                })

        # Sort by report time descending
        blockers.sort(key=lambda b: b.get("reported_at", datetime.min), reverse=True)
        return blockers[:limit]

    def get_in_progress_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get tasks currently in progress.

        Args:
            limit: Maximum tasks to return

        Returns:
            List of in-progress task dicts
        """
        entries = self.memory_store.read_entries(
            "backlog",
            start_date=date.today() - timedelta(days=7),
            end_date=date.today(),
        )

        in_progress = []
        seen_keys = set()

        for entry in entries:
            metadata = entry.metadata or {}
            status = metadata.get("status", "").lower()
            issue_key = metadata.get("issue_key", "")

            is_in_progress = status in (
                "in progress", "in_progress", "processing",
                "対応中", "処理中", "作業中"
            )

            if is_in_progress and issue_key and issue_key not in seen_keys:
                seen_keys.add(issue_key)
                in_progress.append({
                    "issue_key": issue_key,
                    "summary": entry.content[:100] if entry.content else "",
                    "assignee": metadata.get("assignee", ""),
                    "updated_at": entry.timestamp,
                })

        in_progress.sort(key=lambda t: t.get("updated_at", datetime.min), reverse=True)
        return in_progress[:limit]

    def generate_brief(self, include_details: bool = True) -> str:
        """Generate formatted morning brief.

        Args:
            include_details: Include detailed lists (default: True)

        Returns:
            Formatted markdown string
        """
        now = datetime.now()
        weekday_ja = ["月", "火", "水", "木", "金", "土", "日"][now.weekday()]

        lines = [
            "┌─────────────────────────────────────────────────────┐",
            f"│ 📅 Morning Brief - {now.strftime('%Y-%m-%d')} ({weekday_ja})                  │",
            "├─────────────────────────────────────────────────────┤",
        ]

        # Unread summary
        unread = self.get_unread_summary()
        total_unread = sum(unread.values())
        cutoff = self._get_overnight_cutoff()

        lines.append(f"│ 🔔 UNREAD ({total_unread} items since {cutoff.strftime('%H:%M')} yesterday)           │")

        if total_unread > 0:
            for source, count in unread.items():
                if count > 0:
                    lines.append(f"│   • {source.capitalize()}: {count} new items                         │")
        else:
            lines.append("│   • No unread items                                │")

        lines.append("├─────────────────────────────────────────────────────┤")

        if include_details:
            # Completed tasks
            completed = self.get_completed_tasks(limit=5)
            lines.append("│ ✅ COMPLETED OVERNIGHT                              │")

            if completed:
                for task in completed:
                    summary = task["summary"][:35] + "..." if len(task["summary"]) > 35 else task["summary"]
                    lines.append(f"│   • {task['issue_key']}: {summary}         │")
            else:
                lines.append("│   • No tasks completed overnight                   │")

            lines.append("├─────────────────────────────────────────────────────┤")

            # Blockers
            blockers = self.get_blockers(limit=3)
            lines.append("│ ⚠️ BLOCKERS                                         │")

            if blockers:
                for blocker in blockers:
                    summary = blocker["summary"][:35] + "..." if len(blocker["summary"]) > 35 else blocker["summary"]
                    lines.append(f"│   • {blocker['issue_key']}: {summary}         │")
            else:
                lines.append("│   • No blockers detected                           │")

        lines.append("└─────────────────────────────────────────────────────┘")

        return "\n".join(lines)

    def generate_brief_json(self) -> Dict[str, Any]:
        """Generate morning brief as JSON dict.

        Returns:
            Dict with all brief data
        """
        now = datetime.now()
        cutoff = self._get_overnight_cutoff()

        return {
            "generated_at": now.isoformat(),
            "project_key": self.project_key,
            "cutoff_time": cutoff.isoformat(),
            "unread": self.get_unread_summary(),
            "total_unread": self.get_total_unread(),
            "completed_tasks": self.get_completed_tasks(),
            "blockers": self.get_blockers(),
            "in_progress": self.get_in_progress_tasks(),
            "overnight_updates_count": len(self.get_overnight_updates()),
        }
