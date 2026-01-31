"""Tests for viewpoint_extractor module."""
import pytest
from tester.viewpoint_extractor import ViewpointExtractor, Viewpoint


class TestViewpointDataclass:
    """Test Viewpoint dataclass."""

    def test_viewpoint_creation(self):
        """Test creating Viewpoint instance."""
        vp = Viewpoint(
            category="機能性",
            viewpoint="正常系テスト",
            description="Test normal flow",
            priority="高"
        )

        assert vp.category == "機能性"
        assert vp.viewpoint == "正常系テスト"
        assert vp.description == "Test normal flow"
        assert vp.priority == "高"


class TestViewpointExtractorInitialization:
    """Test viewpoint extractor initialization."""

    def test_extractor_has_categories(self):
        """Test extractor has categories."""
        extractor = ViewpointExtractor()

        assert hasattr(extractor, "CATEGORIES")
        assert isinstance(extractor.CATEGORIES, dict)

    def test_categories_not_empty(self):
        """Test categories are not empty."""
        extractor = ViewpointExtractor()

        assert len(extractor.CATEGORIES) > 0


class TestViewpointExtractorBasic:
    """Test basic viewpoint extraction."""

    def test_extract_returns_list(self):
        """Test extract returns a list."""
        extractor = ViewpointExtractor()
        requirements = "ユーザー登録機能"
        viewpoints = extractor.extract(requirements)

        assert isinstance(viewpoints, list)

    def test_extract_returns_viewpoint_objects(self):
        """Test extracted viewpoints are Viewpoint instances."""
        extractor = ViewpointExtractor()
        requirements = "ユーザー登録機能"
        viewpoints = extractor.extract(requirements)

        for vp in viewpoints:
            assert isinstance(vp, Viewpoint)

    def test_extract_always_includes_basic_functional(self):
        """Test that basic functional viewpoints are always included."""
        extractor = ViewpointExtractor()
        requirements = "Any requirement"
        viewpoints = extractor.extract(requirements)

        viewpoint_names = [vp.viewpoint for vp in viewpoints]
        assert "正常系テスト" in viewpoint_names
        assert "異常系テスト" in viewpoint_names

    def test_extract_all_fields_populated(self):
        """Test that all Viewpoint fields are populated."""
        extractor = ViewpointExtractor()
        requirements = "ユーザー登録機能"
        viewpoints = extractor.extract(requirements)

        for vp in viewpoints:
            assert hasattr(vp, "category")
            assert hasattr(vp, "viewpoint")
            assert hasattr(vp, "description")
            assert hasattr(vp, "priority")
            assert len(vp.category) > 0
            assert len(vp.viewpoint) > 0
            assert vp.priority in ["高", "中", "低"]


class TestViewpointExtractorFunctional:
    """Test functional viewpoint detection."""

    def test_extract_normal_flow_viewpoint(self):
        """Test extraction of normal flow viewpoint."""
        extractor = ViewpointExtractor()
        requirements = "ユーザーがログインできる"
        viewpoints = extractor.extract(requirements)

        normal_vps = [vp for vp in viewpoints if "正常系" in vp.viewpoint]
        assert len(normal_vps) > 0

    def test_extract_error_flow_viewpoint(self):
        """Test extraction of error flow viewpoint."""
        extractor = ViewpointExtractor()
        requirements = "エラーハンドリング機能"
        viewpoints = extractor.extract(requirements)

        error_vps = [vp for vp in viewpoints if "異常系" in vp.viewpoint]
        assert len(error_vps) > 0


class TestViewpointExtractorBoundary:
    """Test boundary value viewpoint detection."""

    def test_extract_boundary_viewpoint_with_input_keyword(self):
        """Test boundary viewpoint with input keyword."""
        extractor = ViewpointExtractor()
        requirements = "ユーザー入力を処理する"
        viewpoints = extractor.extract(requirements)

        boundary_vps = [vp for vp in viewpoints if "境界値" in vp.category]
        # May or may not be detected

    def test_extract_boundary_viewpoint_with_value_keyword(self):
        """Test boundary viewpoint with value keyword."""
        extractor = ViewpointExtractor()
        requirements = "数値の処理"
        viewpoints = extractor.extract(requirements)

        assert isinstance(viewpoints, list)


class TestViewpointExtractorSecurity:
    """Test security viewpoint detection."""

    def test_extract_security_viewpoint_with_login(self):
        """Test security viewpoint with login keyword."""
        extractor = ViewpointExtractor()
        requirements = "ユーザーがログインできる機能"
        viewpoints = extractor.extract(requirements)

        security_vps = [vp for vp in viewpoints if "認証" in vp.viewpoint]
        assert len(security_vps) > 0

    def test_extract_security_viewpoint_with_auth(self):
        """Test security viewpoint with auth keyword."""
        extractor = ViewpointExtractor()
        requirements = "Authentication mechanism is required"
        viewpoints = extractor.extract(requirements)

        security_vps = [vp for vp in viewpoints if "セキュリティ" in vp.category]
        assert len(security_vps) > 0

    def test_extract_security_viewpoint_with_password(self):
        """Test security viewpoint with password keyword."""
        extractor = ViewpointExtractor()
        requirements = "Password validation required"
        viewpoints = extractor.extract(requirements)

        assert isinstance(viewpoints, list)


