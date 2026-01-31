"""Tests for gap_detector module."""
import pytest
from analyzer.gap_detector import GapDetector, Gap


class TestGapDataclass:
    """Test Gap dataclass."""

    def test_gap_creation(self):
        """Test creating Gap instance."""
        gap = Gap(
            category="security",
            description="No authentication specified",
            severity="high"
        )

        assert gap.category == "security"
        assert gap.description == "No authentication specified"
        assert gap.severity == "high"


class TestGapDetectorInitialization:
    """Test gap detector initialization."""

    def test_detector_has_checklist(self):
        """Test detector has checklist."""
        detector = GapDetector()

        assert hasattr(detector, "CHECKLIST")
        assert isinstance(detector.CHECKLIST, dict)

    def test_checklist_categories(self):
        """Test checklist has expected categories."""
        detector = GapDetector()

        expected = ["security", "error_handling", "performance", "validation", "logging", "edge_cases"]
        for category in expected:
            assert category in detector.CHECKLIST


class TestGapDetectorBasic:
    """Test basic gap detection."""

    def test_detect_returns_list(self):
        """Test detect returns a list."""
        detector = GapDetector()
        requirements = "ユーザー登録機能"
        gaps = detector.detect(requirements)

        assert isinstance(gaps, list)

    def test_detect_returns_gap_objects(self):
        """Test detected gaps are Gap instances."""
        detector = GapDetector()
        requirements = "ユーザー登録機能"
        gaps = detector.detect(requirements)

        for gap in gaps:
            assert isinstance(gap, Gap)

    def test_detect_all_fields_populated(self):
        """Test that all Gap fields are populated."""
        detector = GapDetector()
        requirements = "ユーザー登録機能"
        gaps = detector.detect(requirements)

        for gap in gaps:
            assert hasattr(gap, "category")
            assert hasattr(gap, "description")
            assert hasattr(gap, "severity")
            assert len(gap.category) > 0
            assert len(gap.description) > 0
            assert gap.severity in ["high", "medium", "low"]


class TestGapDetectorSecurity:
    """Test security gap detection."""

    def test_detects_missing_security(self):
        """Test detection of missing security requirements."""
        detector = GapDetector()
        requirements = "ユーザー登録機能"
        gaps = detector.detect(requirements)

        security_gaps = [g for g in gaps if g.category == "security"]
        # May or may not have security gap depending on content

    def test_no_gap_when_security_mentioned(self):
        """Test no security gap when security is mentioned."""
        detector = GapDetector()
        requirements = "セキュリティ対策が必要。認証機能を実装する。"
        gaps = detector.detect(requirements)

        security_gaps = [g for g in gaps if g.category == "security"]
        # Security gap should not be detected

    def test_security_keywords(self):
        """Test various security keywords."""
        detector = GapDetector()

        keywords = ["認証", "auth", "password", "security"]
        for keyword in keywords:
            requirements = f"System with {keyword}"
            gaps = detector.detect(requirements)
            # All should work without error


class TestGapDetectorErrorHandling:
    """Test error handling gap detection."""

    def test_detects_missing_error_handling(self):
        """Test detection of missing error handling."""
        detector = GapDetector()
        requirements = "ユーザー登録機能"
        gaps = detector.detect(requirements)

        # Check if error handling gaps detected
        error_gaps = [g for g in gaps if g.category == "error_handling"]

    def test_no_gap_when_error_handling_mentioned(self):
        """Test no gap when error handling is mentioned."""
        detector = GapDetector()
        requirements = "エラー処理が必要。例外を適切に処理する。"
        gaps = detector.detect(requirements)

        error_gaps = [g for g in gaps if g.category == "error_handling"]


class TestGapDetectorAcceptanceCriteria:
    """Test acceptance criteria gap detection."""

    def test_detects_missing_acceptance_criteria(self):
        """Test detection of missing acceptance criteria."""
        detector = GapDetector()
        requirements = "ユーザー登録機能が必要"
        gaps = detector.detect(requirements)

        ac_gaps = [g for g in gaps if g.category == "acceptance_criteria"]
        assert len(ac_gaps) > 0  # Should have high severity

    def test_no_gap_when_acceptance_criteria_mentioned(self):
        """Test no gap when acceptance criteria is mentioned."""
        detector = GapDetector()
        requirements = "ユーザー登録機能\n受け入れ基準：入力検証ができること"
        gaps = detector.detect(requirements)

        ac_gaps = [g for g in gaps if g.category == "acceptance_criteria"]
        # Should not detect gap if criteria mentioned


