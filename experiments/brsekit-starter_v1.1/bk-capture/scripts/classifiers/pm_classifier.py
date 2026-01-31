"""PM classifier for bk-capture - classify items as Task/Issue/Risk/Question."""
from enum import Enum
from typing import Tuple
import re


class ItemType(Enum):
    TASK = "task"
    ISSUE = "issue"
    RISK = "risk"
    QUESTION = "question"
    DECISION = "decision"


class PMClassifier:
    """Classify captured items by PM category."""

    # Keywords by type and language
    KEYWORDS = {
        ItemType.TASK: {
            "ja": ["実装", "対応", "作成", "確認", "修正", "追加", "削除", "更新", "調査"],
            "en": ["implement", "create", "fix", "add", "update", "check", "review", "build"],
            "vi": ["thực hiện", "tạo", "sửa", "thêm", "cập nhật", "kiểm tra"]
        },
        ItemType.ISSUE: {
            "ja": ["問題", "バグ", "エラー", "障害", "不具合", "課題"],
            "en": ["bug", "error", "issue", "problem", "failure", "defect"],
            "vi": ["lỗi", "vấn đề", "sự cố"]
        },
        ItemType.RISK: {
            "ja": ["リスク", "懸念", "心配", "遅延", "影響"],
            "en": ["risk", "concern", "delay", "impact", "blocker"],
            "vi": ["rủi ro", "lo ngại", "trì hoãn"]
        },
        ItemType.QUESTION: {
            "ja": ["質問", "確認", "どう", "なぜ", "何"],
            "en": ["question", "how", "why", "what", "clarify", "confirm"],
            "vi": ["hỏi", "tại sao", "như thế nào"]
        },
        ItemType.DECISION: {
            "ja": ["決定", "判断", "選択", "承認"],
            "en": ["decided", "decision", "approved", "agreed", "selected"],
            "vi": ["quyết định", "phê duyệt", "đồng ý"]
        }
    }

    def classify(self, text: str) -> Tuple[ItemType, float]:
        """Classify text into PM category.

        Args:
            text: Input text to classify

        Returns:
            Tuple of (ItemType, confidence_score)
        """
        text_lower = text.lower()
        scores = {item_type: 0 for item_type in ItemType}

        # Score based on keyword matches
        for item_type, lang_keywords in self.KEYWORDS.items():
            for lang, keywords in lang_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        scores[item_type] += 1

        # Question mark detection
        if "?" in text or "？" in text:
            scores[ItemType.QUESTION] += 2

        # Find best match
        best_type = max(scores, key=scores.get)
        max_score = scores[best_type]

        # Calculate confidence
        total_keywords = sum(scores.values())
        if total_keywords == 0:
            return ItemType.TASK, 0.5  # Default to task

        confidence = min(1.0, max_score / 3)  # Normalize to 0-1

        return best_type, confidence

    def classify_batch(self, texts: list) -> list:
        """Classify multiple texts.

        Args:
            texts: List of texts to classify

        Returns:
            List of (ItemType, confidence) tuples
        """
        return [self.classify(text) for text in texts]
