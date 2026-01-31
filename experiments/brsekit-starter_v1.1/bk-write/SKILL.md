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
cd ".claude/skills" && ".venv/Scripts/pip.exe" show pytest
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
- `casual` - Internal, familiar colleagues
- `polite` - Standard business [default]
- `honorific` - Client-facing, executives

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

**For email-internal:**
- recipient: 宛先 (e.g., 佐藤さん)
- subject: 件名
- content_points: 要点 (list)

**For report-issue:**
- issue_title: 概要
- environment: 環境
- steps: 再現手順 (list)
- expected_behavior: 期待動作
- actual_behavior: 実際の動作

**For design-doc:**
- feature_name: 機能名
- overview: 概要
- tech_stack: 技術構成 (list)
- schedule: スケジュール

### Step 2: Generate Document

```bash
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

Edit JSON in `templates/` directory:
- `email-client-ja.json`
- `email-internal-ja.json`
- `report-issue-ja.json`
- `design-doc-ja.json`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/main.py` | CLI entry point |
| `scripts/keigo_helper.py` | Keigo conversion |
| `scripts/japanese_writer.py` | Document generation |

## Tests

```bash
cd ".claude/skills/bk-write" && "../.venv/Scripts/python.exe" -m pytest tests/ -v
```
