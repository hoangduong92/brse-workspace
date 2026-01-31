"""Test case generator for bk-spec."""
from typing import List
from dataclasses import dataclass


@dataclass
class TestCase:
    """Test case entry."""
    id: str
    category: str
    title: str
    precondition: str
    steps: List[str]
    expected: str
    priority: str


class TestCaseGenerator:
    """Generate test cases from requirements."""

    def generate(self, requirements: str, feature: str = None) -> List[TestCase]:
        """Generate test cases from requirements.

        Args:
            requirements: Requirements text
            feature: Specific feature to focus on

        Returns:
            List of TestCase objects
        """
        cases = []
        case_num = 1

        # Basic positive test
        cases.append(TestCase(
            id=f"TC-{case_num:03d}",
            category="正常系",
            title="正常入力での動作確認",
            precondition="システムにアクセス可能な状態",
            steps=["1. 正常な入力値を入力", "2. 実行ボタンをクリック"],
            expected="正常に処理が完了すること",
            priority="高"
        ))
        case_num += 1

        # Basic negative test
        cases.append(TestCase(
            id=f"TC-{case_num:03d}",
            category="異常系",
            title="異常入力でのエラー表示確認",
            precondition="システムにアクセス可能な状態",
            steps=["1. 異常な入力値を入力", "2. 実行ボタンをクリック"],
            expected="適切なエラーメッセージが表示されること",
            priority="高"
        ))
        case_num += 1

        # Required field test
        cases.append(TestCase(
            id=f"TC-{case_num:03d}",
            category="異常系",
            title="必須項目未入力時の確認",
            precondition="入力フォームが表示されている状態",
            steps=["1. 必須項目を空欄のまま", "2. 実行ボタンをクリック"],
            expected="必須項目のエラーが表示されること",
            priority="中"
        ))
        case_num += 1

        # Boundary test
        cases.append(TestCase(
            id=f"TC-{case_num:03d}",
            category="境界値",
            title="最大文字数での入力確認",
            precondition="文字入力フィールドがある状態",
            steps=["1. 最大文字数を入力", "2. 実行ボタンをクリック"],
            expected="正常に処理されること",
            priority="中"
        ))

        return cases

    def format_cases(self, cases: List[TestCase]) -> str:
        """Format test cases as markdown.

        Args:
            cases: List of TestCase

        Returns:
            Markdown formatted test cases
        """
        lines = ["# テストケース一覧\n"]

        for case in cases:
            lines.append(f"## {case.id}: {case.title}")
            lines.append(f"- **カテゴリ:** {case.category}")
            lines.append(f"- **優先度:** {case.priority}")
            lines.append(f"- **事前条件:** {case.precondition}")
            lines.append("- **手順:**")
            for step in case.steps:
                lines.append(f"  {step}")
            lines.append(f"- **期待結果:** {case.expected}")
            lines.append("")

        return "\n".join(lines)
