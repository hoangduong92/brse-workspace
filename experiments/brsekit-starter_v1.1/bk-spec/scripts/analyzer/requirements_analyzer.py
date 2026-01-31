"""Requirements analyzer for bk-spec."""
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    """Result of requirement analysis."""
    functional: List[str]
    non_functional: List[str]
    ambiguities: List[str]
    questions: List[str]


class RequirementsAnalyzer:
    """Analyze requirements documents."""

    # Keywords for categorization
    FUNCTIONAL_KEYWORDS = [
        "shall", "must", "機能", "できる", "表示", "入力", "出力",
        "登録", "削除", "更新", "検索", "ログイン", "認証"
    ]

    NON_FUNCTIONAL_KEYWORDS = [
        "performance", "security", "性能", "セキュリティ", "可用性",
        "スケーラビリティ", "response time", "99.9%", "秒以内"
    ]

    AMBIGUITY_INDICATORS = [
        "など", "etc", "適切な", "必要に応じて", "可能な限り",
        "some", "many", "various", "appropriate"
    ]

    def analyze(self, requirements: str) -> AnalysisResult:
        """Analyze requirements text.

        Args:
            requirements: Requirements document text

        Returns:
            AnalysisResult with categorized requirements
        """
        lines = [l.strip() for l in requirements.split("\n") if l.strip()]

        functional = []
        non_functional = []
        ambiguities = []
        questions = []

        for line in lines:
            # Check for ambiguities
            for indicator in self.AMBIGUITY_INDICATORS:
                if indicator.lower() in line.lower():
                    ambiguities.append(f"Ambiguous: '{line[:80]}...'")
                    questions.append(f"Clarify: {line[:50]}...")
                    break

            # Categorize
            is_functional = any(kw in line.lower() for kw in self.FUNCTIONAL_KEYWORDS)
            is_non_functional = any(kw in line.lower() for kw in self.NON_FUNCTIONAL_KEYWORDS)

            if is_non_functional:
                non_functional.append(line)
            elif is_functional:
                functional.append(line)

        # Generate questions for gaps
        if not non_functional:
            questions.append("No non-functional requirements specified. What are the performance targets?")
        if len(functional) < 3:
            questions.append("Limited functional requirements. Are there additional features?")

        return AnalysisResult(
            functional=functional,
            non_functional=non_functional,
            ambiguities=ambiguities,
            questions=questions
        )

    def format_analysis(self, result: AnalysisResult) -> str:
        """Format analysis as markdown.

        Args:
            result: AnalysisResult

        Returns:
            Markdown string
        """
        lines = ["# Requirements Analysis\n"]

        lines.append(f"## Functional Requirements ({len(result.functional)})")
        for req in result.functional[:10]:
            lines.append(f"- {req[:100]}")
        lines.append("")

        lines.append(f"## Non-Functional Requirements ({len(result.non_functional)})")
        for req in result.non_functional[:10]:
            lines.append(f"- {req[:100]}")
        lines.append("")

        if result.ambiguities:
            lines.append(f"## Ambiguities Found ({len(result.ambiguities)})")
            for amb in result.ambiguities[:5]:
                lines.append(f"- {amb}")
            lines.append("")

        if result.questions:
            lines.append("## Clarifying Questions")
            for q in result.questions:
                lines.append(f"- [ ] {q}")

        return "\n".join(lines)
