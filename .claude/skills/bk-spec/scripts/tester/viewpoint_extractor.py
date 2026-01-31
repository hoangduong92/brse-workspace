"""Viewpoint extractor for bk-spec - create test viewpoint tables."""
from typing import List
from dataclasses import dataclass


@dataclass
class Viewpoint:
    """Test viewpoint entry."""
    category: str
    viewpoint: str
    description: str
    priority: str


class ViewpointExtractor:
    """Extract test viewpoints from requirements."""

    # Standard viewpoint categories
    CATEGORIES = {
        "機能性": ["basic functionality", "正常系", "異常系"],
        "境界値": ["boundary values", "limits", "min/max"],
        "セキュリティ": ["authentication", "authorization", "injection"],
        "性能": ["response time", "load", "stress"],
        "ユーザビリティ": ["usability", "accessibility", "UX"],
    }

    def extract(self, requirements: str) -> List[Viewpoint]:
        """Extract viewpoints from requirements.

        Args:
            requirements: Requirements text

        Returns:
            List of Viewpoint objects
        """
        viewpoints = []
        text_lower = requirements.lower()

        # Always add basic functional viewpoints
        viewpoints.append(Viewpoint(
            category="機能性",
            viewpoint="正常系テスト",
            description="Normal flow testing - happy path scenarios",
            priority="高"
        ))
        viewpoints.append(Viewpoint(
            category="機能性",
            viewpoint="異常系テスト",
            description="Error flow testing - invalid inputs, edge cases",
            priority="高"
        ))

        # Add boundary viewpoints
        if any(kw in text_lower for kw in ["input", "入力", "value", "number"]):
            viewpoints.append(Viewpoint(
                category="境界値",
                viewpoint="境界値テスト",
                description="Test at boundary conditions (min, max, min-1, max+1)",
                priority="中"
            ))

        # Add security viewpoints
        if any(kw in text_lower for kw in ["login", "auth", "password", "ログイン"]):
            viewpoints.append(Viewpoint(
                category="セキュリティ",
                viewpoint="認証テスト",
                description="Authentication and session management testing",
                priority="高"
            ))

        # Add performance viewpoints
        if any(kw in text_lower for kw in ["performance", "response", "性能"]):
            viewpoints.append(Viewpoint(
                category="性能",
                viewpoint="レスポンステスト",
                description="Response time measurement under normal load",
                priority="中"
            ))

        return viewpoints

    def format_table(self, viewpoints: List[Viewpoint]) -> str:
        """Format viewpoints as markdown table.

        Args:
            viewpoints: List of Viewpoint

        Returns:
            Markdown table
        """
        lines = [
            "# テスト観点表 (Viewpoint Table)\n",
            "| カテゴリ | 観点 | 説明 | 優先度 |",
            "|----------|------|------|--------|"
        ]

        for vp in viewpoints:
            lines.append(f"| {vp.category} | {vp.viewpoint} | {vp.description[:50]} | {vp.priority} |")

        return "\n".join(lines)
