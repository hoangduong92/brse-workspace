"""Tests for TextProcessor."""

import pytest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from main import TextProcessor


class TestTextProcessor:
    """Test cases for TextProcessor."""

    def test_init(self):
        """Test initialization."""
        processor = TextProcessor()
        assert processor.code_blocks == []
        assert processor.urls == []

    def test_extract_code_blocks_none(self):
        """Test text with no code blocks."""
        processor = TextProcessor()
        text = "This is plain text with no code."

        result = processor.extract_code_blocks(text)

        assert result == text
        assert processor.code_blocks == []

    def test_extract_code_blocks_triple_backtick(self):
        """Test extracting triple-backtick code blocks."""
        processor = TextProcessor()
        text = """Text before
```python
def hello():
    print("Hello")
```
Text after"""

        result = processor.extract_code_blocks(text)

        assert "[CODE_0]" in result
        assert "```python" not in result
        assert len(processor.code_blocks) == 1
        assert "```python" in processor.code_blocks[0]

    def test_extract_code_blocks_multiple_triple_backtick(self):
        """Test extracting multiple code blocks."""
        processor = TextProcessor()
        text = """First:
```js
const x = 1;
```
Second:
```py
y = 2
```"""

        result = processor.extract_code_blocks(text)

        assert "[CODE_0]" in result
        assert "[CODE_1]" in result
        assert len(processor.code_blocks) == 2

    def test_extract_code_blocks_inline(self):
        """Test extracting inline code."""
        processor = TextProcessor()
        text = "Run `npm test` to test."

        result = processor.extract_code_blocks(text)

        assert "[CODE_0]" in result
        assert "`npm test`" not in result
        assert len(processor.code_blocks) == 1
        assert processor.code_blocks[0] == "`npm test`"

    def test_extract_code_blocks_mixed(self):
        """Test extracting both triple-backtick and inline code."""
        processor = TextProcessor()
        text = """Use `npm install` first.
```bash
npm test
```
Then run `npm start`."""

        result = processor.extract_code_blocks(text)

        # Triple backtick processed first, then inline
        assert "[CODE_0]" in result  # ```bash block
        assert "[CODE_1]" in result  # `npm install`
        assert "[CODE_2]" in result  # `npm start`
        assert len(processor.code_blocks) == 3

    def test_extract_urls_none(self):
        """Test text with no URLs."""
        processor = TextProcessor()
        text = "This is plain text."

        result = processor.extract_urls(text)

        assert result == text
        assert processor.urls == []

    def test_extract_urls_single_http(self):
        """Test extracting single HTTP URL."""
        processor = TextProcessor()
        text = "Visit http://example.com for info."

        result = processor.extract_urls(text)

        assert "[URL_0]" in result
        assert "http://example.com" not in result
        assert len(processor.urls) == 1
        assert processor.urls[0] == "http://example.com"

    def test_extract_urls_single_https(self):
        """Test extracting single HTTPS URL."""
        processor = TextProcessor()
        text = "Visit https://example.com for info."

        result = processor.extract_urls(text)

        assert "[URL_0]" in result
        assert len(processor.urls) == 1
        assert processor.urls[0] == "https://example.com"

    def test_extract_urls_multiple(self):
        """Test extracting multiple URLs."""
        processor = TextProcessor()
        text = "See https://docs.example.com and http://api.example.com"

        result = processor.extract_urls(text)

        assert "[URL_0]" in result
        assert "[URL_1]" in result
        assert len(processor.urls) == 2

    def test_extract_urls_with_path(self):
        """Test extracting URLs with paths."""
        processor = TextProcessor()
        text = "See https://example.com/docs/api/guide for details."

        result = processor.extract_urls(text)

        assert "[URL_0]" in result
        assert len(processor.urls) == 1
        assert processor.urls[0] == "https://example.com/docs/api/guide"

    def test_extract_urls_with_query(self):
        """Test extracting URLs with query parameters."""
        processor = TextProcessor()
        text = "Link: https://example.com/search?q=test&lang=ja"

        result = processor.extract_urls(text)

        assert "[URL_0]" in result
        assert processor.urls[0] == "https://example.com/search?q=test&lang=ja"

    def test_process_clean_text(self):
        """Test processing text with no special elements."""
        processor = TextProcessor()
        text = "Plain text with no code or URLs."

        result = processor.process(text)

        assert result == text
        assert processor.code_blocks == []
        assert processor.urls == []

    def test_process_with_code_and_urls(self):
        """Test processing text with both code and URLs."""
        processor = TextProcessor()
        text = """Visit https://example.com
Run `npm test`
```bash
npm install
```
See http://docs.example.com"""

        result = processor.process(text)

        assert "[CODE_0]" in result  # ```bash block
        assert "[CODE_1]" in result  # `npm test`
        assert "[URL_0]" in result   # https://example.com
        assert "[URL_1]" in result   # http://docs.example.com

        assert len(processor.code_blocks) == 2
        assert len(processor.urls) == 2

    def test_process_resets_state(self):
        """Test that process resets previous state."""
        processor = TextProcessor()

        # First process
        processor.process("Visit https://example.com")
        assert len(processor.urls) == 1

        # Second process should reset
        processor.process("Plain text")
        assert processor.urls == []
        assert processor.code_blocks == []

    def test_get_preservation_note_empty(self):
        """Test preservation note with no elements."""
        processor = TextProcessor()
        processor.process("Plain text")

        note = processor.get_preservation_note()

        assert note == ""

    def test_get_preservation_note_code_only(self):
        """Test preservation note with code blocks only."""
        processor = TextProcessor()
        processor.process("Run `npm test` and `npm start`")

        note = processor.get_preservation_note()

        assert "## Preserved Elements" in note
        assert "[CODE_0]" in note
        assert "[CODE_1]" in note
        assert "URL" not in note

    def test_get_preservation_note_urls_only(self):
        """Test preservation note with URLs only."""
        processor = TextProcessor()
        processor.process("Visit https://example.com and http://test.com")

        note = processor.get_preservation_note()

        assert "## Preserved Elements" in note
        assert "[URL_0]" in note
        assert "[URL_1]" in note
        assert "CODE" not in note

    def test_get_preservation_note_both(self):
        """Test preservation note with both code and URLs."""
        processor = TextProcessor()
        processor.process("`code` and https://example.com")

        note = processor.get_preservation_note()

        assert "## Preserved Elements" in note
        assert "[CODE_0]" in note
        assert "[URL_0]" in note

    def test_extract_code_blocks_language_specified(self):
        """Test extracting code blocks with language specifier."""
        processor = TextProcessor()
        text = """```javascript
const x = 1;
```"""

        result = processor.extract_code_blocks(text)

        assert "[CODE_0]" in result
        assert "```javascript" in processor.code_blocks[0]

    def test_extract_urls_in_parentheses(self):
        """Test URL extraction with trailing parenthesis."""
        processor = TextProcessor()
        text = "See (https://example.com) for details."

        result = processor.extract_urls(text)

        # Should not include the closing parenthesis
        assert processor.urls[0] == "https://example.com"
        assert result == "See ([URL_0]) for details."

    def test_complex_real_world_example(self):
        """Test complex real-world scenario."""
        processor = TextProcessor()
        text = """バグを修正しました。

詳細: https://github.com/user/repo/issues/123

変更内容:
```typescript
function fixBug() {
  // Fixed the issue
  return true;
}
```

テストコマンド: `npm test`

参考: https://docs.example.com/guide
"""

        result = processor.process(text)

        assert "[URL_0]" in result  # GitHub URL
        assert "[URL_1]" in result  # docs URL
        assert "[CODE_0]" in result  # TypeScript block
        assert "[CODE_1]" in result  # npm test

        assert len(processor.urls) == 2
        assert len(processor.code_blocks) == 2

        note = processor.get_preservation_note()
        assert "2 code block(s)" in note
        assert "2 URL(s)" in note