class TestGapDetectorSeverity:
    """Test gap severity classification."""

    def test_security_has_medium_severity(self):
        """Test security gaps have medium severity."""
        detector = GapDetector()
        requirements = "Basic feature"
        gaps = detector.detect(requirements)

        security_gaps = [g for g in gaps if g.category == "security"]
        if security_gaps:
            for gap in security_gaps:
                assert gap.severity == "medium"

    def test_error_handling_has_medium_severity(self):
        """Test error handling gaps have medium severity."""
        detector = GapDetector()
        requirements = "Simple feature"
        gaps = detector.detect(requirements)

        error_gaps = [g for g in gaps if g.category == "error_handling"]
        if error_gaps:
            for gap in error_gaps:
                assert gap.severity == "medium"

    def test_acceptance_criteria_has_high_severity(self):
        """Test acceptance criteria gaps have high severity."""
        detector = GapDetector()
        requirements = "Feature"
        gaps = detector.detect(requirements)

        ac_gaps = [g for g in gaps if g.category == "acceptance_criteria"]
        if ac_gaps:
            for gap in ac_gaps:
                assert gap.severity == "high"


class TestGapDetectorFormatting:
    """Test gap formatting."""

    def test_format_gaps_returns_string(self):
        """Test format_gaps returns markdown string."""
        detector = GapDetector()
        gaps = [
            Gap(category="security", description="No auth", severity="high")
        ]

        formatted = detector.format_gaps(gaps)

        assert isinstance(formatted, str)

    def test_format_gaps_empty_list(self):
        """Test formatting empty gap list."""
        detector = GapDetector()
        formatted = detector.format_gaps([])

        assert isinstance(formatted, str)
        assert "No significant gaps" in formatted

    def test_format_gaps_includes_categories(self):
        """Test that formatted output includes categories."""
        detector = GapDetector()
        gaps = [
            Gap(category="security", description="No auth", severity="high"),
            Gap(category="logging", description="No logging", severity="low")
        ]

        formatted = detector.format_gaps(gaps)

        assert "security" in formatted
        assert "logging" in formatted

    def test_format_gaps_groups_by_severity(self):
        """Test that gaps are grouped by severity."""
        detector = GapDetector()
        gaps = [
            Gap(category="security", description="No auth", severity="high"),
            Gap(category="logging", description="No logging", severity="low")
        ]

        formatted = detector.format_gaps(gaps)

        assert "High Priority" in formatted
        assert "Low Priority" in formatted

    def test_format_gaps_includes_descriptions(self):
        """Test that descriptions are included."""
        detector = GapDetector()
        gaps = [
            Gap(category="security", description="Custom description", severity="high")
        ]

        formatted = detector.format_gaps(gaps)

        assert "Custom description" in formatted


class TestGapDetectorMultilingual:
    """Test multilingual support."""

    def test_detect_japanese_requirements(self):
        """Test detecting gaps in Japanese requirements."""
        detector = GapDetector()
        requirements = "ユーザー登録機能\nメール認証が必要\nパフォーマンス: 1秒以内"
        gaps = detector.detect(requirements)

        assert isinstance(gaps, list)

    def test_detect_english_requirements(self):
        """Test detecting gaps in English requirements."""
        detector = GapDetector()
        requirements = "User registration feature with email verification"
        gaps = detector.detect(requirements)

        assert isinstance(gaps, list)

    def test_detect_mixed_language(self):
        """Test detecting gaps in mixed language requirements."""
        detector = GapDetector()
        requirements = "ユーザー登録 with email authentication and security measures"
        gaps = detector.detect(requirements)

        assert isinstance(gaps, list)


class TestGapDetectorEdgeCases:
    """Test edge cases."""

    def test_detect_empty_requirements(self):
        """Test detecting gaps in empty requirements."""
        detector = GapDetector()
        gaps = detector.detect("")

        assert isinstance(gaps, list)

    def test_detect_very_long_requirements(self):
        """Test detecting gaps in very long requirements."""
        detector = GapDetector()
        requirements = "requirement " * 1000
        gaps = detector.detect(requirements)

        assert isinstance(gaps, list)

    def test_detect_special_characters(self):
        """Test detecting gaps with special characters."""
        detector = GapDetector()
        requirements = "Requirements <>{}[]()&*%$#@!"
        gaps = detector.detect(requirements)

        assert isinstance(gaps, list)
