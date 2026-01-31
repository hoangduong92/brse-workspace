#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for new bk-spec modules."""
import sys
import os
import io

# Force UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from context_enricher import ContextEnricher, EnrichedContext
from user_story_generator import UserStoryGenerator, UserStory
from prompt_builder import PromptBuilder


def test_context_enricher():
    """Test context enricher."""
    print("Testing ContextEnricher...")

    enricher = ContextEnricher()

    # Test keyword extraction
    text = "ユーザー登録機能を実装する。メール認証が必要。"
    keywords = enricher.extract_keywords(text)
    print(f"  Keywords: {keywords[:5]}")

    # Test enrichment (without vault)
    result = enricher.enrich(text, top_k=3)
    print(f"  Original: {result.original[:50]}...")
    print(f"  Keywords count: {len(result.keywords)}")
    print(f"  Related items: {len(result.related_items)}")
    print(f"  Summary: {result.context_summary[:50]}...")

    print("  ✓ ContextEnricher working")


def test_user_story_generator():
    """Test user story generator."""
    print("\nTesting UserStoryGenerator...")

    generator = UserStoryGenerator()

    requirements = """
    ユーザー登録機能が必要
    管理者がユーザーを管理できる
    パフォーマンスは1秒以内
    """

    # Generate stories (Japanese)
    stories_ja = generator.generate(requirements, lang="ja")
    print(f"  Generated {len(stories_ja)} stories (JA)")
    if stories_ja:
        print(f"  Story 1: {generator.format_story(stories_ja[0], lang='ja')[:80]}...")

    # Test other languages
    stories_en = generator.generate(requirements, lang="en")
    print(f"  Generated {len(stories_en)} stories (EN)")

    stories_vi = generator.generate(requirements, lang="vi")
    print(f"  Generated {len(stories_vi)} stories (VI)")

    # Test markdown formatting
    markdown = generator.format_stories_markdown(stories_ja[:2], lang="ja")
    print(f"  Markdown output: {len(markdown)} characters")

    print("  ✓ UserStoryGenerator working")


def test_prompt_builder():
    """Test prompt builder."""
    print("\nTesting PromptBuilder...")

    builder = PromptBuilder()

    # List templates
    templates = builder.list_templates()
    print(f"  Available templates: {list(templates.keys())}")

    # Build prompt without context
    input_text = "ユーザー認証機能の要件定義"
    prompt = builder.build("analyze", input_text)
    print(f"  Prompt length (no context): {len(prompt)} characters")

    # Build prompt with context
    context = {
        "keywords": ["認証", "ユーザー", "セキュリティ"],
        "related_items": [
            {
                "title": "認証システム設計",
                "source": "previous-project",
                "score": 0.85
            }
        ],
        "context_summary": "過去の認証システム実装例が見つかりました"
    }

    prompt_with_context = builder.build("test", input_text, context=context)
    print(f"  Prompt length (with context): {len(prompt_with_context)} characters")

    # Test other templates
    for task_type in ["story", "gap", "viewpoint"]:
        p = builder.build(task_type, input_text)
        print(f"  Template '{task_type}': {len(p)} characters")

    print("  ✓ PromptBuilder working")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing bk-spec new modules")
    print("=" * 60)

    try:
        test_context_enricher()
        test_user_story_generator()
        test_prompt_builder()

        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