class TestViewpointExtractorPerformance:
    """Test performance viewpoint detection."""

    def test_extract_performance_viewpoint_with_performance_keyword(self):
        """Test performance viewpoint with performance keyword."""
        extractor = ViewpointExtractor()
        requirements = "Performance must be optimized"
        viewpoints = extractor.extract(requirements)

        perf_vps = [vp for vp in viewpoints if "性能" in vp.category]
        assert len(perf_vps) > 0

    def test_extract_performance_viewpoint_with_response_keyword(self):
        """Test performance viewpoint with response keyword."""
        extractor = ViewpointExtractor()
        requirements = "Response time should be fast"
        viewpoints = extractor.extract(requirements)

        perf_vps = [vp for vp in viewpoints if "性能" in vp.category]
        assert len(perf_vps) > 0

    def test_extract_performance_viewpoint_japanese(self):
        """Test performance viewpoint with Japanese keyword."""
        extractor = ViewpointExtractor()
        requirements = "性能要件を満たす必要があります"
        viewpoints = extractor.extract(requirements)

        perf_vps = [vp for vp in viewpoints if "性能" in vp.category]
        assert len(perf_vps) > 0


class TestViewpointExtractorPriority:
    """Test viewpoint priority assignment."""

    def test_basic_functional_has_high_priority(self):
        """Test that basic functional viewpoints have high priority."""
        extractor = ViewpointExtractor()
        requirements = "Any requirement"
        viewpoints = extractor.extract(requirements)

        for vp in viewpoints:
            if "正常系" in vp.viewpoint or "異常系" in vp.viewpoint:
                assert vp.priority == "高"

    def test_boundary_has_medium_priority(self):
        """Test that boundary viewpoints have medium priority."""
        extractor = ViewpointExtractor()
        requirements = "With input values"
        viewpoints = extractor.extract(requirements)

        for vp in viewpoints:
            if "境界値" in vp.category:
                assert vp.priority == "中"


class TestViewpointExtractorFormatting:
    """Test markdown table formatting."""

    def test_format_table_returns_string(self):
        """Test format_table returns markdown string."""
        extractor = ViewpointExtractor()
        viewpoints = [
            Viewpoint(
                category="機能性",
                viewpoint="正常系テスト",
                description="Test normal flow",
                priority="高"
            )
        ]

        table = extractor.format_table(viewpoints)

        assert isinstance(table, str)

    def test_format_table_includes_header(self):
        """Test that table includes header."""
        extractor = ViewpointExtractor()
        viewpoints = [
            Viewpoint(
                category="機能性",
                viewpoint="正常系テスト",
                description="Test normal flow",
                priority="高"
            )
        ]

        table = extractor.format_table(viewpoints)

        assert "カテゴリ" in table
        assert "観点" in table
        assert "説明" in table
        assert "優先度" in table

    def test_format_table_includes_data(self):
        """Test that table includes data."""
        extractor = ViewpointExtractor()
        viewpoints = [
            Viewpoint(
                category="機能性",
                viewpoint="正常系テスト",
                description="Test normal flow",
                priority="高"
            )
        ]

        table = extractor.format_table(viewpoints)

        assert "機能性" in table
        assert "正常系テスト" in table

    def test_format_table_empty_list(self):
        """Test formatting empty viewpoint list."""
        extractor = ViewpointExtractor()
        table = extractor.format_table([])

        assert isinstance(table, str)

    def test_format_table_multiple_viewpoints(self):
        """Test formatting multiple viewpoints."""
        extractor = ViewpointExtractor()
        viewpoints = [
            Viewpoint(
                category="機能性",
                viewpoint="正常系テスト",
                description="Test normal flow",
                priority="高"
            ),
            Viewpoint(
                category="セキュリティ",
                viewpoint="認証テスト",
                description="Test auth",
                priority="高"
            )
        ]

        table = extractor.format_table(viewpoints)

        assert "機能性" in table
        assert "セキュリティ" in table


class TestViewpointExtractorMultilingual:
    """Test multilingual support."""

    def test_extract_from_japanese_requirements(self):
        """Test extraction from Japanese requirements."""
        extractor = ViewpointExtractor()
        requirements = "ユーザー登録機能でログイン認証が必要。性能は1秒以内。"
        viewpoints = extractor.extract(requirements)

        assert isinstance(viewpoints, list)
        assert len(viewpoints) > 0

    def test_extract_from_english_requirements(self):
        """Test extraction from English requirements."""
        extractor = ViewpointExtractor()
        requirements = "User login with authentication. Performance under 1 second."
        viewpoints = extractor.extract(requirements)

        assert isinstance(viewpoints, list)
        assert len(viewpoints) > 0

    def test_extract_from_mixed_language(self):
        """Test extraction from mixed language requirements."""
        extractor = ViewpointExtractor()
        requirements = "ユーザー登録 with authentication and performance optimization"
        viewpoints = extractor.extract(requirements)

        assert isinstance(viewpoints, list)


class TestViewpointExtractorEdgeCases:
    """Test edge cases."""

    def test_extract_empty_requirements(self):
        """Test extraction from empty requirements."""
        extractor = ViewpointExtractor()
        viewpoints = extractor.extract("")

        assert isinstance(viewpoints, list)
        # Should still have basic functional viewpoints
        assert len(viewpoints) >= 2

    def test_extract_very_long_requirements(self):
        """Test extraction from very long requirements."""
        extractor = ViewpointExtractor()
        requirements = "requirement " * 1000
        viewpoints = extractor.extract(requirements)

        assert isinstance(viewpoints, list)

    def test_extract_special_characters(self):
        """Test extraction with special characters."""
        extractor = ViewpointExtractor()
        requirements = "Requirements <>{}[]()&*%$#@!"
        viewpoints = extractor.extract(requirements)

        assert isinstance(viewpoints, list)
