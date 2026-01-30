"""Per-project embedding store for BrseKit v2 semantic search."""
import json
import logging
import re
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .embedder import GeminiEmbedder

logger = logging.getLogger(__name__)

# Valid layer values
VALID_LAYERS = {"knowledge", "memory"}


@dataclass
class EmbeddingItem:
    """Item with embedding vector."""
    item_id: str
    content: str
    embedding: Optional[List[float]] = None
    source: Optional[str] = None
    layer: Optional[str] = None  # "knowledge" or "memory"
    metadata: Optional[Dict[str, Any]] = None
    indexed_at: Optional[datetime] = None


@dataclass
class SearchResult:
    """Search result with score."""
    item_id: str
    content: str
    score: float
    source: Optional[str] = None
    layer: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EmbeddingStore:
    """Per-project embedding database for semantic search."""

    _local = threading.local()

    def __init__(self, project_key: str, embedder: Optional[GeminiEmbedder] = None):
        """Initialize embedding store for project.

        Args:
            project_key: Project identifier
            embedder: Optional GeminiEmbedder instance (lazy init if None)
        """
        self.project_key = project_key
        self._embedder = embedder
        self._db_path = (
            Path.home() / ".brsekit" / "db" / "embeddings" / f"{project_key}.db"
        )
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _get_embedder(self) -> GeminiEmbedder:
        """Lazy init embedder."""
        if self._embedder is None:
            self._embedder = GeminiEmbedder()
        return self._embedder

    def _get_conn(self) -> sqlite3.Connection:
        """Get thread-local connection."""
        conn_key = f"emb_{self.project_key}"
        if not hasattr(self._local, conn_key):
            conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            conn.row_factory = sqlite3.Row
            setattr(self._local, conn_key, conn)
        return getattr(self._local, conn_key)

    def _init_schema(self):
        """Create tables and FTS index."""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Main embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                item_id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                embedding TEXT,
                source TEXT,
                layer TEXT,
                metadata TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # FTS5 for keyword search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS embeddings_fts USING fts5(
                item_id, content, source, layer,
                content='embeddings',
                content_rowid='rowid'
            )
        """)

        # Triggers to keep FTS in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS embeddings_ai AFTER INSERT ON embeddings BEGIN
                INSERT INTO embeddings_fts(rowid, item_id, content, source, layer)
                VALUES (new.rowid, new.item_id, new.content, new.source, new.layer);
            END
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS embeddings_ad AFTER DELETE ON embeddings BEGIN
                INSERT INTO embeddings_fts(embeddings_fts, rowid, item_id, content, source, layer)
                VALUES ('delete', old.rowid, old.item_id, old.content, old.source, old.layer);
            END
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS embeddings_au AFTER UPDATE ON embeddings BEGIN
                INSERT INTO embeddings_fts(embeddings_fts, rowid, item_id, content, source, layer)
                VALUES ('delete', old.rowid, old.item_id, old.content, old.source, old.layer);
                INSERT INTO embeddings_fts(rowid, item_id, content, source, layer)
                VALUES (new.rowid, new.item_id, new.content, new.source, new.layer);
            END
        """)

        # Indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emb_source ON embeddings(source)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emb_layer ON embeddings(layer)"
        )
        conn.commit()

    def index_item(
        self,
        item_id: str,
        content: str,
        source: Optional[str] = None,
        layer: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Index single item with embedding.

        Args:
            item_id: Unique identifier (required, non-empty)
            content: Text content to index (required, non-empty)
            source: Source type (backlog, slack, email, etc.)
            layer: Must be 'knowledge' or 'memory' if provided

        Returns:
            True if indexed, False if validation fails or error
        """
        # Input validation
        if not item_id or not isinstance(item_id, str):
            logger.warning("Invalid item_id: must be non-empty string")
            return False
        if not content or not isinstance(content, str):
            logger.warning("Invalid content: must be non-empty string")
            return False
        if layer and layer not in VALID_LAYERS:
            logger.warning(f"Invalid layer '{layer}': must be one of {VALID_LAYERS}")
            return False

        try:
            embedding = self._get_embedder().embed(content)
            return self._store_item(item_id, content, embedding, source, layer, metadata)
        except Exception as e:
            # Log and store without embedding if embedding fails
            logger.warning(f"Embedding failed for {item_id}: {e}")
            return self._store_item(item_id, content, None, source, layer, metadata)

    def _store_item(
        self,
        item_id: str,
        content: str,
        embedding: Optional[List[float]],
        source: Optional[str],
        layer: Optional[str],
        metadata: Optional[Dict[str, Any]],
    ) -> bool:
        """Store item in database."""
        conn = self._get_conn()
        cursor = conn.cursor()

        embedding_json = json.dumps(embedding) if embedding else None
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute(
            """
            INSERT INTO embeddings (item_id, content, embedding, source, layer, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
                content = excluded.content,
                embedding = excluded.embedding,
                source = excluded.source,
                layer = excluded.layer,
                metadata = excluded.metadata,
                indexed_at = CURRENT_TIMESTAMP
        """,
            (item_id, content, embedding_json, source, layer, metadata_json),
        )
        conn.commit()
        return True

    def index_batch(
        self,
        items: List[Dict[str, Any]],
    ) -> int:
        """Index batch of items.

        Args:
            items: List of dicts with keys: item_id, content, source?, layer?, metadata?

        Returns:
            Number of items indexed
        """
        count = 0
        for item in items:
            if self.index_item(
                item_id=item["item_id"],
                content=item["content"],
                source=item.get("source"),
                layer=item.get("layer"),
                metadata=item.get("metadata"),
            ):
                count += 1
        return count

    def delete_item(self, item_id: str) -> bool:
        """Delete item from index."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM embeddings WHERE item_id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.3,
        source: Optional[str] = None,
        layer: Optional[str] = None,
    ) -> List[SearchResult]:
        """Semantic search using embeddings.

        Args:
            query: Search query
            top_k: Max results
            min_score: Minimum similarity threshold
            source: Filter by source
            layer: Filter by layer (knowledge/memory)

        Returns:
            List of SearchResult sorted by score
        """
        query_embedding = self._get_embedder().embed_query(query)
        return self._search_by_embedding(
            query_embedding, top_k, min_score, source, layer
        )

    def _search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int,
        min_score: float,
        source: Optional[str],
        layer: Optional[str],
        max_candidates: int = 1000,
    ) -> List[SearchResult]:
        """Search using cosine similarity.

        Args:
            max_candidates: Limit initial fetch for performance (default 1000).
                           For larger datasets, consider using approximate nearest neighbor.
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        # Build query with filters and limit for performance
        sql = "SELECT * FROM embeddings WHERE embedding IS NOT NULL"
        params: List[Any] = []
        if source:
            sql += " AND source = ?"
            params.append(source)
        if layer:
            sql += " AND layer = ?"
            params.append(layer)
        # Order by most recent for relevance and limit candidates
        sql += " ORDER BY indexed_at DESC LIMIT ?"
        params.append(max_candidates)

        cursor.execute(sql, params)

        results = []
        for row in cursor.fetchall():
            embedding = json.loads(row["embedding"])
            score = self._cosine_similarity(query_embedding, embedding)
            if score >= min_score:
                results.append(
                    SearchResult(
                        item_id=row["item_id"],
                        content=row["content"],
                        score=score,
                        source=row["source"],
                        layer=row["layer"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else None,
                    )
                )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity."""
        if len(vec1) != len(vec2):
            return 0.0

        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5

        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)

    def _sanitize_fts_query(self, query: str) -> str:
        """Sanitize query for FTS5 to prevent injection.

        Escapes special FTS5 characters and wraps in quotes for phrase search.
        """
        # Remove/escape FTS5 special characters: " * - + ^ : ( ) { } [ ]
        sanitized = re.sub(r'[\"*\-+^:\(\)\{\}\[\]]', ' ', query)
        # Collapse multiple spaces
        sanitized = ' '.join(sanitized.split())
        # Wrap in quotes for phrase search
        return f'"{sanitized}"' if sanitized else '""'

    def keyword_search(
        self,
        query: str,
        top_k: int = 10,
        source: Optional[str] = None,
        layer: Optional[str] = None,
    ) -> List[SearchResult]:
        """Full-text keyword search using FTS5."""
        conn = self._get_conn()
        cursor = conn.cursor()

        # Sanitize FTS query to prevent injection
        fts_query = self._sanitize_fts_query(query)
        sql = """
            SELECT e.*, bm25(embeddings_fts) as rank
            FROM embeddings_fts f
            JOIN embeddings e ON e.item_id = f.item_id
            WHERE embeddings_fts MATCH ?
        """
        params = [fts_query]

        if source:
            sql += " AND e.source = ?"
            params.append(source)
        if layer:
            sql += " AND e.layer = ?"
            params.append(layer)

        sql += " ORDER BY rank LIMIT ?"
        params.append(top_k)

        cursor.execute(sql, params)

        results = []
        for row in cursor.fetchall():
            # Normalize BM25 score to 0-1 range
            bm25_score = abs(row["rank"])  # BM25 returns negative
            normalized_score = min(1.0, bm25_score / 10.0)

            results.append(
                SearchResult(
                    item_id=row["item_id"],
                    content=row["content"],
                    score=normalized_score,
                    source=row["source"],
                    layer=row["layer"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None,
                )
            )
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        conn = self._get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM embeddings")
        total = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COUNT(*) as with_emb FROM embeddings WHERE embedding IS NOT NULL"
        )
        with_emb = cursor.fetchone()["with_emb"]

        cursor.execute("SELECT DISTINCT source FROM embeddings WHERE source IS NOT NULL")
        sources = [row["source"] for row in cursor.fetchall()]

        cursor.execute("SELECT MAX(indexed_at) as last FROM embeddings")
        last = cursor.fetchone()["last"]

        return {
            "total_items": total,
            "items_with_embedding": with_emb,
            "sources": sources,
            "last_indexed": last,
        }

    def close(self):
        """Close database connection."""
        conn_key = f"emb_{self.project_key}"
        if hasattr(self._local, conn_key):
            conn = getattr(self._local, conn_key)
            conn.close()
            delattr(self._local, conn_key)
