"""Memory store - JSONL append-only storage for auto-synced data."""
import gzip
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .directory_manager import DirectoryManager


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    source: str
    timestamp: datetime
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    synced_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "id": self.id,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "metadata": self.metadata,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dict."""
        return cls(
            id=data["id"],
            source=data["source"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            content=data["content"],
            metadata=data.get("metadata", {}),
            synced_at=datetime.fromisoformat(data["synced_at"]) if data.get("synced_at") else None,
        )


class MemoryStore:
    """JSONL-based memory store with date-based files, compression, and archival."""

    def __init__(self, project_key: str, base_path: Optional[Path] = None):
        """Initialize memory store for a project.

        Args:
            project_key: Unique project identifier
            base_path: Optional base path (default: ~/.brsekit)
        """
        self.project_key = project_key
        self.dir_manager = DirectoryManager(base_path)
        self.dir_manager.ensure_project_structure(project_key)

    def _get_file_path(self, source: str, target_date: date) -> Path:
        """Get JSONL file path for source and date."""
        memory_path = self.dir_manager.get_memory_path(self.project_key, source)
        return memory_path / f"{target_date.isoformat()}.jsonl"

    def _get_gzip_path(self, source: str, target_date: date) -> Path:
        """Get gzipped file path."""
        memory_path = self.dir_manager.get_memory_path(self.project_key, source)
        return memory_path / f"{target_date.isoformat()}.jsonl.gz"

    def append(self, source: str, entry: MemoryEntry) -> bool:
        """Append a single entry to JSONL file.

        Args:
            source: Source name (backlog, slack, email, meetings)
            entry: MemoryEntry to append

        Returns:
            True if successful
        """
        # Set synced_at if not set
        if entry.synced_at is None:
            entry.synced_at = datetime.now()

        target_date = entry.timestamp.date()
        file_path = self._get_file_path(source, target_date)

        # Atomic write using temp file
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=file_path.parent,
                delete=False,
                suffix=".tmp"
            ) as tmp:
                # Read existing content if file exists
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        tmp.write(f.read())

                # Append new entry
                tmp.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
                tmp_path = tmp.name

            # Atomic rename
            shutil.move(tmp_path, file_path)
            return True

        except Exception:
            # Clean up temp file on error
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    def append_batch(self, source: str, entries: List[MemoryEntry]) -> int:
        """Append multiple entries.

        Args:
            source: Source name
            entries: List of entries to append

        Returns:
            Number of entries appended
        """
        if not entries:
            return 0

        # Group entries by date
        entries_by_date: Dict[date, List[MemoryEntry]] = {}
        for entry in entries:
            if entry.synced_at is None:
                entry.synced_at = datetime.now()
            target_date = entry.timestamp.date()
            if target_date not in entries_by_date:
                entries_by_date[target_date] = []
            entries_by_date[target_date].append(entry)

        count = 0
        for target_date, date_entries in entries_by_date.items():
            file_path = self._get_file_path(source, target_date)

            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=file_path.parent,
                delete=False,
                suffix=".tmp",
                encoding="utf-8"
            ) as tmp:
                # Read existing content
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        tmp.write(f.read())

                # Append new entries
                for entry in date_entries:
                    tmp.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
                    count += 1

                tmp_path = tmp.name

            shutil.move(tmp_path, file_path)

        return count

    def read_entries(
        self,
        source: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[MemoryEntry]:
        """Read entries from date range.

        Args:
            source: Source name
            start_date: Start date (inclusive, default: 7 days ago)
            end_date: End date (inclusive, default: today)

        Returns:
            List of MemoryEntry
        """
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=7)

        entries = []
        current_date = start_date

        while current_date <= end_date:
            entries.extend(self._read_date(source, current_date))
            current_date += timedelta(days=1)

        return entries

    def _read_date(self, source: str, target_date: date) -> List[MemoryEntry]:
        """Read entries for a specific date."""
        entries = []

        # Try regular file first
        file_path = self._get_file_path(source, target_date)
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(MemoryEntry.from_dict(json.loads(line)))
            return entries

        # Try gzipped file
        gzip_path = self._get_gzip_path(source, target_date)
        if gzip_path.exists():
            with gzip.open(gzip_path, "rt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(MemoryEntry.from_dict(json.loads(line)))

        return entries

    def read_today(self, source: str) -> List[MemoryEntry]:
        """Shortcut for today's entries."""
        return self._read_date(source, date.today())

    def get_entry_count(self, source: str, target_date: Optional[date] = None) -> int:
        """Count entries for source/date."""
        if target_date:
            return len(self._read_date(source, target_date))

        # Count all entries
        memory_path = self.dir_manager.get_memory_path(self.project_key, source)
        if not memory_path.exists():
            return 0

        count = 0
        for file_path in memory_path.glob("*.jsonl*"):
            if file_path.suffix == ".gz":
                with gzip.open(file_path, "rt", encoding="utf-8") as f:
                    count += sum(1 for line in f if line.strip())
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    count += sum(1 for line in f if line.strip())

        return count

    def list_dates(self, source: str) -> List[date]:
        """List all dates with data for source."""
        memory_path = self.dir_manager.get_memory_path(self.project_key, source)
        if not memory_path.exists():
            return []

        dates = set()
        for file_path in memory_path.glob("*.jsonl*"):
            # Extract date from filename (YYYY-MM-DD.jsonl or YYYY-MM-DD.jsonl.gz)
            date_str = file_path.name.split(".")[0]
            try:
                dates.add(date.fromisoformat(date_str))
            except ValueError:
                continue

        return sorted(dates)

    def compress_old_files(self, days_threshold: int = 7) -> int:
        """Compress JSONL files older than threshold.

        Args:
            days_threshold: Files older than this many days will be compressed

        Returns:
            Number of files compressed
        """
        cutoff_date = date.today() - timedelta(days=days_threshold)
        compressed = 0

        for source in DirectoryManager.MEMORY_SOURCES:
            memory_path = self.dir_manager.get_memory_path(self.project_key, source)
            if not memory_path.exists():
                continue

            for file_path in memory_path.glob("*.jsonl"):
                # Extract date from filename
                date_str = file_path.stem
                try:
                    file_date = date.fromisoformat(date_str)
                except ValueError:
                    continue

                if file_date < cutoff_date:
                    gzip_path = file_path.with_suffix(".jsonl.gz")

                    # Compress
                    with open(file_path, "rb") as f_in:
                        with gzip.open(gzip_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    # Remove original
                    file_path.unlink()
                    compressed += 1

        return compressed

    def archive_old_files(self, days_threshold: int = 30) -> int:
        """Move files older than threshold to archive folder.

        Args:
            days_threshold: Files older than this will be archived

        Returns:
            Number of files archived
        """
        cutoff_date = date.today() - timedelta(days=days_threshold)
        archive_path = self.dir_manager.get_archive_path(self.project_key)
        archived = 0

        for source in DirectoryManager.MEMORY_SOURCES:
            memory_path = self.dir_manager.get_memory_path(self.project_key, source)
            if not memory_path.exists():
                continue

            # Create archive subfolder for source
            source_archive = archive_path / source
            source_archive.mkdir(parents=True, exist_ok=True)

            for file_path in memory_path.glob("*.jsonl*"):
                date_str = file_path.name.split(".")[0]
                try:
                    file_date = date.fromisoformat(date_str)
                except ValueError:
                    continue

                if file_date < cutoff_date:
                    dest_path = source_archive / file_path.name
                    shutil.move(str(file_path), str(dest_path))
                    archived += 1

        return archived
