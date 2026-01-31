"""Gap detector for bk-spec - find missing requirements."""
from typing import List
from dataclasses import dataclass


@dataclass
class Gap:
    """Detected gap in requirements."""
    category: str
    description: str
    severity: str  # high, medium, low


class GapDetector:
    """Detect gaps in requirements."""

    # Common missing areas
    CHECKLIST = {
        "security": ["認証", "認可", "暗号化", "auth", "security", "password"],
        "error_handling": ["エラー", "例外", "error", "exception", "failure"],
        "performance": ["性能", "レスポンス", "performance", "latency", "throughput"],
        "validation": ["バリデーション", "validation", "check", "verify"],
        "logging": ["ログ", "監査", "log", "audit", "trace"],
        "edge_cases": ["境界", "上限", "下限", "boundary", "limit", "max", "min"]
    }

    def detect(self, requirements: str) -> List[Gap]:
        """Detect gaps in requirements.

        Args:
            requirements: Requirements text

        Returns:
            List of detected gaps
        """
        text_lower = requirements.lower()
        gaps = []

        for category, keywords in self.CHECKLIST.items():
            found = any(kw in text_lower for kw in keywords)

            if not found:
                gaps.append(Gap(
                    category=category,
                    description=f"No {category.replace('_', ' ')} requirements specified",
                    severity="medium" if category in ["security", "error_handling"] else "low"
                ))

        # Check for acceptance criteria
        if "受け入れ基準" not in requirements and "acceptance" not in text_lower:
            gaps.append(Gap(
                category="acceptance_criteria",
                description="No acceptance criteria defined",
                severity="high"
            ))

        return gaps

    def format_gaps(self, gaps: List[Gap]) -> str:
        """Format gaps as markdown.

        Args:
            gaps: List of Gap objects

        Returns:
            Markdown string
        """
        if not gaps:
            return "No significant gaps detected."

        lines = ["## Requirement Gaps\n"]

        # Group by severity
        high = [g for g in gaps if g.severity == "high"]
        medium = [g for g in gaps if g.severity == "medium"]
        low = [g for g in gaps if g.severity == "low"]

        if high:
            lines.append("### High Priority")
            for g in high:
                lines.append(f"- **{g.category}**: {g.description}")
            lines.append("")

        if medium:
            lines.append("### Medium Priority")
            for g in medium:
                lines.append(f"- **{g.category}**: {g.description}")
            lines.append("")

        if low:
            lines.append("### Low Priority")
            for g in low:
                lines.append(f"- **{g.category}**: {g.description}")

        return "\n".join(lines)
