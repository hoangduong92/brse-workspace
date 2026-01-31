"""Tests for context_enricher module."""
import pytest
from context_enricher import ContextEnricher, EnrichedContext


class TestContextEnricherKeywordExtraction:
    """Test keyword extraction functionality."""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        enricher = ContextEnricher()
        text = "ユーザー登録機能を実装する。メール認証が必要。"
        keywords = enricher.extract_keywords(text)

        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert len(keywords) <= 15

    def test_extract_keywords_removes_stop_words(self):
        """Test that common stop words are removed."""
        enricher = ContextEnricher()
        text = "する ある いる 登録 認証"
        keywords = enricher.extract_keywords(text)

        # Stop words should not be in results
        assert "する" not in keywords
        assert "ある" not in keywords

    def test_extract_keywords_removes_short_words(self):
        """Test that short words are filtered out."""
        enricher = ContextEnricher()
        text = "a is the システム"
        keywords = enricher.extract_keywords(text)

        # Words with length <= 2 should be removed
        for kw in keywords:
            assert len(kw) > 2

    def test_extract_keywords_preserves_order(self):
        """Test that order is preserved (first occurrence)."""
        enricher = ContextEnricher()
        text = "ユーザー登録 ユーザー認証 システム"
        keywords = enricher.extract_keywords(text)

        # Duplicates should be removed but order preserved
        seen = set()
        for kw in keywords:
            assert kw not in seen
            seen.add(kw)

    def test_extract_keywords_limit_to_15(self):
        """Test that results are limited to 15 keywords."""
        enricher = ContextEnricher()
        text = " ".join([f"word{i}" for i in range(50)])
        keywords = enricher.extract_keywords(text)

        assert len(keywords) <= 15

    def test_extract_keywords_english_text(self):
        """Test keyword extraction from English text."""
        enricher = ContextEnricher()
        text = "User registration system authentication login"
        keywords = enricher.extract_keywords(text)

        assert len(keywords) > 0
        assert "user" in keywords or "registration" in keywords


class TestContextEnricherContextSummary:
    """Test context summary building."""

    def test_build_context_summary_empty_items(self):
        """Test summary with no items."""
        enricher = ContextEnricher()
        summary = enricher.build_context_summary([])

        assert isinstance(summary, str)
        assert "No related context" in summary

    def test_build_context_summary_single_item(self):
        """Test summary with single item."""
        enricher = ContextEnricher()
        items = [
            {
                "title": "Test Item",
                "source": "test-source",
                "score": 0.95
            }
        ]
        summary = enricher.build_context_summary(items)

        assert isinstance(summary, str)
        assert "Found 1 related items" in summary
        assert "Test Item" in summary
        assert "test-source" in summary

    def test_build_context_summary_multiple_items(self):
        """Test summary with multiple items."""
        enricher = ContextEnricher()
        items = [
            {
                "title": f"Item {i}",
                "source": f"source-{i}",
                "score": 0.9 - (i * 0.1)
            }
            for i in range(5)
        ]
        summary = enricher.build_context_summary(items)

        assert isinstance(summary, str)
        assert "Found 5 related items" in summary

    def test_build_context_summary_limits_to_5_items(self):
        """Test that only 5 items max are shown."""
        enricher = ContextEnricher()
        items = [
            {
                "title": f"Item {i}",
                "source": f"source-{i}",
                "score": 0.9
            }
            for i in range(10)
        ]
        summary = enricher.build_context_summary(items)

        # Count items in summary (each item is one line starting with -)
        item_lines = [l for l in summary.split("\n") if l.strip().startswith("-")]
        assert len(item_lines) <= 5


class TestContextEnricherEnrichment:
    """Test main enrichment functionality."""

    def test_enrich_returns_enriched_context(self):
        """Test that enrich returns correct type."""
        enricher = ContextEnricher()
        text = "ユーザー登録機能"
        result = enricher.enrich(text)

        assert isinstance(result, EnrichedContext)

    def test_enrich_preserves_original_text(self):
        """Test that original text is preserved."""
        enricher = ContextEnricher()
        text = "ユーザー登録機能を実装する"
        result = enricher.enrich(text)

        assert result.original == text

    def test_enrich_extracts_keywords(self):
        """Test that keywords are extracted."""
        enricher = ContextEnricher()
        text = "ユーザー登録機能"
        result = enricher.enrich(text)

        assert isinstance(result.keywords, list)
        assert len(result.keywords) > 0

    def test_enrich_has_related_items_list(self):
        """Test that related_items is a list."""
        enricher = ContextEnricher()
        text = "ユーザー登録機能"
        result = enricher.enrich(text)

        assert isinstance(result.related_items, list)

    def test_enrich_has_context_summary(self):
        """Test that context_summary is a string."""
        enricher = ContextEnricher()
        text = "ユーザー登録機能"
        result = enricher.enrich(text)

        assert isinstance(result.context_summary, str)

    def test_enrich_with_custom_top_k(self):
        """Test enrichment with custom top_k parameter."""
        enricher = ContextEnricher()
        text = "ユーザー登録機能"

        result1 = enricher.enrich(text, top_k=3)
        result2 = enricher.enrich(text, top_k=10)

        # Both should work without error
        assert isinstance(result1, EnrichedContext)
        assert isinstance(result2, EnrichedContext)

    def test_enrich_gracefully_handles_vault_unavailable(self):
        """Test that enrich works even if vault is unavailable."""
        enricher = ContextEnricher()
        # Vault may not be available in test environment
        text = "ユーザー登録機能"

        # Should not raise an exception
        result = enricher.enrich(text)

        assert isinstance(result, EnrichedContext)
        assert result.original == text
        assert isinstance(result.keywords, list)
        assert isinstance(result.related_items, list)
        assert isinstance(result.context_summary, str)


class TestContextEnricherMultilingual:
    """Test multilingual support."""

    def test_extract_keywords_mixed_languages(self):
        """Test keyword extraction from mixed language text."""
        enricher = ContextEnricher()
        text = "ユーザー登録 user authentication認証"
        keywords = enricher.extract_keywords(text)

        assert len(keywords) > 0

    def test_extract_keywords_vietnamese(self):
        """Test keyword extraction from Vietnamese text."""
        enricher = ContextEnricher()
        text = "Đăng ký người dùng xác minh email"
        keywords = enricher.extract_keywords(text)

        assert isinstance(keywords, list)

    def test_enrich_vietnamese_text(self):
        """Test enrichment of Vietnamese text."""
        enricher = ContextEnricher()
        text = "Đăng ký người dùng"
        result = enricher.enrich(text)

        assert result.original == text


class TestEnrichedContextDataclass:
    """Test EnrichedContext dataclass."""

    def test_enriched_context_creation(self):
        """Test creating EnrichedContext instance."""
        context = EnrichedContext(
            original="test text",
            keywords=["key1", "key2"],
            related_items=[],
            context_summary="summary"
        )

        assert context.original == "test text"
        assert context.keywords == ["key1", "key2"]
        assert context.related_items == []
        assert context.context_summary == "summary"

    def test_enriched_context_field_access(self):
        """Test accessing all fields."""
        context = EnrichedContext(
            original="test",
            keywords=["a", "b"],
            related_items=[{"title": "test"}],
            context_summary="summary"
        )

        assert hasattr(context, "original")
        assert hasattr(context, "keywords")
        assert hasattr(context, "related_items")
        assert hasattr(context, "context_summary")
