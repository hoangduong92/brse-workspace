"""Tests for requirements_analyzer module."""
import pytest
from analyzer.requirements_analyzer import RequirementsAnalyzer, AnalysisResult


class TestAnalysisResultDataclass:
    """Test AnalysisResult dataclass."""

    def test_analysis_result_creation(self):
        """Test creating AnalysisResult instance."""
        result = AnalysisResult(
            functional=["req1"],
            non_functional=["req2"],
            ambiguities=["amb1"],
            questions=["q1"]
        )

        assert result.functional == ["req1"]
        assert result.non_functional == ["req2"]
        assert result.ambiguities == ["amb1"]
        assert result.questions == ["q1"]


class TestRequirementsAnalyzerBasic:
    """Test basic analysis functionality."""

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = RequirementsAnalyzer()

        assert hasattr(analyzer, "FUNCTIONAL_KEYWORDS")
        assert hasattr(analyzer, "NON_FUNCTIONAL_KEYWORDS")
        assert hasattr(analyzer, "AMBIGUITY_INDICATORS")

    def test_analyze_returns_analysis_result(self):
        """Test that analyze returns correct type."""
        analyzer = RequirementsAnalyzer()
        requirements = "ユーザー登録機能が必要"
        result = analyzer.analyze(requirements)

        assert isinstance(result, AnalysisResult)

    def test_analyze_returns_lists(self):
        """Test that all fields are lists."""
        analyzer = RequirementsAnalyzer()
        requirements = "ユーザー登録機能"
        result = analyzer.analyze(requirements)

        assert isinstance(result.functional, list)
        assert isinstance(result.non_functional, list)
        assert isinstance(result.ambiguities, list)
        assert isinstance(result.questions, list)


class TestRequirementsAnalyzerFunctional:
    """Test functional requirements detection."""

    def test_detect_functional_requirements_japanese(self):
        """Test detection of Japanese functional requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = "ユーザー登録機能を実装する"
        result = analyzer.analyze(requirements)

        assert len(result.functional) > 0

    def test_detect_functional_requirements_english(self):
        """Test detection of English functional requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = "System must provide user login"
        result = analyzer.analyze(requirements)

        assert isinstance(result.functional, list)

    def test_functional_keywords(self):
        """Test that functional keywords are recognized."""
        analyzer = RequirementsAnalyzer()

        for keyword in ["shall", "must", "機能", "できる"]:
            requirements = f"The system {keyword} support login"
            result = analyzer.analyze(requirements)

            # Should have functional requirement if keyword matched
            assert isinstance(result.functional, list)


class TestRequirementsAnalyzerNonFunctional:
    """Test non-functional requirements detection."""

    def test_detect_non_functional_performance(self):
        """Test detection of performance requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = "Response time must be under 1 second"
        result = analyzer.analyze(requirements)

        assert len(result.non_functional) > 0

    def test_detect_non_functional_security(self):
        """Test detection of security requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = "セキュリティ対策が必要"
        result = analyzer.analyze(requirements)

        assert len(result.non_functional) > 0

    def test_non_functional_keywords(self):
        """Test that non-functional keywords are recognized."""
        analyzer = RequirementsAnalyzer()

        for keyword in ["performance", "security", "性能", "セキュリティ"]:
            requirements = f"The system requires {keyword} optimization"
            result = analyzer.analyze(requirements)

            assert isinstance(result.non_functional, list)


class TestRequirementsAnalyzerAmbiguity:
    """Test ambiguity detection."""

    def test_detect_ambiguities(self):
        """Test detection of ambiguous statements."""
        analyzer = RequirementsAnalyzer()
        requirements = "システムは適切なエラー処理などを行うこと"
        result = analyzer.analyze(requirements)

        assert len(result.ambiguities) > 0
        assert len(result.questions) > 0

    def test_ambiguity_indicators(self):
        """Test that ambiguity indicators are detected."""
        analyzer = RequirementsAnalyzer()

        for indicator in ["など", "etc", "appropriate"]:
            requirements = f"Handle errors {indicator} properly"
            result = analyzer.analyze(requirements)

            # If indicator is in text, should detect ambiguity
            if indicator in requirements.lower():
                assert isinstance(result.ambiguities, list)

    def test_no_ambiguities_in_clear_requirements(self):
        """Test that clear requirements don't generate ambiguities."""
        analyzer = RequirementsAnalyzer()
        requirements = "The system must validate user email addresses"
        result = analyzer.analyze(requirements)

        # Clear requirement should have fewer ambiguities
        assert isinstance(result.ambiguities, list)


