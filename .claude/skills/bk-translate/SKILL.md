# bk-translate

**JA↔VI Translation with Glossary Support**

Automate JA↔VI translation using Claude with consistent terminology via glossary files.

## Features

- **Automatic language detection** (JA/VI)
- **Glossary support** for consistent IT terminology
- **Code block preservation** (inline & multi-line)
- **URL preservation** (maintains links)
- **Pipe to Claude** for instant translation

## Usage

### Basic Translation

```bash
# Inline text
python scripts/main.py --text "テストを実施しました" | claude -p

# From file
python scripts/main.py --file input.txt | claude -p
```

### With Custom Glossary

```bash
python scripts/main.py --text "バグを修正しました" --glossary glossaries/custom-terms.json | claude -p
```

## Glossary Format

Create JSON files in `glossaries/` directory:

```json
{
  "バグ": "lỗi",
  "テスト": "kiểm thử",
  "実装": "triển khai",
  "修正": "sửa",
  "確認": "xác nhận"
}
```

**Default glossary:** `glossaries/default-it-terms.json`

## Architecture

### Components

1. **GlossaryManager** (`scripts/glossary_manager.py`)
   - Load/save glossary files
   - Format terms for prompt injection
   - Add/remove terms

2. **TextProcessor** (`scripts/main.py`)
   - Extract code blocks → `[CODE_N]` placeholders
   - Extract URLs → `[URL_N]` placeholders
   - Preserve formatting

3. **LanguageDetector** (from `backlog` skill)
   - Auto-detect JA/VI
   - Determine translation direction

### Workflow

```
Input Text
    ↓
Language Detection (JA or VI)
    ↓
Extract Code Blocks & URLs → Placeholders
    ↓
Load Glossary Terms
    ↓
Build Translation Prompt
    ↓
Output to stdout → Pipe to Claude
    ↓
Translated Text (with preserved elements)
```

## Command Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--text` | Yes* | Text to translate (inline) |
| `--file` | Yes* | Path to text file |
| `--glossary` | No | Glossary JSON path (default: `glossaries/default-it-terms.json`) |

*One of `--text` or `--file` is required

## Examples

### Example 1: Bug Report Translation

```bash
# Japanese → Vietnamese
python scripts/main.py --text "バグを修正しました。テストケースを追加しました。" | claude -p

# Vietnamese → Japanese (auto-detected)
python scripts/main.py --text "Đã sửa lỗi. Đã thêm test case." | claude -p
```

### Example 2: File with Code Blocks

**input.txt:**
```
テスト結果:
`npm test`コマンドを実行しました。
全てのテストが成功しました。
```

**Command:**
```bash
python scripts/main.py --file input.txt | claude -p
```

**Output preserves:**
- `npm test` → `[CODE_0]` placeholder
- Code blocks remain unchanged in translation

### Example 3: Custom Glossary

**glossaries/project-x.json:**
```json
{
  "プロジェクトX": "Dự án X",
  "マイルストーン": "cột mốc",
  "デリバリー": "phát hành"
}
```

**Command:**
```bash
python scripts/main.py --text "プロジェクトXのマイルストーンを達成しました" --glossary glossaries/project-x.json | claude -p
```

## Integration with Claude

The script outputs a complete prompt to stdout. Pipe to `claude -p` for translation:

```bash
python scripts/main.py --text "テキスト" | claude -p
```

Claude receives:
- Glossary terms (must-use translations)
- Preserved elements list
- Source/target language instructions
- Text with placeholders

## Testing

```bash
cd ".claude/skills/bk-translate"
"../.venv/Scripts/python.exe" -m pytest tests/ -v
```

## Dependencies

- **Python 3.8+**
- **backlog skill** (for `LanguageDetector` and `Language` models)
- **Built-in modules:** `json`, `re`, `argparse`, `sys`, `pathlib`

## Error Handling

- **Missing file:** Clear error message with file path
- **Invalid JSON:** Glossary load failure warning (continues with empty glossary)
- **No input:** Error requiring `--text` or `--file`
- **Missing glossary:** Warning only (continues without glossary)

## Limitations

- Code block detection: Triple backticks and inline backticks only
- URL detection: `http://` and `https://` only
- Language detection: JA/VI only (from backlog skill)
