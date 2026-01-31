"""Context summarizer for bk-recall."""
import os
from typing import Optional, List

from search_handler import SearchHandler


class Summarizer:
    """Generate context summaries from vault items."""

    def __init__(self):
        """Initialize summarizer."""
        self.search = SearchHandler()

    def summarize(
        self,
        topic: Optional[str] = None,
        source: Optional[str] = None,
        top_k: int = 10
    ) -> str:
        """Generate summary of relevant context.

        Args:
            topic: Topic to summarize (searches vault if provided)
            source: Filter by source
            top_k: Number of items to include

        Returns:
            Markdown summary
        """
        if topic:
            results = self.search.query(topic, source=source, top_k=top_k)
        else:
            # Get recent items
            results = self.search.query("project status update", source=source, top_k=top_k)

        if not results:
            return "No relevant context found in vault."

        # Build context for summary
        context_items = []
        for r in results:
            item = r.item
            context_items.append({
                "source": item.source,
                "title": item.title,
                "content": item.content[:500],
                "score": r.score
            })

        # Generate summary structure
        summary = self._build_summary(topic, context_items)
        return summary

    def _build_summary(self, topic: Optional[str], items: List[dict]) -> str:
        """Build markdown summary from items.

        Args:
            topic: Summary topic
            items: Context items

        Returns:
            Markdown summary
        """
        lines = []

        if topic:
            lines.append(f"# Context Summary: {topic}\n")
        else:
            lines.append("# Project Context Summary\n")

        # Group by source
        by_source = {}
        for item in items:
            src = item["source"]
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(item)

        # Summary stats
        lines.append(f"**Total items:** {len(items)}")
        lines.append(f"**Sources:** {', '.join(by_source.keys())}\n")

        # Key points from each source
        for source, source_items in by_source.items():
            lines.append(f"## {source.title()} ({len(source_items)} items)\n")

            for item in source_items[:5]:
                title = item["title"] or "(No title)"
                snippet = item["content"][:150].replace("\n", " ")
                lines.append(f"- **{title}**: {snippet}...")

            lines.append("")

        # Prompt for LLM summary (if available)
        lines.append("---")
        lines.append("*Use this context to answer questions about the project.*")

        return "\n".join(lines)
