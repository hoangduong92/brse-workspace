"""Vault database connection and schema management."""
import sqlite3
import threading
from pathlib import Path
from typing import Optional


class VaultDB:
    """Thread-safe SQLite connection manager for vault."""

    _local = threading.local()
    _db_path: Optional[Path] = None
    _sqlite_vec_available = None

    @classmethod
    def initialize(cls, db_path: Optional[Path] = None):
        """Initialize database path and schema."""
        if db_path is None:
            db_path = Path.home() / ".brsekit" / "vault.db"

        cls._db_path = db_path
        cls._db_path.parent.mkdir(parents=True, exist_ok=True)

        # Check sqlite-vec availability
        cls._check_sqlite_vec()

        # Initialize schema
        cls._init_schema()

    @classmethod
    def get_project_db_path(cls, project: str, workspace_root: Optional[Path] = None) -> Path:
        """Get database path for specific project."""
        root = workspace_root or Path.cwd()
        vault_dir = root / "projects" / project / "vault"
        vault_dir.mkdir(parents=True, exist_ok=True)
        return vault_dir / "vault.db"

    @classmethod
    def initialize_for_project(cls, project: str, workspace_root: Optional[Path] = None):
        """Initialize database for specific project."""
        db_path = cls.get_project_db_path(project, workspace_root)
        cls.initialize(db_path)

    @classmethod
    def _check_sqlite_vec(cls):
        """Check if sqlite-vec extension is available."""
        if cls._sqlite_vec_available is not None:
            return

        try:
            conn = sqlite3.connect(":memory:")
            conn.enable_load_extension(True)
            conn.load_extension("vec0")
            conn.close()
            cls._sqlite_vec_available = True
        except Exception:
            cls._sqlite_vec_available = False

    @classmethod
    def _init_schema(cls):
        """Create tables if they don't exist."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        # Vault items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_items (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sync state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_state (
                source TEXT PRIMARY KEY,
                last_synced TIMESTAMP,
                last_item_id TEXT,
                config TEXT
            )
        """)

        # Time logs table - tracks actualHours changes per issue/member/day
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_logs (
                id TEXT PRIMARY KEY,
                project_key TEXT NOT NULL,
                issue_key TEXT NOT NULL,
                member_id INTEGER,
                member_name TEXT NOT NULL,
                hours_delta REAL NOT NULL,
                total_after REAL NOT NULL,
                logged_at DATE NOT NULL,
                activity_id INTEGER,
                synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vault_source
            ON vault_items(source)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_vault_updated
            ON vault_items(updated_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_time_logs_project
            ON time_logs(project_key)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_time_logs_member_date
            ON time_logs(member_name, logged_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_time_logs_issue
            ON time_logs(issue_key, logged_at)
        """)

        # Add project column if not exists (SQLite migration)
        cursor.execute("PRAGMA table_info(vault_items)")
        columns = [row[1] for row in cursor.fetchall()]
        if "project" not in columns:
            cursor.execute("ALTER TABLE vault_items ADD COLUMN project TEXT")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_vault_project ON vault_items(project)"
            )

        conn.commit()

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(cls._local, "conn") or cls._local.conn is None:
            if cls._db_path is None:
                cls.initialize()

            cls._local.conn = sqlite3.connect(
                str(cls._db_path),
                check_same_thread=False
            )
            cls._local.conn.row_factory = sqlite3.Row

        return cls._local.conn

    @classmethod
    def is_vec_available(cls) -> bool:
        """Check if sqlite-vec extension is available."""
        if cls._sqlite_vec_available is None:
            cls._check_sqlite_vec()
        return cls._sqlite_vec_available

    @classmethod
    def close(cls):
        """Close thread-local connection."""
        if hasattr(cls._local, "conn") and cls._local.conn:
            cls._local.conn.close()
            cls._local.conn = None
