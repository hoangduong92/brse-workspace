---
phase: 4
title: "JSON Templates"
status: pending
effort: 1.5h
---

# Phase 4: JSON Templates for Document Types

## Context Links

- Writer module: `.claude/skills/bk-write/scripts/japanese_writer.py`
- Template pattern: `.claude/skills/bk-task/templates/issue.md`
- Template loader ref: `.claude/skills/bk-task/scripts/template_loader.py`

## Overview

Create JSON templates for all 4 document types. Templates define structure and sections for each document.

## Key Insights

- JSON format allows non-developers to customize
- Each section has type (greeting, text, list, closing)
- Sections rendered in order by `japanese_writer.py`

## Requirements

### Functional
- 4 templates: email-client-ja.json, email-internal-ja.json, report-issue-ja.json, design-doc-ja.json
- Each template defines sections with labels and types
- Labels in Japanese for output

### Non-functional
- Valid JSON (parseable by `json.load`)
- UTF-8 encoding for Japanese text

## Files to Create

```
.claude/skills/bk-write/templates/
├── email-client-ja.json
├── email-internal-ja.json
├── report-issue-ja.json
└── design-doc-ja.json
```

## Implementation Steps

### 1. Create Templates Directory (5 min)

```bash
mkdir -p .claude/skills/bk-write/templates
```

### 2. Create email-client-ja.json (20 min)

```json
{
  "name": "email-client",
  "description": "Client-facing email template",
  "recommended_level": "polite",
  "sections": [
    {
      "key": "greeting",
      "type": "greeting"
    },
    {
      "key": "intro",
      "type": "text",
      "template": "{company}の{sender_name}でございます。"
    },
    {
      "key": "subject_line",
      "label": "件名",
      "type": "header"
    },
    {
      "key": "purpose",
      "label": "ご連絡事項",
      "type": "text"
    },
    {
      "key": "content_points",
      "label": "詳細",
      "type": "list"
    },
    {
      "key": "action_request",
      "label": "お願い事項",
      "type": "text"
    },
    {
      "key": "deadline",
      "label": "期限",
      "type": "text"
    },
    {
      "key": "contact",
      "label": "お問い合わせ先",
      "type": "text"
    },
    {
      "key": "closing",
      "type": "closing"
    },
    {
      "key": "signature",
      "type": "signature"
    }
  ],
  "signature_template": "\n---\n{company}\n{sender_name}\nTel: {phone}\nEmail: {email}"
}
```

### 3. Create email-internal-ja.json (15 min)

```json
{
  "name": "email-internal",
  "description": "Internal team email template",
  "recommended_level": "casual",
  "sections": [
    {
      "key": "greeting",
      "type": "greeting"
    },
    {
      "key": "subject",
      "label": "件名",
      "type": "header"
    },
    {
      "key": "content",
      "type": "text"
    },
    {
      "key": "content_points",
      "label": "要点",
      "type": "list"
    },
    {
      "key": "action_items",
      "label": "対応事項",
      "type": "list"
    },
    {
      "key": "deadline",
      "label": "期限",
      "type": "text"
    },
    {
      "key": "closing",
      "type": "closing"
    }
  ]
}
```

### 4. Create report-issue-ja.json (20 min)

```json
{
  "name": "report-issue",
  "description": "Issue/bug report template",
  "recommended_level": "polite",
  "sections": [
    {
      "key": "issue_title",
      "label": "概要",
      "type": "header"
    },
    {
      "key": "environment",
      "label": "環境",
      "type": "text"
    },
    {
      "key": "steps",
      "label": "再現手順",
      "type": "numbered_list"
    },
    {
      "key": "expected_behavior",
      "label": "期待動作",
      "type": "text"
    },
    {
      "key": "actual_behavior",
      "label": "実際の動作",
      "type": "text"
    },
    {
      "key": "screenshots",
      "label": "スクリーンショット",
      "type": "text"
    },
    {
      "key": "additional_notes",
      "label": "備考",
      "type": "text"
    },
    {
      "key": "severity",
      "label": "重大度",
      "type": "text"
    },
    {
      "key": "assignee",
      "label": "担当者",
      "type": "text"
    }
  ]
}
```

### 5. Create design-doc-ja.json (20 min)

```json
{
  "name": "design-doc",
  "description": "Design document / specification template",
  "recommended_level": "polite",
  "sections": [
    {
      "key": "feature_name",
      "label": "機能名",
      "type": "header"
    },
    {
      "key": "overview",
      "label": "概要",
      "type": "text"
    },
    {
      "key": "background",
      "label": "背景・目的",
      "type": "text"
    },
    {
      "key": "specifications",
      "label": "仕様",
      "type": "section",
      "subsections": [
        {
          "key": "functional_requirements",
          "label": "機能要件",
          "type": "list"
        },
        {
          "key": "non_functional_requirements",
          "label": "非機能要件",
          "type": "list"
        }
      ]
    },
    {
      "key": "tech_stack",
      "label": "技術構成",
      "type": "list"
    },
    {
      "key": "architecture",
      "label": "アーキテクチャ",
      "type": "text"
    },
    {
      "key": "api_design",
      "label": "API設計",
      "type": "text"
    },
    {
      "key": "database_design",
      "label": "DB設計",
      "type": "text"
    },
    {
      "key": "schedule",
      "label": "スケジュール",
      "type": "text"
    },
    {
      "key": "risks",
      "label": "リスク・課題",
      "type": "list"
    },
    {
      "key": "references",
      "label": "参考資料",
      "type": "list"
    }
  ]
}
```

### 6. Run Full Test Suite (10 min)

```bash
cd ".claude/skills/bk-write" && "../.venv/Scripts/python.exe" -m pytest tests/ -v
```

Expected: All tests pass.

## Template Section Types Reference

| Type | Description | Example Output |
|------|-------------|----------------|
| `greeting` | Keigo-appropriate greeting | いつもお世話になっております。 |
| `closing` | Keigo-appropriate closing | よろしくお願いいたします。 |
| `header` | Section header | ## 概要: ログイン機能 |
| `text` | Plain text with label | **環境:** 本番環境 |
| `list` | Bulleted list | - 項目1<br>- 項目2 |
| `numbered_list` | Numbered list | 1. 手順1<br>2. 手順2 |
| `section` | Nested section | ## 仕様<br>### 機能要件 |
| `signature` | Email signature block | ---<br>会社名<br>名前 |

## Todo List

- [ ] Create `templates/` directory
- [ ] Create `email-client-ja.json`
- [ ] Create `email-internal-ja.json`
- [ ] Create `report-issue-ja.json`
- [ ] Create `design-doc-ja.json`
- [ ] Validate all JSON files parse correctly
- [ ] Run full test suite - all pass

## Success Criteria

- All 4 template files created
- JSON valid and parseable
- Full test suite passes
- Generated documents have consistent structure

## Template Customization Guide

Users can customize templates by:
1. Adding/removing sections
2. Changing labels
3. Reordering sections
4. Adding new section types (requires code change in japanese_writer.py)

## Next Phase

Phase 5: SKILL.md & main.py integration for command-line usage.
