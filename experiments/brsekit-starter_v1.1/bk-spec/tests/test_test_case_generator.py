"""Tests for test_case_generator module."""
import pytest
from tester.test_case_generator import TestCaseGenerator, TestCase


class TestTestCaseDataclass:
    """Test TestCase dataclass."""

    def test_test_case_creation(self):
        """Test creating TestCase instance."""
        case = TestCase(
            id="TC-001",
            category="正常系",
            title="Test normal flow",
            precondition="System ready",
            steps=["Step 1", "Step 2"],
            expected="Pass",
            priority="高"
        )

        assert case.id == "TC-001"
        assert case.category == "正常系"
        assert case.title == "Test normal flow"
        assert len(case.steps) == 2
        assert case.priority == "高"


class TestTestCaseGeneratorBasic:
    """Test basic test case generation."""

    def test_generate_returns_list(self):
        """Test generate returns a list."""
        generator = TestCaseGenerator()
        requirements = "ユーザー登録機能"
        cases = generator.generate(requirements)

        assert isinstance(cases, list)

    def test_generate_returns_test_case_objects(self):
        """Test generated cases are TestCase instances."""
        generator = TestCaseGenerator()
        requirements = "ユーザー登録機能"
        cases = generator.generate(requirements)

        for case in cases:
            assert isinstance(case, TestCase)

    def test_generate_default_cases(self):
        """Test that default test cases are generated."""
        generator = TestCaseGenerator()
        requirements = "Any requirement"
        cases = generator.generate(requirements)

        # Should have at least the 4 default cases
        assert len(cases) >= 4

    def test_generate_cases_have_sequential_ids(self):
        """Test that cases have sequential IDs."""
        generator = TestCaseGenerator()
        requirements = "Test requirement"
        cases = generator.generate(requirements)

        for i, case in enumerate(cases, 1):
            assert case.id == f"TC-{i:03d}"


class TestTestCaseGeneratorNormalFlow:
    """Test normal flow test case generation."""

    def test_generates_positive_test_case(self):
        """Test that positive test case is generated."""
        generator = TestCaseGenerator()
        requirements = "User registration"
        cases = generator.generate(requirements)

        positive_cases = [c for c in cases if c.category == "正常系"]
        assert len(positive_cases) > 0

    def test_positive_case_has_correct_structure(self):
        """Test positive case has correct structure."""
        generator = TestCaseGenerator()
        requirements = "Requirement"
        cases = generator.generate(requirements)

        positive_cases = [c for c in cases if c.category == "正常系"]
        if positive_cases:
            case = positive_cases[0]
            assert case.title
            assert case.precondition
            assert len(case.steps) > 0
            assert case.expected
            assert case.priority == "高"


class TestTestCaseGeneratorErrorFlow:
    """Test error flow test case generation."""

    def test_generates_negative_test_case(self):
        """Test that negative test case is generated."""
        generator = TestCaseGenerator()
        requirements = "Error handling"
        cases = generator.generate(requirements)

        negative_cases = [c for c in cases if c.category == "異常系"]
        assert len(negative_cases) > 0

    def test_negative_case_has_correct_structure(self):
        """Test negative case has correct structure."""
        generator = TestCaseGenerator()
        requirements = "Requirement"
        cases = generator.generate(requirements)

        negative_cases = [c for c in cases if c.category == "異常系"]
        if negative_cases:
            case = negative_cases[0]
            assert case.title
            assert case.precondition
            assert len(case.steps) > 0
            assert case.expected
            assert case.priority == "高"


class TestTestCaseGeneratorBoundary:
    """Test boundary value test case generation."""

    def test_generates_boundary_test_case(self):
        """Test that boundary value test case is generated."""
        generator = TestCaseGenerator()
        requirements = "Character input"
        cases = generator.generate(requirements)

        boundary_cases = [c for c in cases if c.category == "境界値"]
        assert len(boundary_cases) > 0

    def test_boundary_case_has_correct_structure(self):
        """Test boundary case has correct structure."""
        generator = TestCaseGenerator()
        requirements = "Requirement"
        cases = generator.generate(requirements)

        boundary_cases = [c for c in cases if c.category == "境界値"]
        if boundary_cases:
            case = boundary_cases[0]
            assert case.title
            assert case.precondition
            assert len(case.steps) > 0
            assert case.expected
            assert case.priority == "中"


