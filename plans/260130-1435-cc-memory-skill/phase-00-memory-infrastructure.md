# Phase 0: Memory Infrastructure

## Context Links
- Vault lib: `.claude/skills/lib/vault/`
- VaultDB: `.claude/skills/lib/vault/db.py`
- VaultStore: `.claude/skills/lib/vault/store.py`

## Overview
- **Priority:** P0 (foundation)
- **Status:** pending
- **Effort:** 1.5h

Setup memory database, config, and core models extending existing vault infrastructure.

## Key Insights

1. VaultDB already handles SQLite + thread-safety
2. VaultStore provides CRUD with auto-embedding
3. Memory needs: sessions table, facts table, config management
4. User-level path: `~/claude_client/memory/`

## Requirements

### Functional
- Initialize memory directory at `~/claude_client/memory/`
- Create SQLite database `vault.db` with sessions/facts tables
- Load/save `facts.md` for quick access
- Manage `config.json` for user preferences

### Non-Functional
- No startup latency impact (<50ms)
- Thread-safe database access
- Graceful degradation if Gemini unavailable

## Architecture

```
MemoryDB (extends VaultDB)
    ├── sessions table (session_id, workspace, start_time, end_time, summary)
    ├── facts table (id, content, source_session, confidence, created_at)
    └── embeddings (via existing vault_items)

MemoryStore (extends VaultStore)
    ├── add_session()
    ├── add_fact()
    ├── get_facts()
    └── search_facts()
```

## Related Code Files

### Create
- `.claude/skills/cc-memory/SKILL.md` - Skill manifest
- `.claude/skills/cc-memory/scripts/memory_db.py` - MemoryDB class
- `.claude/skills/cc-memory/scripts/memory_store.py` - MemoryStore class
- `.claude/skills/cc-memory/scripts/config_manager.py` - Config handling
- `.claude/skills/cc-memory/scripts/__init__.py` - Package init

### Modify
- None (new skill)

## Implementation Steps

### Step 1: Create skill directory structure
```
.claude/skills/cc-memory/
├── SKILL.md
├── scripts/
│   ├── __init__.py
│   ├── memory_db.py
│   ├── memory_store.py
│   ├── config_manager.py
│   └── main.py
└── tests/
    └── __init__.py
```

### Step 2: Implement memory_db.py

```python
"""Memory database - extends VaultDB for user-level memory storage."""
import sqlite3
from pathlib import Path
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
from vault import VaultDB

class MemoryDB(VaultDB):
    """Thread-safe SQLite for memory storage at ~/claude_client/memory/."""

    _memory_path: Optional[Path] = None

    @classmethod
    def get_memory_dir(cls) -> Path:
        """Get user-level memory directory."""
        return Path.home() / "claude_client" / "memory"

    @classmethod
    def initialize(cls, db_path: Optional[Path] = None):
        """Initialize memory database."""
        if db_path is None:
            memory_dir = cls.get_memory_dir()
            memory_dir.mkdir(parents=True, exist_ok=True)
            db_path = memory_dir / "vault.db"

        cls._memory_path = db_path
        super().initialize(db_path)
        cls._init_memory_schema()

    @classmethod
    def _init_memory_schema(cls):
        """Create memory-specific tables."""
        conn = cls.get_connection()
        cursor = conn.cursor()

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_sessions (
                session_id TEXT PRIMARY KEY,
                workspace TEXT NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                summary TEXT,
                message_count INTEGER DEFAULT 0,
                archived_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Facts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_facts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                source_session TEXT,
                confidence REAL DEFAULT 1.0,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_session) REFERENCES memory_sessions(session_id)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_category
            ON memory_facts(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_workspace
            ON memory_sessions(workspace)
        """)

        conn.commit()
```

### Step 3: Implement memory_store.py

