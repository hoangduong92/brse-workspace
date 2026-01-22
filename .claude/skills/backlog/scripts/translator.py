"""Claude-powered translation service for JA ↔ VI."""

import logging
from typing import Optional
import anthropic

try:
    from .models import Language
    from .language_detector import LanguageDetector
except ImportError:
    from models import Language
    from language_detector import LanguageDetector

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Custom exception for translation errors."""
    pass


class TranslationService:
    """AI translation service using Claude API."""

    PROMPT_TEMPLATE = """Translate the following text to {target_lang}.

IMPORTANT RULES:
1. Preserve all markdown formatting (headers, lists, code blocks, links)
2. Do NOT translate:
   - Code blocks (content inside ```)
   - Technical terms (API names, function names, variable names)
   - URLs and file paths
   - Issue IDs (e.g., HB21373-123)
3. Translate naturally, not word-by-word
4. Keep the same structure and formatting

Text to translate:
{text}

Translation:"""

    SUMMARY_PROMPT_TEMPLATE = """Translate this issue title to {target_lang}.
Keep it concise (max 100 characters).
Do NOT translate technical terms, issue IDs, or proper nouns.

Title: {text}

Translation:"""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        """Initialize translation service.

        Args:
            api_key: Anthropic API key
            model: Claude model to use (default: Haiku for speed/cost)
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.detector = LanguageDetector()

        if not api_key:
            raise ValueError("Anthropic API key is required")

    def translate(self, text: str, target: Language) -> str:
        """Translate text to target language.

        Args:
            text: Text to translate
            target: Target language

        Returns:
            Translated text, or original if same language or error
        """
        if not text or not text.strip():
            return text

        source = self.detector.detect(text)
        if source == target:
            logger.debug("Source and target language are the same, skipping translation")
            return text

        try:
            target_lang = "Japanese" if target == Language.JAPANESE else "Vietnamese"
            prompt = self.PROMPT_TEMPLATE.format(target_lang=target_lang, text=text)

            logger.info(f"Translating from {source.value} to {target.value}")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            translated = response.content[0].text.strip()
            logger.debug(f"Translation complete: {len(text)} -> {len(translated)} chars")
            return translated

        except anthropic.APIError as e:
            logger.error(f"Translation API error: {e}")
            return text  # Fallback to original
        except Exception as e:
            logger.error(f"Unexpected translation error: {e}")
            return text  # Fallback to original

    def translate_summary(self, text: str) -> str:
        """Translate issue summary/title with auto language detection.

        Args:
            text: Summary text to translate

        Returns:
            Translated summary
        """
        if not text or not text.strip():
            return text

        source = self.detector.detect(text)
        target = self.detector.get_target_language(source)

        if source == target:
            return text

        try:
            target_lang = "Japanese" if target == Language.JAPANESE else "Vietnamese"
            prompt = self.SUMMARY_PROMPT_TEMPLATE.format(target_lang=target_lang, text=text)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Summary translation error: {e}")
            return text

    def translate_description(self, text: str) -> str:
        """Translate issue description with auto language detection.

        Args:
            text: Description text to translate

        Returns:
            Translated description
        """
        if not text or not text.strip():
            return text

        source = self.detector.detect(text)
        target = self.detector.get_target_language(source)

        return self.translate(text, target)

    def translate_issue_content(
        self,
        summary: str,
        description: str
    ) -> tuple[str, str, Language, Language]:
        """Translate both summary and description.

        Args:
            summary: Issue summary
            description: Issue description

        Returns:
            Tuple of (translated_summary, translated_description, source_lang, target_lang)
        """
        source = self.detector.detect(summary or description)
        target = self.detector.get_target_language(source)

        translated_summary = self.translate(summary, target) if summary else ""
        translated_description = self.translate(description, target) if description else ""

        return translated_summary, translated_description, source, target
