# Phase 03: Claude Translation Service

**Context**: Parent plan [../plan.md](plan.md)

## Overview

**Date**: 2026-01-22
**Description**: Implement AI translation service using Claude API for JA ↔ VI translation with language detection
**Priority**: P1
**Status**: pending
**Effort**: 2h

## Context Links

- Depends on: [Phase 01: Project Setup](phase-01-project-setup.md)
- Related: [Phase 04: Template System](phase-04-template-system.md)

## Key Insights

- Use Claude Haiku for fast, cost-effective translation
- Language detection via character range analysis (hiragana, katakana, kanji)
- Translate only if source ≠ target language
- Preserve formatting (markdown, code blocks)

## Requirements

### Functional
- Detect language (Japanese or Vietnamese)
- Translate summary (short text)
- Translate description (long text, may contain markdown)
- Preserve code blocks and technical terms
- Handle translation errors gracefully

### Non-Functional
- < 3s for summary translation
- < 10s for full description translation
- Fallback to original text if translation fails

## Architecture

```python
class LanguageDetector:
    def detect(text: str) -> Language  # JA or VI

class TranslationService:
    def __init__(api_key: str, model: str)
    def translate(text: str, target: Language) -> str
    def translate_summary(text: str) -> str  # Auto detect target
    def translate_description(text: str) -> str  # Auto detect target

class Language(Enum):
    JAPANESE = "ja"
    VIETNAMESE = "vi"
```

## Related Code Files

### Modify
- `.claude/skills/backlog/scripts/translator.py`

### Create
- `.claude/skills/backlog/scripts/language_detector.py`
- `.claude/skills/backlog/tests/test_translator.py`
- `.claude/skills/backlog/tests/test_language_detector.py`

### Reference
- Anthropic docs: https://docs.anthropic.com/

## Implementation Steps

1. **Create language detector** (`language_detector.py`)
   ```python
   import re

   JAPANESE_PATTERNS = [
       r'[\u3040-\u309F]',  # Hiragana
       r'[\u30A0-\u30FF]',  # Katakana
       r'[\u4E00-\u9FBF]',  # Kanji
   ]

   class LanguageDetector:
       @staticmethod
       def detect(text: str) -> Language:
           # Check for Japanese characters
           for pattern in JAPANESE_PATTERNS:
               if re.search(pattern, text):
                   return Language.JAPANESE
           return Language.VIETNAMESE
   ```

2. **Implement translation service** (`translator.py`)
   ```python
   import anthropic

   class TranslationService:
       PROMPT_TEMPLATE = """Translate the following text to {target_lang}.
       Preserve markdown formatting, code blocks, and technical terms.

       Text:
       {text}

       Translation:"""

       def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
           self.client = anthropic.Anthropic(api_key=api_key)
           self.model = model
           self.detector = LanguageDetector()

       def translate(self, text: str, target: Language) -> str:
           source = self.detector.detect(text)
           if source == target:
               return text  # No translation needed

           target_lang = "Japanese" if target == Language.JAPANESE else "Vietnamese"
           prompt = self.PROMPT_TEMPLATE.format(
               target_lang=target_lang,
               text=text
           )

           response = self.client.messages.create(
               model=self.model,
               max_tokens=4096,
               messages=[{"role": "user", "content": prompt}]
           )

           return response.content[0].text

       def translate_summary(self, text: str) -> str:
           source = self.detector.detect(text)
           target = Language.VIETNAMESE if source == Language.JAPANESE else Language.JAPANESE
           return self.translate(text, target)
   ```

3. **Add error handling**
   ```python
       def translate(self, text: str, target: Language) -> str:
           try:
               # Translation logic
           except anthropic.APIError as e:
               logging.error(f"Translation failed: {e}")
               return text  # Fallback to original
           except Exception as e:
               logging.error(f"Unexpected error: {e}")
               return text
   ```

4. **Add caching** (optional optimization)
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=100)
   def _translate_cached(self, text: str, target: Language) -> str:
       # Actual translation call
   ```

5. **Write tests**
   - Test language detection with JA/VI samples
   - Test translation preserves formatting
   - Test code blocks are not translated
   - Test error fallback behavior
   - Mock Anthropic API for unit tests

## Todo List

- [ ] Create Language enum
- [ ] Implement LanguageDetector with regex patterns
- [ ] Implement TranslationService class
- [ ] Add Anthropic client initialization
- [ ] Implement translate method with prompt
- [ ] Add error handling with fallback
- [ ] Add caching for repeated translations
- [ ] Write unit tests for detector
- [ ] Write unit tests for translator with mocks
- [ ] Test with real Claude API (use test key)

## Success Criteria

- [ ] Language detection > 95% accuracy
- [ ] Translation preserves markdown formatting
- [ ] Code blocks are not translated
- [ ] Error fallback returns original text
- [ ] All unit tests passing
- [ ] Translation time < 3s (summary), < 10s (description)

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| API quota exceeded | Medium | Use Haiku (cheaper), add caching |
| Poor translation quality | Medium | Preserve technical terms, human review option |
| Rate limits | Low | Haiku has high limits |
| Formatting loss | Low | Explicit instruction to preserve markdown |

## Security Considerations

- Never log full API responses (may contain sensitive data)
- Use environment variable for API key
- Sanitize text before logging in error cases
- Implement request timeout (30s)

## Next Steps

Proceed to [Phase 04: Template System](phase-04-template-system.md) after translation tests pass.

---

**Dependencies**: Phase 01 must be complete
**Blocks**: Phase 05 (needs translation for ticket creation)
