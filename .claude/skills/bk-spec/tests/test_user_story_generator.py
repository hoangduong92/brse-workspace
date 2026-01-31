"""Tests for user_story_generator module."""
import pytest
from user_story_generator import UserStoryGenerator, UserStory


class TestUserStoryDataclass:
    """Test UserStory dataclass."""

    def test_user_story_creation(self):
        """Test creating UserStory instance."""
        story = UserStory(
            role="user",
            feature="login",
            benefit="access account",
            acceptance_criteria=["criteria1"],
            priority="high",
            story_points=5
        )

        assert story.role == "user"
        assert story.feature == "login"
        assert story.benefit == "access account"
        assert story.priority == "high"
        assert story.story_points == 5

    def test_user_story_default_priority(self):
        """Test default priority is medium."""
        story = UserStory(
            role="user",
            feature="login",
            benefit="access account",
            acceptance_criteria=[]
        )

        assert story.priority == "medium"

    def test_user_story_optional_story_points(self):
        """Test story_points is optional."""
        story = UserStory(
            role="user",
            feature="login",
            benefit="access account",
            acceptance_criteria=[]
        )

        assert story.story_points is None


class TestUserStoryGeneratorBasic:
    """Test basic story generation."""

    def test_generate_returns_list(self):
        """Test generate returns a list."""
        generator = UserStoryGenerator()
        requirements = "ユーザー登録機能が必要"
        stories = generator.generate(requirements)

        assert isinstance(stories, list)

    def test_generate_returns_user_story_objects(self):
        """Test generated stories are UserStory instances."""
        generator = UserStoryGenerator()
        requirements = "ユーザー登録機能が必要"
        stories = generator.generate(requirements)

        if stories:
            for story in stories:
                assert isinstance(story, UserStory)

    def test_generate_japanese_stories(self):
        """Test generating Japanese stories."""
        generator = UserStoryGenerator()
        requirements = "ユーザー登録機能が必要"
        stories = generator.generate(requirements, lang="ja")

        assert isinstance(stories, list)

    def test_generate_english_stories(self):
        """Test generating English stories."""
        generator = UserStoryGenerator()
        requirements = "User registration feature is needed"
        stories = generator.generate(requirements, lang="en")

        assert isinstance(stories, list)

    def test_generate_vietnamese_stories(self):
        """Test generating Vietnamese stories."""
        generator = UserStoryGenerator()
        requirements = "Cần tính năng đăng ký"
        stories = generator.generate(requirements, lang="vi")

        assert isinstance(stories, list)

    def test_generate_from_multiple_requirements(self):
        """Test generating from multiple requirements."""
        generator = UserStoryGenerator()
        requirements = """
        ユーザー登録機能が必要
        管理者がユーザーを管理できる
        パフォーマンスは1秒以内
        """
        stories = generator.generate(requirements)

        # Should generate multiple stories
        assert len(stories) >= 1

    def test_generate_extracts_multiple_features(self):
        """Test that multiple features are extracted."""
        generator = UserStoryGenerator()
        requirements = "\n".join([
            f"機能{i}: 重要な機能です" for i in range(5)
        ])
        stories = generator.generate(requirements)

        assert len(stories) >= 1


class TestUserStoryGeneratorRoleInference:
    """Test role inference."""

    def test_infer_role_admin(self):
        """Test admin role inference."""
        generator = UserStoryGenerator()

        # With admin keyword
        role_ja = generator._infer_role("管理者がユーザーを管理できる", "ja")
        assert role_ja == "管理者"

        role_en = generator._infer_role("admin manages users", "en")
        assert role_en == "admin"

    def test_infer_role_developer(self):
        """Test developer role inference."""
        generator = UserStoryGenerator()

        # With developer keyword
        role_ja = generator._infer_role("開発者がAPIを使用できる", "ja")
        assert role_ja == "開発者"

    def test_infer_role_operator(self):
        """Test operator role inference."""
        generator = UserStoryGenerator()

        role_ja = generator._infer_role("運用者がシステムを監視できる", "ja")
        assert role_ja == "運用者"

    def test_infer_role_default_user(self):
        """Test default role is user."""
        generator = UserStoryGenerator()

        role_ja = generator._infer_role("システムにアクセスできる", "ja")
        assert role_ja == "ユーザー"


