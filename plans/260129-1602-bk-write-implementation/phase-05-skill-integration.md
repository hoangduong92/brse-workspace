---
phase: 5
title: "Skill Integration"
status: pending
effort: 1.5h
---

# Phase 5: SKILL.md & main.py Integration

## Context Links

- SKILL.md pattern: `.claude/skills/bk-task/SKILL.md`
- SKILL.md pattern: `.claude/skills/bk-status/SKILL.md`
- main.py pattern: `.claude/skills/bk-task/scripts/main.py`

## Overview

Create skill definition file (SKILL.md), entry point (main.py), and supporting files for command-line integration.

## Files to Create

```
.claude/skills/bk-write/
├── SKILL.md              # Skill definition
├── .env.example          # Environment template (optional)
└── requirements.txt      # Dependencies
```

## Implementation Steps

### 1. Create SKILL.md (40 min)

**File:** `.claude/skills/bk-write/SKILL.md`

```markdown
---
name: bk-write
description: Generate consistent Japanese business documents with proper keigo levels. Supports emails, issue reports, and design docs.
license: MIT
allowed-tools:
  - Bash
  - Read
  - Write
---

# bk-write - Japanese Business Writing

Generate template-based Japanese business documents with consistent keigo (formality) levels.

## Pain Point Solved

> "4 nguoi lam file thiet ke, cach hanh van tieng Nhat khac nhau"
> (4 people writing design files, different Japanese writing styles)

## Setup

```bash
# No additional setup required - uses shared venv
# Optionally verify installation:
cd ".claude/skills" && ".venv/Scripts/pip.exe" show pyyaml
```

## Usage

```
/bk-write [doc-type] [--level LEVEL]
```

**Document Types:**
- `email-client` - Client-facing email
- `email-internal` - Internal team email
- `report-issue` - Bug/issue report
- `design-doc` - Design specification

**Keigo Levels:**
- `casual` - Internal, familiar colleagues (カジュアル)
- `polite` - Standard business (丁寧) [default]
- `honorific` - Client-facing, executives (敬語)

**Examples:**
```
/bk-write email-client --level=polite
/bk-write email-internal --level=casual
/bk-write report-issue
/bk-write design-doc --level=polite
```

## Workflow Instructions (for Claude Code)

### Step 1: Gather Input

Prompt user for document details based on type:

**For email-client:**
- recipient: 宛先 (e.g., 田中様)
- subject: 件名
- content_points: 内容ポイント (list)
- action_request: お願い事項 (optional)

**For email-internal:**
- recipient: 宛先 (e.g., 佐藤さん)
- subject: 件名
- content_points: 要点 (list)
- action_items: 対応事項 (optional)

**For report-issue:**
- issue_title: 概要
- environment: 環境 (e.g., 本番, ステージング)
- steps: 再現手順 (list)
- expected_behavior: 期待動作
- actual_behavior: 実際の動作

**For design-doc:**
- feature_name: 機能名
- overview: 概要
- specifications: 仕様 (list)
- tech_stack: 技術構成 (list)
- schedule: スケジュール

### Step 2: Generate Document

```bash
# Run generator script
cd ".claude/skills/bk-write" && "../.venv/Scripts/python.exe" scripts/main.py \
  --type [doc-type] \
  --level [keigo-level] \
  --input [json-file-or-stdin]
```

### Step 3: Present Output

Show generated document to user for review/copy.

## Keigo Level Guide

| Level | Japanese | Use Case | Example Closing |
|-------|----------|----------|-----------------|
| casual | カジュアル | Internal team | よろしく |
| polite | 丁寧 | Standard business | よろしくお願いいたします |
| honorific | 敬語 | Clients, executives | 何卒よろしくお願い申し上げます |

## Template Customization

Templates are JSON files in `templates/` directory:
- `email-client-ja.json`
- `email-internal-ja.json`
- `report-issue-ja.json`
- `design-doc-ja.json`

Edit JSON to customize sections, labels, and order.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/main.py` | Entry point - CLI interface |
| `scripts/keigo_helper.py` | Keigo level conversion |
| `scripts/japanese_writer.py` | Document generation |

## Tests

```bash
cd ".claude/skills/bk-write" && "../.venv/Scripts/python.exe" -m pytest tests/ -v
```

## Example Output

**Input:** `/bk-write email-client --level=polite`
**Content:** Subject: プロジェクト進捗, Points: 設計完了, 開発開始

