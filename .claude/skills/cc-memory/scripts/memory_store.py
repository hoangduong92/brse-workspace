"""Memory store - CRUD for sessions and facts with embedding support."""
import json
import math
import struct
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import os

# Add paths for imports
_script_dir = Path(__file__).parent
sys.path.insert(0, str(_script_dir))
sys.path.insert(0, str(_script_dir.parent.parent / "lib"))

from memory_db import MemoryDB

# Try to import Gemini embedder from vault lib
try:
    from vault import GeminiEmbedder
    EMBEDDER_AVAILABLE = True
except ImportError:
    EMBEDDER_AVAILABLE = False
    GeminiEmbedder = None


@dataclass
class Session:
    """Claude Code session record."""
    session_id: str
    workspace: str
    workspace_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    summary: Optional[str] = None
    message_count: int = 0
    archived_path: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Fact:
    """Memorable fact extracted from conversations."""
    id: str
    content: str
    source_session: Optional[str] = None
    confidence: float = 1.0
    category: Optional[str] = None
    embedding: Optional[List[float]] = None
    created_at: Optional[datetime] = None


@dataclass
class SearchResult:
    """Search result with similarity score."""
    fact: Fact
    score: float
    session: Optional[Session] = None


class MemoryStore:
    """CRUD operations for memory sessions and facts."""

    def __init__(self, embedder: Optional["GeminiEmbedder"] = None):
        """Initialize store with optional embedder for semantic search."""
        self.embedder = embedder
        MemoryDB.initialize()

    # === Session Methods ===

    def add_session(self, session: Session) -> str:
        """Add or update a session record."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO memory_sessions
            (session_id, workspace, workspace_name, start_time, end_time,
             summary, message_count, archived_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session.session_id,
            session.workspace,
            session.workspace_name,
            session.start_time.isoformat() if session.start_time else None,
            session.end_time.isoformat() if session.end_time else None,
            session.summary,
            session.message_count,
            session.archived_path,
            session.created_at.isoformat() if session.created_at else datetime.now().isoformat()
        ))
        conn.commit()
        return session.session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, workspace, workspace_name, start_time, end_time,
                   summary, message_count, archived_path, created_at
            FROM memory_sessions WHERE session_id = ?
        """, (session_id,))

        row = cursor.fetchone()
        return self._row_to_session(row) if row else None

    def get_recent_sessions(self, limit: int = 10, workspace: Optional[str] = None) -> List[Session]:
        """Get most recent sessions, optionally filtered by workspace."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        if workspace:
            cursor.execute("""
                SELECT session_id, workspace, workspace_name, start_time, end_time,
                       summary, message_count, archived_path, created_at
                FROM memory_sessions
                WHERE workspace = ?
                ORDER BY start_time DESC LIMIT ?
            """, (workspace, limit))
        else:
            cursor.execute("""
                SELECT session_id, workspace, workspace_name, start_time, end_time,
                       summary, message_count, archived_path, created_at
                FROM memory_sessions
                ORDER BY start_time DESC LIMIT ?
            """, (limit,))

        return [self._row_to_session(row) for row in cursor.fetchall()]

    def count_sessions(self) -> int:
        """Get total session count."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memory_sessions")
        return cursor.fetchone()[0]

    # === Fact Methods ===

    def add_fact(self, fact: Fact) -> str:
        """Add a fact with optional embedding."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        fact_id = fact.id or str(uuid.uuid4())[:8]

        # Generate embedding if embedder available
        embedding_blob = None
        if self.embedder and fact.content:
            try:
                embedding = self.embedder.embed(fact.content)
                fact.embedding = embedding
                embedding_blob = self._pack_embedding(embedding)
            except Exception:
                pass  # Continue without embedding

        cursor.execute("""
            INSERT INTO memory_facts
            (id, content, source_session, confidence, category, embedding, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            fact_id,
            fact.content,
            fact.source_session,
            fact.confidence,
            fact.category,
            embedding_blob,
            fact.created_at.isoformat() if fact.created_at else datetime.now().isoformat()
        ))
        conn.commit()
        return fact_id

    def get_fact(self, fact_id: str) -> Optional[Fact]:
        """Get fact by ID."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content, source_session, confidence, category, embedding, created_at
            FROM memory_facts WHERE id = ?
        """, (fact_id,))

        row = cursor.fetchone()
        return self._row_to_fact(row) if row else None

    def get_all_facts(self, limit: int = 100) -> List[Fact]:
        """Get all facts, most recent first."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content, source_session, confidence, category, embedding, created_at
            FROM memory_facts
            ORDER BY created_at DESC LIMIT ?
        """, (limit,))

        return [self._row_to_fact(row) for row in cursor.fetchall()]

    def get_facts_by_category(self, category: str, limit: int = 50) -> List[Fact]:
        """Get facts by category."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content, source_session, confidence, category, embedding, created_at
            FROM memory_facts
            WHERE category = ?
            ORDER BY created_at DESC LIMIT ?
        """, (category, limit))

        return [self._row_to_fact(row) for row in cursor.fetchall()]

    def get_facts_by_session(self, session_id: str) -> List[Fact]:
        """Get all facts from a specific session."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content, source_session, confidence, category, embedding, created_at
            FROM memory_facts
            WHERE source_session = ?
            ORDER BY created_at DESC
        """, (session_id,))

        return [self._row_to_fact(row) for row in cursor.fetchall()]

    def delete_fact(self, fact_id: str) -> bool:
        """Delete a fact by ID."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM memory_facts WHERE id = ?", (fact_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count_facts(self) -> int:
        """Get total fact count."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM memory_facts")
        return cursor.fetchone()[0]

    # === Search Methods ===

    def search_facts(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.3
    ) -> List[SearchResult]:
        """Semantic search for facts using embeddings."""
        if not self.embedder:
            # Fallback to text search if no embedder
            return self._text_search(query, top_k)

        try:
            query_embedding = self.embedder.embed_query(query)
            return self._search_by_embedding(query_embedding, top_k, min_score)
        except Exception:
            # Fallback to text search on embedding failure
            return self._text_search(query, top_k)

    def _search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int,
        min_score: float
    ) -> List[SearchResult]:
        """Search using cosine similarity."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content, source_session, confidence, category, embedding, created_at
            FROM memory_facts
            WHERE embedding IS NOT NULL
        """)

        results = []
        for row in cursor.fetchall():
            fact = self._row_to_fact(row)
            if fact.embedding:
                score = self._cosine_similarity(query_embedding, fact.embedding)
                if score >= min_score:
                    session = self.get_session(fact.source_session) if fact.source_session else None
                    results.append(SearchResult(fact=fact, score=score, session=session))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _text_search(self, query: str, top_k: int) -> List[SearchResult]:
        """Fallback text search using LIKE."""
        conn = MemoryDB.get_connection()
        cursor = conn.cursor()

        # Simple text matching
        cursor.execute("""
            SELECT id, content, source_session, confidence, category, embedding, created_at
            FROM memory_facts
            WHERE content LIKE ?
            ORDER BY created_at DESC LIMIT ?
        """, (f"%{query}%", top_k))

        results = []
        for row in cursor.fetchall():
            fact = self._row_to_fact(row)
            session = self.get_session(fact.source_session) if fact.source_session else None
            results.append(SearchResult(fact=fact, score=0.5, session=session))

        return results

    # === Export Methods ===

    def export_facts_to_markdown(self, path: Optional[Path] = None) -> str:
        """Export all facts to markdown file."""
        if path is None:
            path = MemoryDB.get_memory_dir() / "facts.md"

        facts = self.get_all_facts(limit=500)

        lines = ["# Memory Facts", "", f"_Generated: {datetime.now().isoformat()}_", ""]

        # Group by category
        by_category: Dict[str, List[Fact]] = {}
        for fact in facts:
            cat = fact.category or "general"
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(fact)

        for category, cat_facts in sorted(by_category.items()):
            lines.append(f"## {category.title()}")
            lines.append("")
            for fact in cat_facts:
                lines.append(f"- {fact.content} `[{fact.id}]`")
            lines.append("")

        content = "\n".join(lines)
        path.write_text(content, encoding="utf-8")
        return str(path)

    # === Helper Methods ===

    def _row_to_session(self, row) -> Session:
        """Convert database row to Session."""
        return Session(
            session_id=row[0],
            workspace=row[1],
            workspace_name=row[2],
            start_time=datetime.fromisoformat(row[3]) if row[3] else None,
            end_time=datetime.fromisoformat(row[4]) if row[4] else None,
            summary=row[5],
            message_count=row[6],
            archived_path=row[7],
            created_at=datetime.fromisoformat(row[8]) if row[8] else None
        )

    def _row_to_fact(self, row) -> Fact:
        """Convert database row to Fact."""
        return Fact(
            id=row[0],
            content=row[1],
            source_session=row[2],
            confidence=row[3],
            category=row[4],
            embedding=self._unpack_embedding(row[5]) if row[5] else None,
            created_at=datetime.fromisoformat(row[6]) if row[6] else None
        )

    def _pack_embedding(self, embedding: List[float]) -> bytes:
        """Pack embedding as binary blob."""
        return struct.pack(f'{len(embedding)}f', *embedding)

    def _unpack_embedding(self, blob: bytes) -> List[float]:
        """Unpack embedding from binary blob."""
        count = len(blob) // 4
        return list(struct.unpack(f'{count}f', blob))

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)
