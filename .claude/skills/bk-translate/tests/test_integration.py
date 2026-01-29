"""Integration tests for bk-translate CLI."""

import subprocess
import pytest
from pathlib import Path


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @pytest.fixture
    def scripts_dir(self):
        """Get scripts directory path."""
        return Path(__file__).parent.parent / 'scripts'

    @pytest.fixture
    def python_exe(self):
        """Get Python executable path."""
        return Path(__file__).parent.parent.parent / '.venv' / 'Scripts' / 'python.exe'

    @pytest.fixture
    def glossary_path(self):
        """Get test glossary path."""
        return Path(__file__).parent / 'fixtures' / 'sample-glossary.json'

    @pytest.fixture
    def ja_file_path(self):
        """Get Japanese test file path."""
        return Path(__file__).parent / 'fixtures' / 'sample-japanese.txt'

    @pytest.fixture
    def vi_file_path(self):
        """Get Vietnamese test file path."""
        return Path(__file__).parent / 'fixtures' / 'sample-vietnamese.txt'

    def test_cli_with_japanese_text(self, python_exe, scripts_dir):
        """Test CLI with inline Japanese text."""
        result = subprocess.run(
            [str(python_exe), str(scripts_dir / 'main.py'), '--text', 'バグを修正しました'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode == 0
        assert 'Japanese↔Vietnamese translator' in result.stdout
        assert 'バグを修正しました' in result.stdout
        assert '## Glossary' in result.stdout
        assert '## Instructions:' in result.stdout

    def test_cli_with_vietnamese_text(self, python_exe, scripts_dir):
        """Test CLI with inline Vietnamese text."""
        result = subprocess.run(
            [str(python_exe), str(scripts_dir / 'main.py'), '--text', 'Đã sửa lỗi'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode == 0
        assert 'Vietnamese↔Japanese translator' in result.stdout
        assert 'Đã sửa lỗi' in result.stdout

    def test_cli_with_file(self, python_exe, scripts_dir, ja_file_path):
        """Test CLI with Japanese file input."""
        result = subprocess.run(
            [str(python_exe), str(scripts_dir / 'main.py'), '--file', str(ja_file_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode == 0
        assert '[CODE_0]' in result.stdout
        assert '[URL_0]' in result.stdout
        assert '## Preserved Elements' in result.stdout

    def test_cli_with_custom_glossary(self, python_exe, scripts_dir, glossary_path):
        """Test CLI with custom glossary."""
        result = subprocess.run(
            [
                str(python_exe),
                str(scripts_dir / 'main.py'),
                '--text', 'テストを実施しました',
                '--glossary', str(glossary_path)
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode == 0
        # Should use custom glossary, not default
        assert 'テスト → kiểm thử' in result.stdout
        assert 'バグ → lỗi' in result.stdout

    def test_cli_missing_input(self, python_exe, scripts_dir):
        """Test CLI with no input (should fail)."""
        result = subprocess.run(
            [str(python_exe), str(scripts_dir / 'main.py')],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode != 0
        assert 'Either --text or --file must be provided' in result.stderr

    def test_cli_nonexistent_file(self, python_exe, scripts_dir):
        """Test CLI with nonexistent file (should fail)."""
        result = subprocess.run(
            [str(python_exe), str(scripts_dir / 'main.py'), '--file', 'nonexistent.txt'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode != 0
        assert 'File not found' in result.stderr

    def test_cli_with_code_blocks(self, python_exe, scripts_dir):
        """Test CLI preserves code blocks."""
        text_with_code = """テスト
```python
def test():
    pass
```
コード: `npm test`"""

        result = subprocess.run(
            [str(python_exe), str(scripts_dir / 'main.py'), '--text', text_with_code],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode == 0
        assert '[CODE_0]' in result.stdout
        assert '[CODE_1]' in result.stdout
        assert '2 code block(s)' in result.stdout

    def test_cli_with_urls(self, python_exe, scripts_dir):
        """Test CLI preserves URLs."""
        text_with_urls = 'リンク: https://example.com と http://test.com'

        result = subprocess.run(
            [str(python_exe), str(scripts_dir / 'main.py'), '--text', text_with_urls],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode == 0
        assert '[URL_0]' in result.stdout
        assert '[URL_1]' in result.stdout
        assert '2 URL(s)' in result.stdout

    def test_cli_output_structure(self, python_exe, scripts_dir):
        """Test CLI output has expected structure."""
        result = subprocess.run(
            [str(python_exe), str(scripts_dir / 'main.py'), '--text', 'テスト'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=scripts_dir.parent
        )

        assert result.returncode == 0

        # Verify all required sections exist
        assert 'You are a professional' in result.stdout
        assert '## Glossary (MUST use these exact translations):' in result.stdout
        assert '## Instructions:' in result.stdout
        assert '## Text to Translate:' in result.stdout
        assert '## Output:' in result.stdout
        assert 'Provide ONLY the translated text' in result.stdout