**Output:**
```
田中様

いつもお世話になっております。

## 件名: プロジェクト進捗報告

### 詳細
- 設計完了
- 開発開始予定

よろしくお願いいたします。
```
```

### 2. Create main.py (30 min)

**File:** `scripts/main.py`

```python
#!/usr/bin/env python3
"""Entry point for bk-write skill.

Usage:
    python main.py --type email-client --level polite --input data.json
    echo '{"recipient": "田中様"}' | python main.py --type email-client
"""

import argparse
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from japanese_writer import JapaneseWriter, DocumentType
from keigo_helper import KeigoLevel


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Japanese business documents"
    )
    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=["email-client", "email-internal", "report-issue", "design-doc"],
        help="Document type to generate"
    )
    parser.add_argument(
        "--level", "-l",
        default="polite",
        choices=["casual", "polite", "honorific"],
        help="Keigo formality level (default: polite)"
    )
    parser.add_argument(
        "--input", "-i",
        help="JSON file with document data (use stdin if not provided)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (stdout if not provided)"
    )
    return parser.parse_args()


def load_input(input_path: str | None) -> dict:
    """Load input from file or stdin."""
    if input_path:
        with open(input_path, encoding="utf-8") as f:
            return json.load(f)

    # Read from stdin
    if not sys.stdin.isatty():
        return json.load(sys.stdin)

    # Interactive mode - return empty dict
    return {}


def main():
    """Main entry point."""
    args = parse_args()

    # Load input data
    try:
        data = load_input(args.input)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file not found - {args.input}", file=sys.stderr)
        sys.exit(1)

    # Generate document
    writer = JapaneseWriter()
    try:
        doc_type = DocumentType.from_string(args.type)
        level = KeigoLevel.from_string(args.level)

        result = writer.generate(
            doc_type=doc_type,
            level=level,
            **data
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Output result
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Document saved to: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
```

### 3. Create requirements.txt (5 min)

**File:** `requirements.txt`

```
# bk-write dependencies
# No additional dependencies - uses Python standard library only
# pytest for testing (already in shared venv)
```

### 4. Create .env.example (5 min)

**File:** `.env.example`

```bash
# bk-write environment variables
# Currently no environment variables required
# Future: May add default keigo level, company info, etc.

# Optional: Default keigo level
# BK_WRITE_DEFAULT_LEVEL=polite

# Optional: Company info for signatures
# BK_WRITE_COMPANY_NAME=株式会社Example
# BK_WRITE_SENDER_NAME=山田太郎
```

### 5. Final Test Suite (15 min)

```bash
# Run all tests
cd ".claude/skills/bk-write" && "../.venv/Scripts/python.exe" -m pytest tests/ -v

# Test CLI
cd ".claude/skills/bk-write" && echo '{"recipient": "田中様", "subject": "テスト"}' | "../.venv/Scripts/python.exe" scripts/main.py --type email-client --level polite
```

## Todo List

- [ ] Create `SKILL.md` with full documentation
- [ ] Implement `scripts/main.py` CLI entry point
- [ ] Create `requirements.txt`
- [ ] Create `.env.example`
- [ ] Run full test suite
- [ ] Test CLI with sample input
- [ ] Verify SKILL.md follows pattern of bk-task, bk-status

## Success Criteria

- [ ] SKILL.md follows existing patterns
- [ ] `main.py` accepts CLI arguments
- [ ] `main.py` reads from stdin or file
- [ ] Generated output is valid markdown
- [ ] All tests pass
- [ ] `/bk-write` command works in Claude Code

## Final Checklist

- [ ] All 5 phases complete
- [ ] All tests pass
- [ ] SKILL.md documented
- [ ] Templates customizable via JSON
- [ ] 3 keigo levels work correctly
- [ ] 4 document types generate correctly

## Directory Structure (Final)

```
.claude/skills/bk-write/
├── SKILL.md                      # Skill definition
├── .env.example                  # Environment template
├── requirements.txt              # Dependencies
├── scripts/
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   ├── keigo_helper.py           # Keigo conversion
│   └── japanese_writer.py        # Document generation
├── templates/
│   ├── email-client-ja.json
│   ├── email-internal-ja.json
│   ├── report-issue-ja.json
│   └── design-doc-ja.json
└── tests/
    ├── __init__.py
    ├── fixtures/
    │   └── sample_inputs.json
    ├── test_keigo_helper.py
    └── test_japanese_writer.py
```
