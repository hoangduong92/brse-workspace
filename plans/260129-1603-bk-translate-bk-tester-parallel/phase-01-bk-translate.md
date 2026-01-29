# Phase 1: bk-translate Implementation

## Overview
- **Priority:** P2
- **Status:** pending
- **Approach:** TDD
- **Directory:** `.claude/skills/bk-translate/`

## Purpose

Translate text between Japanese (JA) and Vietnamese (VI) with:
- Auto language detection
- Glossary preservation for technical terms
- Code block/URL preservation

## Architecture

```
.claude/skills/bk-translate/
├── SKILL.md
├── requirements.txt
├── .env.example
├── scripts/
│   ├── __init__.py
│   ├── main.py
│   ├── translator.py
│   └── glossary_manager.py
├── glossaries/
│   └── default-it-terms.json
└── tests/
    ├── __init__.py
    ├── test_translator.py
    ├── test_glossary_manager.py
    └── fixtures/
        ├── sample_ja_text.txt
        ├── sample_vi_text.txt
        └── expected_translations.json
```

## Implementation Steps

### 1. Setup & Fixtures (TDD)
- [ ] Create directory structure
- [ ] Create test fixtures with sample JA/VI texts
- [ ] Create default glossary (IT terms)
- [ ] Write failing tests

### 2. Glossary Manager
- [ ] `GlossaryManager` class
  - `load_glossary(path)` - Load JSON glossary
  - `add_term(ja, vi)` - Add term to glossary
  - `remove_term(ja)` - Remove term
  - `list_terms()` - List all terms
  - `lookup(term, source_lang)` - Find translation
- [ ] Default IT terms glossary

### 3. Translator
- [ ] `Translator` class
  - Use `LanguageDetector` from backlog skill
  - `translate(text)` - Auto-detect and translate
  - `translate_ja_to_vi(text)` - JA→VI
  - `translate_vi_to_ja(text)` - VI→JA
  - Preserve code blocks (``` ... ```)
  - Preserve URLs
  - Apply glossary terms

### 4. Main Entry Point
- [ ] CLI: `main.py --text "..." [--glossary path]`
- [ ] Support stdin for long text
- [ ] Output translation result

### 5. SKILL.md
- [ ] Usage documentation
- [ ] Commands: `/bk-translate`, `/bk-glossary`

## Test Cases

| Test | Input | Expected |
|------|-------|----------|
| JA→VI basic | "テストを実施しました" | "Đã thực hiện test" |
| VI→JA basic | "Đã hoàn thành chức năng" | "機能が完了しました" |
| Glossary apply | "バッチ処理を実装" (batch=xử lý batch) | Uses glossary term |
| Code preserve | "```python\ncode\n```" | Keep code unchanged |
| URL preserve | "See https://example.com" | Keep URL unchanged |
| Auto-detect JA | Japanese text | Detects JA, outputs VI |
| Auto-detect VI | Vietnamese text | Detects VI, outputs JA |

## Default Glossary (IT Terms)

```json
{
  "terms": [
    {"ja": "バッチ処理", "vi": "xử lý batch"},
    {"ja": "キュー", "vi": "queue"},
    {"ja": "インスタンス", "vi": "instance"},
    {"ja": "ルーティング", "vi": "routing"},
    {"ja": "デプロイ", "vi": "deploy"},
    {"ja": "リリース", "vi": "release"},
    {"ja": "マージ", "vi": "merge"},
    {"ja": "コミット", "vi": "commit"},
    {"ja": "プルリクエスト", "vi": "pull request"},
    {"ja": "レビュー", "vi": "review"},
    {"ja": "テスト", "vi": "test"},
    {"ja": "バグ", "vi": "bug"},
    {"ja": "障害", "vi": "lỗi/sự cố"},
    {"ja": "仕様", "vi": "spec/yêu cầu"},
    {"ja": "設計", "vi": "thiết kế"}
  ]
}
```

## Dependencies

- `LanguageDetector` from `.claude/skills/backlog/scripts/language_detector.py`
- `Language` enum from `.claude/skills/backlog/scripts/models.py`
- Google Translate API or Claude for translation (use Claude via prompt)

## Translation Strategy (claude -p)

Use `claude -p` (print mode) for fully automated translation:

```bash
# Workflow
python scripts/main.py --text "テストを実施しました" | claude -p
```

**Steps in main.py:**
1. Load glossary from JSON
2. Detect language (JA/VI)
3. Extract code blocks/URLs as placeholders
4. Build translation prompt with glossary context
5. Print prompt to stdout

**Prompt template:**
```
You are a professional JA↔VI translator for IT projects.

## Glossary (MUST use these exact translations):
{glossary_terms}

## Instructions:
- Translate from {source} to {target}
- Use glossary terms exactly as provided
- Preserve any [CODE_N] or [URL_N] placeholders unchanged
- Keep technical terms consistent

## Text to translate:
{prepared_text}

## Output:
Provide ONLY the translated text, nothing else.
```

**Post-processing (optional):**
- Restore code blocks/URLs from placeholders
- Can be done in separate script or SKILL.md instructions

## Success Criteria

- [ ] Auto-detect works correctly
- [ ] JA↔VI translation works
- [ ] Glossary terms preserved
- [ ] Code blocks unchanged
- [ ] URLs unchanged
- [ ] All tests pass