class TestTestCaseGeneratorRequiredField:
    """Test required field validation test case."""

    def test_generates_required_field_test_case(self):
        """Test that required field test case is generated."""
        generator = TestCaseGenerator()
        requirements = "Form with required fields"
        cases = generator.generate(requirements)

        # Should have required field test case
        assert len(cases) >= 3

    def test_required_field_case_checks_validation(self):
        """Test that required field case checks validation."""
        generator = TestCaseGenerator()
        requirements = "Form"
        cases = generator.generate(requirements)

        # Find required field case
        req_cases = [c for c in cases if "必須" in c.title]
        if req_cases:
            case = req_cases[0]
            assert case.priority == "中"


class TestTestCaseGeneratorPriority:
    """Test test case priority assignment."""

    def test_normal_case_has_high_priority(self):
        """Test that normal cases have high priority."""
        generator = TestCaseGenerator()
        requirements = "Test"
        cases = generator.generate(requirements)

        normal_cases = [c for c in cases if c.category == "正常系"]
        if normal_cases:
            assert normal_cases[0].priority == "高"

    def test_error_case_has_high_priority(self):
        """Test that error cases have high priority."""
        generator = TestCaseGenerator()
        requirements = "Test"
        cases = generator.generate(requirements)

        error_cases = [c for c in cases if c.category == "異常系"]
        if error_cases:
            assert error_cases[0].priority == "高"

    def test_boundary_case_has_medium_priority(self):
        """Test that boundary cases have medium priority."""
        generator = TestCaseGenerator()
        requirements = "Test"
        cases = generator.generate(requirements)

        boundary_cases = [c for c in cases if c.category == "境界値"]
        if boundary_cases:
            assert boundary_cases[0].priority == "中"


class TestTestCaseGeneratorWithFeature:
    """Test case generation with specific feature."""

    def test_generate_with_feature_parameter(self):
        """Test generate with feature parameter."""
        generator = TestCaseGenerator()
        requirements = "System requirements"
        feature = "Login functionality"

        cases = generator.generate(requirements, feature=feature)

        assert isinstance(cases, list)
        assert len(cases) > 0

    def test_generate_with_none_feature(self):
        """Test generate with None feature."""
        generator = TestCaseGenerator()
        requirements = "Requirements"

        cases = generator.generate(requirements, feature=None)

        assert isinstance(cases, list)


class TestTestCaseGeneratorFormatting:
    """Test markdown formatting."""

    def test_format_cases_returns_markdown(self):
        """Test format_cases returns markdown string."""
        generator = TestCaseGenerator()
        cases = [
            TestCase(
                id="TC-001",
                category="正常系",
                title="Normal test",
                precondition="Ready",
                steps=["Step 1"],
                expected="Pass",
                priority="高"
            )
        ]

        markdown = generator.format_cases(cases)

        assert isinstance(markdown, str)
        assert "テストケース一覧" in markdown

    def test_format_cases_includes_headers(self):
        """Test that formatted output includes headers."""
        generator = TestCaseGenerator()
        cases = [
            TestCase(
                id="TC-001",
                category="正常系",
                title="Test title",
                precondition="Ready",
                steps=["Step 1"],
                expected="Pass",
                priority="高"
            )
        ]

        markdown = generator.format_cases(cases)

        assert "TC-001" in markdown
        assert "Test title" in markdown

    def test_format_cases_includes_all_fields(self):
        """Test that all test case fields are in markdown."""
        generator = TestCaseGenerator()
        cases = [
            TestCase(
                id="TC-001",
                category="正常系",
                title="Test title",
                precondition="Precondition text",
                steps=["Step 1", "Step 2"],
                expected="Expected result",
                priority="高"
            )
        ]

        markdown = generator.format_cases(cases)

        assert "カテゴリ" in markdown
        assert "正常系" in markdown
        assert "優先度" in markdown
        assert "手順" in markdown
        assert "期待結果" in markdown

    def test_format_cases_empty_list(self):
        """Test formatting empty case list."""
        generator = TestCaseGenerator()
        markdown = generator.format_cases([])

        assert isinstance(markdown, str)

    def test_format_cases_multiple_cases(self):
        """Test formatting multiple cases."""
        generator = TestCaseGenerator()
        cases = [
            TestCase(
                id="TC-001",
                category="正常系",
                title="Test 1",
                precondition="Ready",
                steps=["Step"],
                expected="Pass",
                priority="高"
            ),
            TestCase(
                id="TC-002",
                category="異常系",
                title="Test 2",
                precondition="Ready",
                steps=["Step"],
                expected="Fail",
                priority="高"
            )
        ]

        markdown = generator.format_cases(cases)

        assert "TC-001" in markdown
        assert "TC-002" in markdown
        assert "Test 1" in markdown
        assert "Test 2" in markdown


