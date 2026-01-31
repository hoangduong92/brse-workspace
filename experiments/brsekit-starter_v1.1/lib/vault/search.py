"""Semantic search with cosine similarity."""
import math
from typing import List, Optional
from dataclasses import dataclass

from .db import VaultDB
from .embedder import GeminiEmbedder
from .store import VaultStore, VaultItem


@dataclass
class SearchResult:
    """Search result with similarity score."""
    item: VaultItem
    score: float


class VaultSearch:
    """Semantic search for vault items."""

    def __init__(self, embedder: GeminiEmbedder):
        """Initialize search with embedder."""
        self.embedder = embedder
        self.store = VaultStore()
        VaultDB.initialize()

    def query(
        self,
        text: str,
        top_k: int = 10,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar items across all sources."""
        query_embedding = self.embedder.embed_query(text)
        return self._search_by_embedding(query_embedding, top_k, min_score)

    def query_by_source(
        self,
        text: str,
        source: str,
        top_k: int = 10,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar items within specific source."""
        query_embedding = self.embedder.embed_query(text)
        return self._search_by_embedding(
            query_embedding,
            top_k,
            min_score,
            source
        )

    def _search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int,
        min_score: float,
        source: Optional[str] = None
    ) -> List[SearchResult]:
        """Search using brute-force cosine similarity."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        # Fetch all items with embeddings
        if source:
            cursor.execute("""
                SELECT id, source, title, content, embedding, metadata,
                       created_at, updated_at
                FROM vault_items
                WHERE source = ? AND embedding IS NOT NULL
            """, (source,))
        else:
            cursor.execute("""
                SELECT id, source, title, content, embedding, metadata,
                       created_at, updated_at
                FROM vault_items
                WHERE embedding IS NOT NULL
            """)

        results = []
        for row in cursor.fetchall():
            item = self.store._row_to_item(row)
            if item.embedding:
                score = self._cosine_similarity(query_embedding, item.embedding)
                if score >= min_score:
                    results.append(SearchResult(item=item, score=score))

        # Sort by score descending and return top-k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)
