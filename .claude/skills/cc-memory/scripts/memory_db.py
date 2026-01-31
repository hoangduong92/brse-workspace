"""Memory database - separate SQLite at ~/claude_client/memory/."""
import sqlite3
import threading
from pathlib import Path
from typing import Optional


class MemoryDB:
    """Thread-safe SQLite for user-level memory storage."""

    _local = threading.local()
    _db_path: Optional[Path] = None
    _initialized = False

    @classmethod
    def get_memory_dir(cls) -> Path:
        """Get user-level memory directory."""
        return Path.home() / "claude_client" / "memory"

    @classmethod
    def initialize(cls, db_path: Optional[Path] = None):
        """Initialize memory database with schema."""
        if cls._initialized and cls._db_path == db_path:
            return

        if db_path is None:
            memory_dir = cls.get_memory_dir()
            memory_dir.mkdir(parents=True, exist_ok=True)
            # Create conversations archive directory
            (memory_dir / "conversations" / "archives").mkdir(parents=True, exist_ok=True)
            db_path = memory_dir / "vault.db"

        cls._db_path = db_path
        cls._init_schema()
        cls._initialized = True

    @classmethod
    def _init_schema(cls):
        """Create memory-specific tables."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        # Sessions table - tracks all Claude Code sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_sessions (
                session_id TEXT PRIMARY KEY,
                workspace TEXT NOT NULL,
                workspace_name TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                summary TEXT,
                message_count INTEGER DEFAULT 0,
                archived_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Facts table - memorable facts extracted from sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_facts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source_session TEXT,
                confidence REAL DEFAULT 1.0,
                category TEXT,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_session) REFERENCES memory_sessions(session_id)
            )
        """)

        # Indexes for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_category
            ON memory_facts(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_session
            ON memory_facts(source_session)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_workspace
            ON memory_sessions(workspace)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_time
            ON memory_sessions(start_time DESC)
        """)

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
    def close(cls):
        """Close thread-local connection."""
        if hasattr(cls._local, "conn") and cls._local.conn:
            cls._local.conn.close()
            cls._local.conn = None

    @classmethod
    def reset(cls):
        """Reset database state (for testing)."""
        cls.close()
        cls._initialized = False
        cls._db_path = None