class TestTestCaseGeneratorMultilingual:
    """Test multilingual support."""

    def test_generate_from_japanese_requirements(self):
        """Test generating from Japanese requirements."""
        generator = TestCaseGenerator()
        requirements = "ユーザー登録機能。入力フォームがある。エラー処理が必要。"
        cases = generator.generate(requirements)

        assert isinstance(cases, list)
        assert len(cases) > 0

    def test_generate_from_english_requirements(self):
        """Test generating from English requirements."""
        generator = TestCaseGenerator()
        requirements = "User registration with email field. Error handling required."
        cases = generator.generate(requirements)

        assert isinstance(cases, list)
        assert len(cases) > 0

    def test_generate_from_mixed_language(self):
        """Test generating from mixed language requirements."""
        generator = TestCaseGenerator()
        requirements = "ユーザー登録 with email verification. エラー処理が必要。"
        cases = generator.generate(requirements)

        assert isinstance(cases, list)


class TestTestCaseGeneratorStructure:
    """Test test case structure."""

    def test_case_id_format(self):
        """Test that case IDs follow correct format."""
        generator = TestCaseGenerator()
        requirements = "Test"
        cases = generator.generate(requirements)

        for case in cases:
            assert case.id.startswith("TC-")
            # ID format: TC-###
            assert len(case.id) == 6

    def test_case_has_steps(self):
        """Test that all cases have steps."""
        generator = TestCaseGenerator()
        requirements = "Test"
        cases = generator.generate(requirements)

        for case in cases:
            assert isinstance(case.steps, list)
            assert len(case.steps) > 0

    def test_case_precondition_is_string(self):
        """Test that precondition is a string."""
        generator = TestCaseGenerator()
        requirements = "Test"
        cases = generator.generate(requirements)

        for case in cases:
            assert isinstance(case.precondition, str)
            assert len(case.precondition) > 0

    def test_case_expected_is_string(self):
        """Test that expected result is a string."""
        generator = TestCaseGenerator()
        requirements = "Test"
        cases = generator.generate(requirements)

        for case in cases:
            assert isinstance(case.expected, str)
            assert len(case.expected) > 0


class TestTestCaseGeneratorEdgeCases:
    """Test edge cases."""

    def test_generate_empty_requirements(self):
        """Test generating from empty requirements."""
        generator = TestCaseGenerator()
        cases = generator.generate("")

        assert isinstance(cases, list)
        assert len(cases) >= 4

    def test_generate_very_long_requirements(self):
        """Test generating from very long requirements."""
        generator = TestCaseGenerator()
        requirements = "requirement " * 1000
        cases = generator.generate(requirements)

        assert isinstance(cases, list)

    def test_generate_special_characters(self):
        """Test generating with special characters."""
        generator = TestCaseGenerator()
        requirements = "Requirements <>{}[]()&*%$#@!"
        cases = generator.generate(requirements)

        assert isinstance(cases, list)
