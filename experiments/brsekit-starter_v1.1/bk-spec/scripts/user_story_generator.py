"""User story generator for bk-spec."""
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserStory:
    """User story in standard format."""
    role: str
    feature: str
    benefit: str
    acceptance_criteria: List[str]
    priority: str = "medium"
    story_points: Optional[int] = None


class UserStoryGenerator:
    """Generate user stories from requirements."""

    # Templates for different languages
    TEMPLATES = {
        "ja": "【役割】として、【機能】したい、なぜなら【理由】",
        "vi": "Với vai trò {role}, tôi muốn {feature}, để {benefit}",
        "en": "As a {role}, I want {feature}, so that {benefit}"
    }

    # Common user roles
    COMMON_ROLES = {
        "ja": ["ユーザー", "管理者", "開発者", "運用者", "顧客"],
        "vi": ["người dùng", "quản trị viên", "nhà phát triển", "vận hành viên", "khách hàng"],
        "en": ["user", "admin", "developer", "operator", "customer"]
    }

    def generate(self, requirements: str, lang: str = "ja") -> List[UserStory]:
        """Generate user stories from requirements text.

        Args:
            requirements: Requirements text
            lang: Output language (ja/vi/en)

        Returns:
            List of UserStory objects
        """
        stories = []
        lines = [l.strip() for l in requirements.split("\n") if l.strip()]

        # Extract features from requirements
        features = self._extract_features(lines)

        for feature in features:
            role = self._infer_role(feature, lang)
            benefit = self._infer_benefit(feature, lang)
            criteria = self._generate_acceptance_criteria(feature, lang)
            priority = self._infer_priority(feature)

            story = UserStory(
                role=role,
                feature=feature,
                benefit=benefit,
                acceptance_criteria=criteria,
                priority=priority,
                story_points=None
            )
            stories.append(story)

        return stories

    def _extract_features(self, lines: List[str]) -> List[str]:
        """Extract features from requirement lines."""
        features = []
        for line in lines:
            # Skip headers, empty lines, and very short lines
            if line.startswith("#") or len(line) < 10:
                continue

            # Skip questions and comments
            if line.endswith("?") or line.startswith("//"):
                continue

            features.append(line)

        return features[:10]  # Limit to top 10 features

    def _infer_role(self, feature: str, lang: str) -> str:
        """Infer user role from feature description."""
        feature_lower = feature.lower()

        # Check for role keywords
        if "admin" in feature_lower or "管理" in feature:
            return self.COMMON_ROLES[lang][1]  # admin
        if "develop" in feature_lower or "開発" in feature:
            return self.COMMON_ROLES[lang][2]  # developer
        if "operator" in feature_lower or "運用" in feature:
            return self.COMMON_ROLES[lang][3]  # operator

        # Default to user
        return self.COMMON_ROLES[lang][0]

    def _infer_benefit(self, feature: str, lang: str) -> str:
        """Infer benefit from feature description."""
        benefits = {
            "ja": "業務効率を向上させるため",
            "vi": "cải thiện hiệu quả công việc",
            "en": "improve work efficiency"
        }

        # Try to extract explicit benefit
        if "ため" in feature:
            match = re.search(r"(.+?)ため", feature)
            if match:
                return match.group(1).strip()

        if "so that" in feature.lower():
            match = re.search(r"so that (.+)", feature, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        if "để" in feature:
            match = re.search(r"để (.+)", feature)
            if match:
                return match.group(1).strip()

        # Return default benefit
        return benefits.get(lang, benefits["en"])

    def _generate_acceptance_criteria(self, feature: str, lang: str) -> List[str]:
        """Generate acceptance criteria for feature."""
        criteria_templates = {
            "ja": [
                "機能が正常に動作すること",
                "エラーが適切に処理されること",
                "パフォーマンス要件を満たすこと"
            ],
            "vi": [
                "Tính năng hoạt động bình thường",
                "Lỗi được xử lý đúng cách",
                "Đáp ứng yêu cầu hiệu năng"
            ],
            "en": [
                "Feature works correctly",
                "Errors are handled properly",
                "Performance requirements are met"
            ]
        }

        return criteria_templates.get(lang, criteria_templates["en"])

    def _infer_priority(self, feature: str) -> str:
        """Infer priority from feature description."""
        feature_lower = feature.lower()

        if any(kw in feature_lower for kw in ["critical", "必須", "bắt buộc"]):
            return "high"
        if any(kw in feature_lower for kw in ["nice to have", "あれば良い", "tốt nếu có"]):
            return "low"

        return "medium"

    def format_story(self, story: UserStory, lang: str = "ja") -> str:
        """Format story in standard template.

        Japanese: [役割]として、[機能]したい、なぜなら[理由]
        English: As a [role], I want [feature], so that [benefit]
        Vietnamese: Với vai trò [role], tôi muốn [feature], để [benefit]
        """
        if lang == "ja":
            return f"{story.role}として、{story.feature}したい、なぜなら{story.benefit}"
        elif lang == "vi":
            return f"Với vai trò {story.role}, tôi muốn {story.feature}, để {story.benefit}"
        else:  # en
            return f"As a {story.role}, I want {story.feature}, so that {story.benefit}"

    def format_stories_markdown(self, stories: List[UserStory], lang: str = "ja") -> str:
        """Format all stories as markdown.

        Args:
            stories: List of UserStory objects
            lang: Output language

        Returns:
            Markdown formatted string
        """
        headers = {
            "ja": "# ユーザーストーリー",
            "vi": "# User Stories",
            "en": "# User Stories"
        }

        lines = [headers.get(lang, headers["en"]), ""]

        for i, story in enumerate(stories, 1):
            lines.append(f"## Story {i}: {story.feature[:50]}...")
            lines.append("")
            lines.append(self.format_story(story, lang))
            lines.append("")
            lines.append(f"**Priority:** {story.priority}")
            if story.story_points:
                lines.append(f"**Story Points:** {story.story_points}")
            lines.append("")

            ac_header = {
                "ja": "**受入基準:**",
                "vi": "**Tiêu chí chấp nhận:**",
                "en": "**Acceptance Criteria:**"
            }
            lines.append(ac_header.get(lang, ac_header["en"]))
            for criterion in story.acceptance_criteria:
                lines.append(f"- {criterion}")
            lines.append("")

        return "\n".join(lines)
