"""Context enricher for bk-spec - query bk-recall for related context."""
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

# Add lib to path for vault access
_lib_dir = Path(__file__).parent.parent.parent / "lib"
sys.path.insert(0, str(_lib_dir))

try:
    from vault.search import VaultSearch
    from vault.embedder import GeminiEmbedder
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


@dataclass
class EnrichedContext:
    """Enriched context with vault items."""
    original: str
    keywords: List[str]
    related_items: List[Dict]
    context_summary: str


class ContextEnricher:
    """Enrich requirements with context from vault."""

    def __init__(self):
        """Initialize enricher with vault search."""
        self.vault_available = VAULT_AVAILABLE
        if self.vault_available:
            try:
                api_key = os.getenv("GOOGLE_API_KEY")
                if api_key:
                    embedder = GeminiEmbedder(api_key)
                    self.search = VaultSearch(embedder)
                else:
                    self.vault_available = False
            except Exception:
                self.vault_available = False

    def enrich(self, input_text: str, top_k: int = 5) -> EnrichedContext:
        """Enrich input with relevant context from vault.

        Args:
            input_text: Requirements or feature description
            top_k: Number of relevant items to retrieve

        Returns:
            EnrichedContext with original text, keywords, and related items
        """
        keywords = self.extract_keywords(input_text)
        related_items = []

        if self.vault_available:
            try:
                results = self.search.query(input_text, top_k=top_k, min_score=0.5)
                related_items = [
                    {
                        "title": r.item.title,
                        "content": r.item.content[:200],
                        "source": r.item.source,
                        "score": round(r.score, 3)
                    }
                    for r in results
                ]
            except Exception as e:
                # Graceful degradation if vault search fails
                pass

        context_summary = self.build_context_summary(related_items)

        return EnrichedContext(
            original=input_text,
            keywords=keywords,
            related_items=related_items,
            context_summary=context_summary
        )

    def extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from text for search.

        Extracts technical terms, feature names, and key phrases.
        """
        # Remove common words
        stop_words = {
            "する", "できる", "ある", "いる", "なる", "れる", "られる",
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "có", "là", "được", "của", "cho"
        }

        # Extract words (Japanese, English, Vietnamese mixed)
        words = re.findall(r'[\w]+', text.lower())

        # Filter by length and stop words
        keywords = [
            w for w in words
            if len(w) > 2 and w not in stop_words
        ]

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords[:15]  # Top 15 keywords

    def build_context_summary(self, items: List[Dict]) -> str:
        """Summarize related context items.

        Builds a concise summary of related vault items.
        """
        if not items:
            return "No related context found in vault."

        lines = [f"Found {len(items)} related items:"]
        for item in items[:5]:
            lines.append(
                f"- [{item['source']}] {item['title']} "
                f"(score: {item['score']})"
            )

        return "\n".join(lines)