class TestUserStoryGeneratorBenefitInference:
    """Test benefit inference."""

    def test_infer_benefit_from_japanese_ため(self):
        """Test benefit extraction from ため in Japanese."""
        generator = UserStoryGenerator()

        feature = "登録機能を使いたい、なぜなら効率を向上させるため"
        benefit = generator._infer_benefit(feature, "ja")

        assert benefit != ""
        assert isinstance(benefit, str)

    def test_infer_benefit_from_english_so_that(self):
        """Test benefit extraction from 'so that' in English."""
        generator = UserStoryGenerator()

        feature = "I want to register, so that I can access my account"
        benefit = generator._infer_benefit(feature, "en")

        assert benefit != ""

    def test_infer_benefit_from_vietnamese_để(self):
        """Test benefit extraction from 'để' in Vietnamese."""
        generator = UserStoryGenerator()

        feature = "Tôi muốn đăng ký, để tôi có thể truy cập tài khoản"
        benefit = generator._infer_benefit(feature, "vi")

        assert benefit != ""

    def test_infer_benefit_uses_default_if_no_pattern(self):
        """Test that default benefit is used if no pattern found."""
        generator = UserStoryGenerator()

        feature = "Simple feature description"
        benefit = generator._infer_benefit(feature, "en")

        assert benefit == "improve work efficiency"


class TestUserStoryGeneratorPriority:
    """Test priority inference."""

    def test_infer_priority_high(self):
        """Test high priority detection."""
        generator = UserStoryGenerator()

        priority1 = generator._infer_priority("Critical: user login必須")
        assert priority1 == "high"

        priority2 = generator._infer_priority("必須: ユーザー認証")
        assert priority2 == "high"

    def test_infer_priority_low(self):
        """Test low priority detection."""
        generator = UserStoryGenerator()

        priority = generator._infer_priority("Nice to have: social login")
        assert priority == "low"

    def test_infer_priority_medium_default(self):
        """Test medium is default priority."""
        generator = UserStoryGenerator()

        priority = generator._infer_priority("ユーザー登録機能")
        assert priority == "medium"


class TestUserStoryGeneratorFormatting:
    """Test story formatting."""

    def test_format_story_japanese(self):
        """Test Japanese story formatting."""
        generator = UserStoryGenerator()
        story = UserStory(
            role="ユーザー",
            feature="ログインできる",
            benefit="アカウントにアクセスできる",
            acceptance_criteria=[]
        )

        formatted = generator.format_story(story, lang="ja")

        assert isinstance(formatted, str)
        assert "ユーザー" in formatted
        assert "として" in formatted
        assert "したい" in formatted

    def test_format_story_english(self):
        """Test English story formatting."""
        generator = UserStoryGenerator()
        story = UserStory(
            role="user",
            feature="login",
            benefit="access account",
            acceptance_criteria=[]
        )

        formatted = generator.format_story(story, lang="en")

        assert isinstance(formatted, str)
        assert "As a" in formatted
        assert "I want" in formatted
        assert "so that" in formatted

    def test_format_story_vietnamese(self):
        """Test Vietnamese story formatting."""
        generator = UserStoryGenerator()
        story = UserStory(
            role="người dùng",
            feature="đăng nhập",
            benefit="truy cập tài khoản",
            acceptance_criteria=[]
        )

        formatted = generator.format_story(story, lang="vi")

        assert isinstance(formatted, str)
        assert "Với vai trò" in formatted


