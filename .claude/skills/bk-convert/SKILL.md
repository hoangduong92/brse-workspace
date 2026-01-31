---
name: bk-convert
description: JA↔VI translation with glossary support. Use when translating between Japanese and Vietnamese with consistent IT terminology. Supports text, Excel, and PowerPoint files.
argument-hint: "<text> | excel <file.xlsx> --to ja|vi | pptx <file.pptx> --to ja|vi"
---

# bk-convert

**JA↔VI Translation with Glossary Support**

Translate text, Excel, and PowerPoint files between Japanese and Vietnamese while preserving formatting.

## Usage

### Text Translation (pipe to Claude)

```bash
# Inline text
/bk-convert "テストを実施しました"

# From file
/bk-convert --file input.txt

# With custom glossary
/bk-convert --text "バグを修正しました" --glossary glossaries/custom-terms.json
```

### Excel Translation (preserves formatting)

```bash
# Vietnamese to Japanese (default)
/bk-convert excel input.xlsx --to ja

# Japanese to Vietnamese
/bk-convert excel input.xlsx --to vi

# With custom glossary
/bk-convert excel input.xlsx --to ja --glossary glossaries/custom.json
```

### PowerPoint Translation (preserves formatting)

```bash
# Vietnamese to Japanese (default)
/bk-convert pptx input.pptx --to ja

# Japanese to Vietnamese
/bk-convert pptx input.pptx --to vi

# With custom glossary
/bk-convert pptx input.pptx --to ja --glossary glossaries/custom.json
```

## Features

### Text Translation
- **Auto language detection** (JA/VI)
- **Glossary support** for consistent terminology
- **Code block/URL preservation**
- **Pipe to Claude** for translation

### Excel Translation
- **100% format preservation** (colors, fonts, borders)
- **Shape/TextBox support** (5 fallback methods)
- **Table cell translation**
- **Requires:** Windows/macOS + Excel installed

### PowerPoint Translation
- **Cross-platform** (no PowerPoint needed)
- **Format preservation** (fonts, alignment, bullets)
- **Table support**
- **Text shape translation**

## Requirements

### Text Translation
No external dependencies.

### Document Translation (Excel/PPTX)
- **GEMINI_API_KEY** in `.env` file
- Install: `pip install openai python-dotenv python-pptx xlwings`

### Platform Requirements
| Format | Platform | Requirements |
|--------|----------|--------------|
| Text | Any | None |
| Excel | Windows/macOS | Excel installed |
| PPTX | Any | None |

## Glossary Format

Create JSON files in `glossaries/` directory:

```json
{
  "バグ": "lỗi",
  "テスト": "kiểm thử",
  "実装": "triển khai"
}
```

**Default:** `glossaries/default-it-terms.json`

## Command Arguments

### Text

| Argument | Description |
|----------|-------------|
| `--text` | Text to translate |
| `--file` | Text file path |
| `--glossary` | Glossary JSON path |

### Excel / PPTX

| Argument | Description |
|----------|-------------|
| `input` | Input file path |
| `--to` | Target: `ja` (default) or `vi` |
| `--output` | Output file path |
| `--glossary` | Glossary JSON path |

## What Gets Preserved

### Excel
- Colors, fonts, borders, column widths
- Cell merges, formulas (unchanged)
- Shapes, TextBox, WordArt, charts

### PowerPoint
- Font styles, sizes, alignment
- Bullet points, indentation
- Tables, slide layouts

## Migration

```bash
# Old
/bk-translate --text "テキスト"

# New
/bk-convert "テキスト"
/bk-convert excel input.xlsx --to ja
/bk-convert pptx input.pptx --to ja
```
