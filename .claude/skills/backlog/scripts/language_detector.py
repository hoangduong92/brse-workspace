"""Language detection for Japanese and Vietnamese text."""

import re

try:
    from .models import Language
except ImportError:
    from models import Language


# Japanese character patterns
JAPANESE_PATTERNS = [
    r'[\u3040-\u309F]',  # Hiragana
    r'[\u30A0-\u30FF]',  # Katakana
    r'[\u4E00-\u9FBF]',  # Kanji (CJK Unified Ideographs)
]

# Vietnamese diacritics (unique to Vietnamese)
VIETNAMESE_PATTERN = r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]'


class LanguageDetector:
    """Detect language of text (Japanese or Vietnamese)."""

    @staticmethod
    def detect(text: str) -> Language:
        """Detect if text is Japanese or Vietnamese.

        Detection strategy:
        1. Check for Japanese characters (hiragana, katakana, kanji)
        2. If no Japanese characters, assume Vietnamese

        Args:
            text: Input text to analyze

        Returns:
            Language enum (JAPANESE or VIETNAMESE)
        """
        if not text:
            return Language.VIETNAMESE  # Default

        text_lower = text.lower()

        # Check for Japanese characters
        for pattern in JAPANESE_PATTERNS:
            if re.search(pattern, text):
                return Language.JAPANESE

        # Check for Vietnamese diacritics (optional, for clarity)
        if re.search(VIETNAMESE_PATTERN, text_lower):
            return Language.VIETNAMESE

        # Default to Vietnamese if no Japanese characters found
        return Language.VIETNAMESE

    @staticmethod
    def get_target_language(source: Language) -> Language:
        """Get target language for translation.

        Args:
            source: Source language

        Returns:
            Target language (opposite of source)
        """
        return Language.VIETNAMESE if source == Language.JAPANESE else Language.JAPANESE