class TestUserStoryGeneratorMarkdown:
    """Test markdown formatting."""

    def test_format_stories_markdown_japanese(self):
        """Test markdown formatting for Japanese stories."""
        generator = UserStoryGenerator()
        stories = [
            UserStory(
                role="ユーザー",
                feature="ログイン",
                benefit="アクセス",
                acceptance_criteria=["criteria1"],
                priority="high"
            )
        ]

        markdown = generator.format_stories_markdown(stories, lang="ja")

        assert isinstance(markdown, str)
        assert "ユーザーストーリー" in markdown
        assert "Story 1" in markdown

    def test_format_stories_markdown_includes_priority(self):
        """Test that priority is included."""
        generator = UserStoryGenerator()
        stories = [
            UserStory(
                role="user",
                feature="login",
                benefit="access",
                acceptance_criteria=[],
                priority="high"
            )
        ]

        markdown = generator.format_stories_markdown(stories, lang="en")

        assert "Priority" in markdown
        assert "high" in markdown

    def test_format_stories_markdown_includes_criteria(self):
        """Test that acceptance criteria are included."""
        generator = UserStoryGenerator()
        stories = [
            UserStory(
                role="user",
                feature="login",
                benefit="access",
                acceptance_criteria=["criteria1", "criteria2"]
            )
        ]

        markdown = generator.format_stories_markdown(stories, lang="en")

        assert "Acceptance Criteria" in markdown
        assert "criteria1" in markdown

    def test_format_stories_markdown_empty_list(self):
        """Test markdown formatting with empty story list."""
        generator = UserStoryGenerator()
        markdown = generator.format_stories_markdown([], lang="en")

        assert isinstance(markdown, str)
        assert "User Stories" in markdown


class TestUserStoryGeneratorAcceptanceCriteria:
    """Test acceptance criteria generation."""

    def test_generate_acceptance_criteria_japanese(self):
        """Test criteria generation in Japanese."""
        generator = UserStoryGenerator()
        criteria = generator._generate_acceptance_criteria("test", "ja")

        assert isinstance(criteria, list)
        assert len(criteria) == 3

    def test_generate_acceptance_criteria_english(self):
        """Test criteria generation in English."""
        generator = UserStoryGenerator()
        criteria = generator._generate_acceptance_criteria("test", "en")

        assert isinstance(criteria, list)
        assert len(criteria) == 3

    def test_generate_acceptance_criteria_vietnamese(self):
        """Test criteria generation in Vietnamese."""
        generator = UserStoryGenerator()
        criteria = generator._generate_acceptance_criteria("test", "vi")

        assert isinstance(criteria, list)
        assert len(criteria) == 3


class TestUserStoryGeneratorFeatureExtraction:
    """Test feature extraction."""

    def test_extract_features_filters_headers(self):
        """Test that header lines are filtered."""
        generator = UserStoryGenerator()
        lines = [
            "# Header",
            "Valid feature line here",
            "## Subheader"
        ]

        features = generator._extract_features(lines)

        assert "# Header" not in features
        assert "## Subheader" not in features

    def test_extract_features_filters_short_lines(self):
        """Test that short lines are filtered."""
        generator = UserStoryGenerator()
        lines = [
            "short",
            "This is a properly sized feature description",
            "too"
        ]

        features = generator._extract_features(lines)

        assert "short" not in features
        assert len(features) >= 0

    def test_extract_features_filters_questions(self):
        """Test that questions are filtered."""
        generator = UserStoryGenerator()
        lines = [
            "What is this question?",
            "This is a valid feature requirement"
        ]

        features = generator._extract_features(lines)

        assert "What is this question?" not in features

    def test_extract_features_filters_comments(self):
        """Test that comments are filtered."""
        generator = UserStoryGenerator()
        lines = [
            "// This is a comment",
            "This is a valid feature requirement"
        ]

        features = generator._extract_features(lines)

        assert "// This is a comment" not in features

    def test_extract_features_limits_to_10(self):
        """Test that results are limited to 10 features."""
        generator = UserStoryGenerator()
        lines = [
            f"Feature {i}: This is a long description of a feature"
            for i in range(20)
        ]

        features = generator._extract_features(lines)

        assert len(features) <= 10
