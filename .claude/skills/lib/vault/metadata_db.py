"""Metadata database for BrseKit v2 - fast lookups, sync state, file indexing."""
import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MetadataDB:
    """Thread-safe SQLite connection manager for metadata.sqlite."""

    _local = threading.local()
    _db_path: Optional[Path] = None
    _initialized = False

    @classmethod
    def initialize(cls, db_path: Optional[Path] = None):
        """Initialize database path and schema."""
        if db_path is None:
            db_path = Path.home() / ".brsekit" / "db" / "metadata.sqlite"

        cls._db_path = db_path
        cls._db_path.parent.mkdir(parents=True, exist_ok=True)
        cls._init_schema()
        cls._initialized = True

    @classmethod
    def _init_schema(cls):
        """Create tables if they don't exist."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        # Projects registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_key TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                config TEXT
            )
        """)

        # Sync state per project/source
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_state (
                project_key TEXT NOT NULL,
                source TEXT NOT NULL,
                last_synced TIMESTAMP,
                last_item_id TEXT,
                cursor TEXT,
                config TEXT,
                PRIMARY KEY (project_key, source)
            )
        """)

        # File index for quick lookup
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_index (
                project_key TEXT NOT NULL,
                layer TEXT NOT NULL,
                source TEXT,
                file_path TEXT NOT NULL,
                entry_count INTEGER DEFAULT 0,
                first_entry_at TIMESTAMP,
                last_entry_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (project_key, layer, file_path)
            )
        """)

        # Read markers for unread detection
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS read_markers (
                project_key TEXT NOT NULL,
                source TEXT NOT NULL,
                last_read_at TIMESTAMP NOT NULL,
                PRIMARY KEY (project_key, source)
            )
        """)

        # Indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sync_project ON sync_state(project_key)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_files_project ON file_index(project_key)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_read_project ON read_markers(project_key)"
        )

        conn.commit()

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(cls._local, "conn") or cls._local.conn is None:
            if cls._db_path is None:
                cls.initialize()

            cls._local.conn = sqlite3.connect(
                str(cls._db_path), check_same_thread=False
            )
            cls._local.conn.row_factory = sqlite3.Row

        return cls._local.conn

    @classmethod
    def close(cls):
        """Close thread-local connection."""
        if hasattr(cls._local, "conn") and cls._local.conn:
            cls._local.conn.close()
            cls._local.conn = None


@dataclass
class ProjectInfo:
    """Project information."""
    project_key: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)


class ProjectRegistry:
    """Project CRUD operations."""

    def register(
        self,
        project_key: str,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Register new project or update existing.

        Returns:
            True if created, False if updated
        """
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        config_json = json.dumps(config or {})
        cursor.execute(
            """
            INSERT INTO projects (project_key, name, config)
            VALUES (?, ?, ?)
            ON CONFLICT(project_key) DO UPDATE SET
                name = COALESCE(excluded.name, projects.name),
                config = excluded.config
        """,
            (project_key, name, config_json),
        )
        conn.commit()
        return cursor.rowcount > 0

    def get(self, project_key: str) -> Optional[ProjectInfo]:
        """Get project info."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM projects WHERE project_key = ?", (project_key,)
        )
        row = cursor.fetchone()

        if row:
            return ProjectInfo(
                project_key=row["project_key"],
                name=row["name"],
                created_at=row["created_at"],
                config=json.loads(row["config"]) if row["config"] else {},
            )
        return None

    def list_all(self) -> List[str]:
        """List all registered projects."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT project_key FROM projects ORDER BY created_at")
        return [row["project_key"] for row in cursor.fetchall()]

    def update_config(self, project_key: str, config: Dict[str, Any]) -> bool:
        """Update project config."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE projects SET config = ? WHERE project_key = ?",
            (json.dumps(config), project_key),
        )
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, project_key: str) -> bool:
        """Delete project from registry."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM projects WHERE project_key = ?", (project_key,))
        conn.commit()
        return cursor.rowcount > 0


class SyncStateManager:
    """Manage sync state per project/source."""

    def __init__(self, project_key: str):
        self.project_key = project_key

    def get_last_sync(self, source: str) -> Optional[datetime]:
        """Get last sync timestamp for source."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_synced FROM sync_state WHERE project_key = ? AND source = ?",
            (self.project_key, source),
        )
        row = cursor.fetchone()
        if row and row["last_synced"]:
            return datetime.fromisoformat(row["last_synced"])
        return None

    def get_last_item_id(self, source: str) -> Optional[str]:
        """Get last synced item ID for incremental sync."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_item_id FROM sync_state WHERE project_key = ? AND source = ?",
            (self.project_key, source),
        )
        row = cursor.fetchone()
        return row["last_item_id"] if row else None

    def update_sync(
        self,
        source: str,
        last_synced: datetime,
        last_item_id: Optional[str] = None,
        cursor_val: Optional[str] = None,
    ) -> None:
        """Update sync state."""
        conn = MetadataDB.get_connection()
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            INSERT INTO sync_state (project_key, source, last_synced, last_item_id, cursor)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_key, source) DO UPDATE SET
                last_synced = excluded.last_synced,
                last_item_id = COALESCE(excluded.last_item_id, sync_state.last_item_id),
                cursor = COALESCE(excluded.cursor, sync_state.cursor)
        """,
            (self.project_key, source, last_synced.isoformat(), last_item_id, cursor_val),
        )
        conn.commit()

    def get_all_sources(self) -> Dict[str, datetime]:
        """Get all sources with their last sync times."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT source, last_synced FROM sync_state WHERE project_key = ?",
            (self.project_key,),
        )
        return {
            row["source"]: datetime.fromisoformat(row["last_synced"])
            for row in cursor.fetchall()
            if row["last_synced"]
        }


class ReadMarkerManager:
    """Manage read markers for unread detection."""

    def __init__(self, project_key: str):
        self.project_key = project_key

    def get_last_read(self, source: str) -> Optional[datetime]:
        """Get last read timestamp for source."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_read_at FROM read_markers WHERE project_key = ? AND source = ?",
            (self.project_key, source),
        )
        row = cursor.fetchone()
        if row and row["last_read_at"]:
            return datetime.fromisoformat(row["last_read_at"])
        return None

    def mark_as_read(self, source: str, read_at: Optional[datetime] = None) -> None:
        """Mark source as read."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        read_at = read_at or datetime.now()
        cursor.execute(
            """
            INSERT INTO read_markers (project_key, source, last_read_at)
            VALUES (?, ?, ?)
            ON CONFLICT(project_key, source) DO UPDATE SET
                last_read_at = excluded.last_read_at
        """,
            (self.project_key, source, read_at.isoformat()),
        )
        conn.commit()

    def get_all_read_markers(self) -> Dict[str, datetime]:
        """Get all read markers for project."""
        conn = MetadataDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT source, last_read_at FROM read_markers WHERE project_key = ?",
            (self.project_key,),
        )
        return {
            row["source"]: datetime.fromisoformat(row["last_read_at"])
            for row in cursor.fetchall()
            if row["last_read_at"]
        }