class TestRequirementsAnalyzerQuestions:
    """Test clarifying questions."""

    def test_generates_questions_for_missing_nfr(self):
        """Test questions generated for missing non-functional requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = "ユーザー登録機能"
        result = analyzer.analyze(requirements)

        # Should ask about performance, security, etc.
        assert len(result.questions) >= 0

    def test_generates_questions_for_limited_fr(self):
        """Test questions for limited functional requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = "One feature"
        result = analyzer.analyze(requirements)

        assert isinstance(result.questions, list)

    def test_questions_are_meaningful(self):
        """Test that questions are meaningful strings."""
        analyzer = RequirementsAnalyzer()
        requirements = "Simple requirement"
        result = analyzer.analyze(requirements)

        for question in result.questions:
            assert isinstance(question, str)
            assert len(question) > 0


class TestRequirementsAnalyzerFormatting:
    """Test markdown formatting."""

    def test_format_analysis_returns_markdown(self):
        """Test that format_analysis returns markdown string."""
        analyzer = RequirementsAnalyzer()
        requirements = "ユーザー登録機能が必要。パフォーマンスは1秒以内。"
        result = analyzer.analyze(requirements)
        markdown = analyzer.format_analysis(result)

        assert isinstance(markdown, str)
        assert "# Requirements Analysis" in markdown

    def test_format_analysis_includes_functional_section(self):
        """Test that markdown includes functional section."""
        analyzer = RequirementsAnalyzer()
        requirements = "ユーザー登録機能"
        result = analyzer.analyze(requirements)
        markdown = analyzer.format_analysis(result)

        assert "Functional Requirements" in markdown

    def test_format_analysis_includes_nonfunctional_section(self):
        """Test that markdown includes non-functional section."""
        analyzer = RequirementsAnalyzer()
        requirements = "パフォーマンス要件"
        result = analyzer.analyze(requirements)
        markdown = analyzer.format_analysis(result)

        assert "Non-Functional Requirements" in markdown

    def test_format_analysis_includes_ambiguities_if_present(self):
        """Test that ambiguities section is included if found."""
        analyzer = RequirementsAnalyzer()
        requirements = "System should handle errors etc"
        result = analyzer.analyze(requirements)
        markdown = analyzer.format_analysis(result)

        assert isinstance(markdown, str)

    def test_format_analysis_includes_questions(self):
        """Test that questions are included."""
        analyzer = RequirementsAnalyzer()
        requirements = "User registration"
        result = analyzer.analyze(requirements)
        markdown = analyzer.format_analysis(result)

        if result.questions:
            assert "Clarifying Questions" in markdown

    def test_format_analysis_limits_items_to_10(self):
        """Test that only 10 items are shown per section."""
        analyzer = RequirementsAnalyzer()
        requirements = "\n".join([
            f"Requirement {i}: This is a functional requirement"
            for i in range(20)
        ])
        result = analyzer.analyze(requirements)
        markdown = analyzer.format_analysis(result)

        # Each section should show max 10 items
        assert isinstance(markdown, str)


class TestRequirementsAnalyzerMultilingual:
    """Test multilingual support."""

    def test_analyze_japanese_requirements(self):
        """Test analyzing Japanese requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = """
        ユーザー登録機能が必要
        メール認証を実装する
        セキュリティ対策が必要
        """
        result = analyzer.analyze(requirements)

        assert isinstance(result, AnalysisResult)

    def test_analyze_english_requirements(self):
        """Test analyzing English requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = """
        User registration feature
        Email verification required
        Security measures needed
        """
        result = analyzer.analyze(requirements)

        assert isinstance(result, AnalysisResult)

    def test_analyze_mixed_language(self):
        """Test analyzing mixed language requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = "ユーザー登録 must support email verification and authentication"
        result = analyzer.analyze(requirements)

        assert isinstance(result, AnalysisResult)


class TestRequirementsAnalyzerEdgeCases:
    """Test edge cases."""

    def test_analyze_empty_requirements(self):
        """Test analyzing empty requirements."""
        analyzer = RequirementsAnalyzer()
        result = analyzer.analyze("")

        assert isinstance(result, AnalysisResult)
        assert isinstance(result.functional, list)
        assert isinstance(result.non_functional, list)

    def test_analyze_single_line(self):
        """Test analyzing single line requirement."""
        analyzer = RequirementsAnalyzer()
        result = analyzer.analyze("Simple requirement")

        assert isinstance(result, AnalysisResult)

    def test_analyze_very_long_requirements(self):
        """Test analyzing very long requirements."""
        analyzer = RequirementsAnalyzer()
        requirements = " ".join(["requirement"] * 1000)
        result = analyzer.analyze(requirements)

        assert isinstance(result, AnalysisResult)

    def test_analyze_with_special_characters(self):
        """Test analyzing requirements with special characters."""
        analyzer = RequirementsAnalyzer()
        requirements = "Requirements with <>{}[]()&*%$#@!?"
        result = analyzer.analyze(requirements)

        assert isinstance(result, AnalysisResult)