```python
"""Memory store - CRUD for sessions and facts."""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
from vault import VaultStore, VaultItem, GeminiEmbedder

from memory_db import MemoryDB

@dataclass
class Session:
    session_id: str
    workspace: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    summary: Optional[str] = None
    message_count: int = 0
    archived_path: Optional[str] = None

@dataclass
class Fact:
    id: str
    content: str
    source_session: Optional[str] = None
    confidence: float = 1.0
    category: Optional[str] = None
    created_at: Optional[datetime] = None

class MemoryStore:
    """CRUD for memory sessions and facts."""

    def __init__(self, embedder: Optional[GeminiEmbedder] = None):
        self.embedder = embedder
        self._vault_store = VaultStore(embedder) if embedder else None
        MemoryDB.initialize()

    # Session methods
    def add_session(self, session: Session) -> str:
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO memory_sessions
            (session_id, workspace, start_time, end_time, summary, message_count, archived_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (session.session_id, session.workspace, session.start_time,
              session.end_time, session.summary, session.message_count, session.archived_path))
        conn.commit()
        return session.session_id

    def get_recent_sessions(self, limit: int = 10) -> List[Session]:
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, workspace, start_time, end_time, summary, message_count, archived_path
            FROM memory_sessions ORDER BY start_time DESC LIMIT ?
        """, (limit,))
        return [self._row_to_session(row) for row in cursor.fetchall()]

    # Fact methods
    def add_fact(self, fact: Fact) -> str:
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        fact_id = fact.id or str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO memory_facts (id, content, source_session, confidence, category)
            VALUES (?, ?, ?, ?, ?)
        """, (fact_id, fact.content, fact.source_session, fact.confidence, fact.category))
        conn.commit()

        # Also add to vault for embedding search
        if self._vault_store:
            item = VaultItem(
                id=f"fact:{fact_id}",
                source="memory",
                title=f"Fact: {fact.content[:50]}",
                content=fact.content,
                metadata={"category": fact.category, "confidence": fact.confidence}
            )
            self._vault_store.add(item)

        return fact_id

    def get_all_facts(self) -> List[Fact]:
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memory_facts ORDER BY created_at DESC")
        return [self._row_to_fact(row) for row in cursor.fetchall()]

    def delete_fact(self, fact_id: str) -> bool:
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory_facts WHERE id = ?", (fact_id,))
        conn.commit()
        return cursor.rowcount > 0

    def _row_to_session(self, row) -> Session:
        return Session(
            session_id=row[0], workspace=row[1],
            start_time=datetime.fromisoformat(row[2]) if row[2] else None,
            end_time=datetime.fromisoformat(row[3]) if row[3] else None,
            summary=row[4], message_count=row[5], archived_path=row[6]
        )

    def _row_to_fact(self, row) -> Fact:
        return Fact(
            id=row[0], content=row[1], source_session=row[2],
            confidence=row[3], category=row[4],
            created_at=datetime.fromisoformat(row[5]) if row[5] else None
        )
```

### Step 4: Implement config_manager.py

```python
"""Config manager for memory settings."""
import json
from pathlib import Path
from typing import Dict, Any
from memory_db import MemoryDB

DEFAULT_CONFIG = {
    "auto_extract": True,
    "extract_method": "hybrid",  # heuristic, gemini, hybrid
    "min_session_messages": 5,
    "max_facts_loaded": 50,
    "gemini_threshold_messages": 20,
    "fact_categories": ["preference", "decision", "requirement", "context"]
}

class ConfigManager:
    """Manage memory configuration."""

    def __init__(self):
        self.config_path = MemoryDB.get_memory_dir() / "config.json"
        self._config = None

    def load(self) -> Dict[str, Any]:
        if self._config:
            return self._config

        if self.config_path.exists():
            with open(self.config_path) as f:
                self._config = {**DEFAULT_CONFIG, **json.load(f)}
        else:
            self._config = DEFAULT_CONFIG.copy()

        return self._config

    def save(self, config: Dict[str, Any]):
        self._config = config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self.load().get(key, default)

    def set(self, key: str, value: Any):
        config = self.load()
        config[key] = value
        self.save(config)
```

### Step 5: Create SKILL.md

```markdown
---
name: cc-memory
description: User-level memory - search past sessions, recall facts. Use for context from previous conversations.
argument-hint: "<search|recent|summarize|add|forget> [query] [--limit N]"
---

# cc-memory

Claude Code memory skill - persistent context across sessions.

## Usage

# Search past conversations
/memory search "authentication decision"

# List recent sessions
/memory recent 5

# Summarize topic across sessions
/memory summarize "database schema"

# Manually add a fact
/memory add "User prefers TypeScript over JavaScript"

# Remove a fact
/memory forget <fact-id>
```

## Todo List

- [ ] Create skill directory structure
- [ ] Implement memory_db.py extending VaultDB
- [ ] Implement memory_store.py with Session/Fact models
- [ ] Implement config_manager.py
- [ ] Create SKILL.md manifest
- [ ] Create __init__.py exports
- [ ] Test database initialization

## Success Criteria

- [ ] `~/claude_client/memory/` directory created on first use
- [ ] SQLite database with sessions + facts tables
- [ ] MemoryStore can add/get sessions and facts
- [ ] Config loads defaults, persists changes

## Security Considerations

- Store at user level, not project level
- No sensitive data in facts (extracted from conversations)
- Config file permissions: user-only read/write
