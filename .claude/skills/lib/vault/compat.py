"""Backward compatibility - migrate from legacy vault.db to new project structure."""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .db import VaultDB
from .directory_manager import DirectoryManager
from .memory_store import MemoryEntry, MemoryStore
from .metadata_db import MetadataDB, ProjectRegistry


class LegacyMigrator:
    """Migrate from legacy vault.db to new per-project structure."""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize migrator.

        Args:
            base_path: Optional base path (default: ~/.brsekit)
        """
        self.base_path = base_path or Path.home() / ".brsekit"
        self.legacy_db_path = self.base_path / "vault.db"
        self.dir_manager = DirectoryManager(base_path)

    def detect_legacy_data(self) -> bool:
        """Check if vault.db has data to migrate.

        Returns:
            True if legacy vault.db exists and has data
        """
        if not self.legacy_db_path.exists():
            return False

        # Initialize legacy VaultDB
        VaultDB.initialize(self.legacy_db_path)
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM vault_items")
        row = cursor.fetchone()

        return row["count"] > 0 if row else False

    def analyze_sources(self) -> Dict[str, int]:
        """Count items per source in vault.db.

        Returns:
            Dict mapping source to item count
        """
        if not self.legacy_db_path.exists():
            return {}

        VaultDB.initialize(self.legacy_db_path)
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM vault_items
            GROUP BY source
        """)

        return {row["source"]: row["count"] for row in cursor.fetchall()}

    def backup_vault(self, backup_path: Optional[Path] = None) -> Path:
        """Backup vault.db before migration.

        Args:
            backup_path: Optional custom backup path

        Returns:
            Path to backup file
        """
        if not self.legacy_db_path.exists():
            raise FileNotFoundError(f"vault.db not found at {self.legacy_db_path}")

        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.base_path / f"vault_backup_{timestamp}.db"

        shutil.copy2(self.legacy_db_path, backup_path)
        return backup_path

    def migrate_to_project(
        self,
        project_key: str,
        sources: Optional[List[str]] = None,
        delete_after: bool = False,
    ) -> Dict[str, int]:
        """Migrate vault.db items to project memory layer.

        Args:
            project_key: Target project key
            sources: Optional list of sources to migrate (default: all)
            delete_after: If True, delete migrated items from vault.db

        Returns:
            Dict mapping source to migrated count
        """
        if not self.legacy_db_path.exists():
            return {}

        # Initialize databases
        VaultDB.initialize(self.legacy_db_path)
        MetadataDB.initialize()

        # Ensure project structure
        self.dir_manager.ensure_project_structure(project_key)

        # Register project
        registry = ProjectRegistry()
        registry.register(project_key, name=f"Migrated from vault.db")

        # Create memory store for project
        memory_store = MemoryStore(project_key, self.base_path)

        # Get source filter
        if sources is None:
            source_analysis = self.analyze_sources()
            sources = list(source_analysis.keys())

        migrated = {}

        for source in sources:
            entries = self._fetch_legacy_entries(source)

            if entries:
                # Convert to MemoryEntry and store
                memory_entries = [
                    self._convert_to_memory_entry(item)
                    for item in entries
                ]

                count = memory_store.append_batch(source, memory_entries)
                migrated[source] = count

                # Optionally delete from legacy
                if delete_after:
                    self._delete_legacy_entries(source)

        return migrated

    def _fetch_legacy_entries(self, source: str) -> List[Dict]:
        """Fetch entries from legacy vault.db."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, source, title, content, metadata, created_at, updated_at
            FROM vault_items
            WHERE source = ?
            ORDER BY created_at
        """, (source,))

        return [dict(row) for row in cursor.fetchall()]

    def _convert_to_memory_entry(self, item: Dict) -> MemoryEntry:
        """Convert legacy vault item to MemoryEntry."""
        metadata = json.loads(item["metadata"]) if item["metadata"] else {}

        # Add title to metadata if exists
        if item["title"]:
            metadata["title"] = item["title"]

        # Parse timestamp
        timestamp_str = item["created_at"] or item["updated_at"]
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        return MemoryEntry(
            id=item["id"],
            source=item["source"],
            timestamp=timestamp,
            content=item["content"],
            metadata=metadata,
            synced_at=datetime.now(),
        )

    def _delete_legacy_entries(self, source: str) -> int:
        """Delete entries from legacy vault.db."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM vault_items WHERE source = ?", (source,))
        conn.commit()

        return cursor.rowcount

    def get_migration_status(self, project_key: str) -> Dict:
        """Get migration status for a project.

        Returns:
            Dict with migration info
        """
        legacy_sources = self.analyze_sources()

        # Check if project exists
        memory_store = MemoryStore(project_key, self.base_path)

        project_counts = {}
        for source in DirectoryManager.MEMORY_SOURCES:
            project_counts[source] = memory_store.get_entry_count(source)

        return {
            "legacy_db_exists": self.legacy_db_path.exists(),
            "legacy_sources": legacy_sources,
            "project_sources": project_counts,
            "total_legacy": sum(legacy_sources.values()),
            "total_project": sum(project_counts.values()),
        }

    def cleanup_legacy(self, confirm: bool = False) -> bool:
        """Remove legacy vault.db after successful migration.

        Args:
            confirm: Must be True to actually delete

        Returns:
            True if deleted
        """
        if not confirm:
            raise ValueError("Must pass confirm=True to delete legacy vault.db")

        if self.legacy_db_path.exists():
            self.legacy_db_path.unlink()
            return True

        return False
