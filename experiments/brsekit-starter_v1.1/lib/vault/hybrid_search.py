"""Hybrid search combining semantic and keyword search for BrseKit v2."""
import logging
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from .embedding_store import EmbeddingStore, SearchResult
from .embedder import GeminiEmbedder

logger = logging.getLogger(__name__)


class HybridSearch:
    """Combined semantic + keyword search with configurable weights."""

    def __init__(
        self,
        project_key: str,
        embedder: Optional[GeminiEmbedder] = None,
        semantic_weight: float = 0.7,
    ):
        """Initialize hybrid search.

        Args:
            project_key: Project identifier
            embedder: Optional embedder instance
            semantic_weight: Weight for semantic score (keyword = 1 - semantic)
        """
        self.project_key = project_key
        self.semantic_weight = semantic_weight
        self.keyword_weight = 1.0 - semantic_weight
        self.embedding_store = EmbeddingStore(project_key, embedder)

    def search(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.3,
        source: Optional[str] = None,
        layer: Optional[str] = None,
    ) -> List[SearchResult]:
        """Hybrid search combining semantic and keyword results.

        Args:
            query: Search query
            top_k: Max results to return
            min_score: Minimum combined score threshold
            source: Filter by source
            layer: Filter by layer (knowledge/memory)

        Returns:
            List of SearchResult sorted by combined score
        """
        # Get semantic results
        semantic_results = self.embedding_store.search(
            query, top_k=top_k * 2, min_score=0.0, source=source, layer=layer
        )

        # Get keyword results
        keyword_results = self.embedding_store.keyword_search(
            query, top_k=top_k * 2, source=source, layer=layer
        )

        # Combine scores
        combined = self._merge_results(semantic_results, keyword_results)

        # Filter by min_score and return top_k
        filtered = [r for r in combined if r.score >= min_score]
        return filtered[:top_k]

    def _merge_results(
        self,
        semantic: List[SearchResult],
        keyword: List[SearchResult],
    ) -> List[SearchResult]:
        """Merge and re-score results from both search methods."""
        # Build score maps
        semantic_scores: Dict[str, float] = {r.item_id: r.score for r in semantic}
        keyword_scores: Dict[str, float] = {r.item_id: r.score for r in keyword}

        # Get all unique item_ids
        all_ids = set(semantic_scores.keys()) | set(keyword_scores.keys())

        # Build item map for metadata
        item_map: Dict[str, SearchResult] = {}
        for r in semantic + keyword:
            if r.item_id not in item_map:
                item_map[r.item_id] = r

        # Calculate combined scores
        results = []
        for item_id in all_ids:
            sem_score = semantic_scores.get(item_id, 0.0)
            kw_score = keyword_scores.get(item_id, 0.0)
            combined_score = (
                self.semantic_weight * sem_score + self.keyword_weight * kw_score
            )

            original = item_map[item_id]
            results.append(
                SearchResult(
                    item_id=item_id,
                    content=original.content,
                    score=combined_score,
                    source=original.source,
                    layer=original.layer,
                    metadata=original.metadata,
                )
            )

        # Sort by combined score
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def search_knowledge(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.3,
        source: Optional[str] = None,
    ) -> List[SearchResult]:
        """Search only in knowledge layer.

        Args:
            query: Search query
            top_k: Max results
            min_score: Minimum score threshold
            source: Filter by source (glossary, faq, specs, rules)

        Returns:
            List of SearchResult from knowledge layer
        """
        return self.search(
            query, top_k=top_k, min_score=min_score, source=source, layer="knowledge"
        )

    def search_memory(
        self,
        query: str,
        top_k: int = 10,
        min_score: float = 0.3,
        source: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[SearchResult]:
        """Search only in memory layer with optional date filter.

        Args:
            query: Search query
            top_k: Max results
            min_score: Minimum score threshold
            source: Filter by source (backlog, slack, email, meetings)
            start_date: Filter from date
            end_date: Filter until date

        Returns:
            List of SearchResult from memory layer
        """
        results = self.search(
            query, top_k=top_k * 2, min_score=min_score, source=source, layer="memory"
        )

        # Apply date filter if provided
        if start_date or end_date:
            results = self._filter_by_date(results, start_date, end_date)

        return results[:top_k]

    def _filter_by_date(
        self,
        results: List[SearchResult],
        start_date: Optional[date],
        end_date: Optional[date],
    ) -> List[SearchResult]:
        """Filter results by date range using metadata.

        Args:
            results: Search results to filter
            start_date: Filter from date (inclusive)
            end_date: Filter until date (inclusive)

        Returns:
            Filtered results with valid timestamps in range
        """
        filtered = []
        skipped_no_timestamp = 0
        skipped_invalid = 0

        for r in results:
            if not r.metadata or "timestamp" not in r.metadata:
                skipped_no_timestamp += 1
                continue

            try:
                ts = r.metadata["timestamp"]
                if isinstance(ts, str):
                    item_date = datetime.fromisoformat(ts).date()
                elif isinstance(ts, datetime):
                    item_date = ts.date()
                else:
                    logger.debug(f"Skipping {r.item_id}: timestamp not str/datetime")
                    skipped_invalid += 1
                    continue

                if start_date and item_date < start_date:
                    continue
                if end_date and item_date > end_date:
                    continue
                filtered.append(r)
            except (ValueError, TypeError) as e:
                logger.debug(f"Skipping {r.item_id}: invalid timestamp - {e}")
                skipped_invalid += 1
                continue

        # Log summary if items were skipped
        if skipped_no_timestamp > 0 or skipped_invalid > 0:
            logger.info(
                f"Date filter: {len(filtered)} matched, "
                f"{skipped_no_timestamp} no timestamp, {skipped_invalid} invalid"
            )

        return filtered

    def get_related(
        self,
        item_id: str,
        top_k: int = 5,
        min_score: float = 0.5,
    ) -> List[SearchResult]:
        """Find items related to a given item.

        Args:
            item_id: Source item ID to find related items for
            top_k: Max results
            min_score: Minimum similarity threshold

        Returns:
            List of related SearchResult (excludes source item)
        """
        # Get source item content
        conn = self.embedding_store._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM embeddings WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()

        if not row:
            return []

        # Search using source content
        results = self.search(row["content"], top_k=top_k + 1, min_score=min_score)

        # Filter out source item
        return [r for r in results if r.item_id != item_id][:top_k]

    def format_results(
        self,
        results: List[SearchResult],
        verbose: bool = False,
    ) -> str:
        """Format search results as markdown.

        Args:
            results: List of SearchResult
            verbose: Include full content if True

        Returns:
            Markdown formatted string
        """
        if not results:
            return "No results found."

        lines = [f"## Search Results ({len(results)} found)\n"]

        for i, r in enumerate(results, 1):
            lines.append(f"### {i}. [{r.layer or 'unknown'}] {r.source or 'unknown'}")
            lines.append(f"- **ID:** {r.item_id}")
            lines.append(f"- **Score:** {r.score:.2f}")

            if r.metadata:
                meta_str = ", ".join(
                    f"{k}: {v}" for k, v in r.metadata.items() if v and k != "content"
                )
                if meta_str:
                    lines.append(f"- **Meta:** {meta_str}")

            if verbose:
                lines.append(f"\n```\n{r.content[:500]}{'...' if len(r.content) > 500 else ''}\n```")
            else:
                snippet = r.content[:200].replace("\n", " ")
                lines.append(f"- **Preview:** {snippet}{'...' if len(r.content) > 200 else ''}")

            lines.append("")

        return "\n".join(lines)
