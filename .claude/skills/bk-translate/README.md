# bk-translate

JA↔VI translation with glossary support using Claude.

## Quick Start

```bash
# Inline text
python scripts/main.py --text "バグを修正しました" | claude -p

# From file
python scripts/main.py --file report.txt | claude -p

# Custom glossary
python scripts/main.py --text "テスト実施" --glossary glossaries/custom.json | claude -p
```

## Features

- Auto-detect language (JA/VI)
- Glossary support for consistent terminology
- Preserve code blocks and URLs
- Pipe directly to Claude

## Documentation

- **[SKILL.md](SKILL.md)** - Full documentation
- **[EXAMPLES.md](EXAMPLES.md)** - Real-world examples

## Testing

```bash
cd .claude/skills/bk-translate
../.venv/Scripts/python.exe -m pytest tests/ -v
```

**Test Coverage:** 57 tests (all passing)
- 16 tests: GlossaryManager
- 22 tests: TextProcessor
- 10 tests: Translation prompt builder
- 9 tests: CLI integration

## File Structure

```
bk-translate/
├── scripts/
│   ├── glossary_manager.py   # Glossary management
│   └── main.py                # CLI & prompt builder
├── glossaries/
│   └── default-it-terms.json  # Default IT glossary (35 terms)
├── tests/
│   ├── test_glossary_manager.py
│   ├── test_text_processor.py
│   ├── test_main.py
│   ├── test_integration.py
│   └── fixtures/
├── SKILL.md                   # Full documentation
├── EXAMPLES.md                # Usage examples
└── README.md                  # This file
```

## Dependencies

- Python 3.8+
- backlog skill (LanguageDetector)
- Built-in modules: json, re, argparse, sys, pathlib

## CLI Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--text` | Yes* | Text to translate |
| `--file` | Yes* | File path |
| `--glossary` | No | Glossary JSON (default: glossaries/default-it-terms.json) |

*One of `--text` or `--file` required

## How It Works

1. Detect language (JA or VI)
2. Load glossary terms
3. Extract code blocks → `[CODE_N]` placeholders
4. Extract URLs → `[URL_N]` placeholders
5. Build translation prompt with glossary
6. Output to stdout → pipe to `claude -p`

## Example Output

**Input:**
```bash
python scripts/main.py --text "バグを修正しました。テストを実施。"
```

**Output (prompt for Claude):**
```
You are a professional Japanese↔Vietnamese translator for IT projects.

## Glossary (MUST use these exact translations):
バグ → lỗi
テスト → kiểm thử
修正 → sửa

## Instructions:
- Translate from Japanese to Vietnamese
- Use glossary terms exactly as specified
...

## Text to Translate:
バグを修正しました。テストを実施。
```

**Claude translates to:**
```
Đã sửa lỗi. Đã thực hiện kiểm thử.
```
