"""Search handler for bk-recall - semantic search via vault."""
import os
import sys
from typing import List, Optional, Union

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from vault import VaultSearch, GeminiEmbedder, SearchResult
from vault.hybrid_search import HybridSearch
from vault.hybrid_search import SearchResult as HybridSearchResult


class SearchHandler:
    """Handle semantic search queries against vault (v1) or project (v2)."""

    def __init__(self, project_key: Optional[str] = None):
        """Initialize search handler.

        Args:
            project_key: If provided, use v2 per-project hybrid search
        """
        self.project_key = project_key
        self.embedder = None
        self.search = None
        self.hybrid_search = None

    def _ensure_initialized(self):
        """Lazy initialization of embedder and search."""
        if self.project_key:
            # v2: per-project hybrid search
            if self.hybrid_search is None:
                self.hybrid_search = HybridSearch(self.project_key)
        else:
            # v1: legacy vault search
            if self.embedder is None:
                self.embedder = GeminiEmbedder()
                self.search = VaultSearch(self.embedder)

    def query(
        self,
        text: str,
        source: Optional[str] = None,
        top_k: int = 10,
        min_score: float = 0.3,
        layer: Optional[str] = None,
    ) -> List[Union[SearchResult, HybridSearchResult]]:
        """Search for items matching query.

        Args:
            text: Search query text
            source: Filter by source (email, backlog, slack, etc.)
            top_k: Max results to return
            min_score: Minimum similarity score
            layer: Filter by layer (knowledge/memory) - v2 only

        Returns:
            List of SearchResult objects
        """
        self._ensure_initialized()

        if self.project_key:
            # v2: use hybrid search
            return self.hybrid_search.search(
                text, top_k=top_k, min_score=min_score, source=source, layer=layer
            )
        else:
            # v1: legacy vault search
            if source:
                return self.search.query_by_source(text, source, top_k, min_score)
            return self.search.query(text, top_k, min_score)

    def format_results(
        self,
        results: List[Union[SearchResult, HybridSearchResult]],
        verbose: bool = False,
    ) -> str:
        """Format search results as markdown.

        Args:
            results: List of SearchResult (v1) or HybridSearchResult (v2)
            verbose: Include full content

        Returns:
            Markdown formatted string
        """
        if not results:
            return "No results found."

        # Use hybrid search formatter if in v2 mode
        if self.project_key and self.hybrid_search:
            return self.hybrid_search.format_results(results, verbose)

        # v1 format
        lines = [f"## Search Results ({len(results)} found)\n"]

        for i, r in enumerate(results, 1):
            # Handle both v1 (item attribute) and v2 (flat attributes) results
            if hasattr(r, "item"):
                # v1 format
                item = r.item
                title = item.title or "(No title)"
                source = item.source
                content = item.content
                metadata = item.metadata
            else:
                # v2 format (HybridSearchResult)
                title = r.item_id
                source = r.source or "unknown"
                content = r.content
                metadata = r.metadata

            score = r.score

            lines.append(f"### {i}. {title}")
            lines.append(f"- **Source:** {source}")
            lines.append(f"- **Score:** {score:.2f}")

            if metadata:
                meta_str = ", ".join(f"{k}: {v}" for k, v in metadata.items() if v)
                if meta_str:
                    lines.append(f"- **Meta:** {meta_str}")

            if verbose:
                lines.append(f"\n```\n{content[:500]}{'...' if len(content) > 500 else ''}\n```")
            else:
                snippet = content[:200].replace("\n", " ")
                lines.append(f"- **Preview:** {snippet}{'...' if len(content) > 200 else ''}")

            lines.append("")

        return "\n".join(lines)
