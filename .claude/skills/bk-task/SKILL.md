---
name: bk-task
description: "[DEPRECATED] Use /bk-capture task instead. Parse unstructured input into tasks."
deprecated: true
redirect: bk-capture task
license: MIT
allowed-tools:
  - Bash
  - Read
  - Write
---

> ⚠️ **DEPRECATED**: This skill is deprecated. Use `/bk-capture task` instead.

## Migration Guide

| Old Command | New Command |
|------------|-------------|
| `/bk-task` | `/bk-capture task` |
| `/bk-task --source email` | `/bk-capture task --source email` |
| `/bk-task --source chat` | `/bk-capture task --source chat` |
| `/bk-task --source minutes` | `/bk-capture task --source minutes` |

## Why Deprecated?

bk-task has been merged into bk-capture for a unified capture experience. All functionality is preserved in the new skill.

---

# bk-task - Create Task from Unstructured Input

Parse unstructured Japanese customer input and create structured Backlog tasks.

## Setup

```bash
# Copy .env.example and fill in credentials
cp .claude/skills/bk-task/.env.example .claude/skills/bk-task/.env

# Install dependencies (use forward slashes for Git Bash/MINGW64)
cd ".claude/skills" && ".venv/Scripts/pip.exe" install -r bk-task/requirements.txt
```

## Usage

```
/bk-task
```

Then paste customer message (Japanese unstructured text).

**Examples:**
```
/bk-task
明日までにログイン画面を田中さんが作成。8時間

/bk-task --source email
[paste email content]

/bk-task --source chat
[paste chat log]
```

**Source Types:**
- `comment` - Backlog comment (default)
- `email` - Forwarded customer email
- `chat` - Slack/Teams message
- `minutes` - Meeting minutes (議事録)

## Workflow Instructions (for Claude Code)

### Step 1: Load Environment
Read `.claude/skills/bk-task/.env` for `NULAB_SPACE_URL`, `NULAB_API_KEY`, `NULAB_PROJECT_ID`.

### Step 2: Parse Input
```bash
# IMPORTANT: Use forward slashes for cross-platform compatibility
cd ".claude/skills/bk-task" && "../.venv/Scripts/python.exe" scripts/main.py --source [type]
```

### Step 3: Review Parsed Task
Claude will show parsed task for user confirmation:

```markdown
## Parsed Task

**Summary:** ログイン機能の不具合修正
**Type:** Bug
**Priority:** High
**Assignee:** 田中 (suggested)
**Due Date:** 2026-01-30 (detected)
**Estimate:** 8h

**Description:**
- 現象: ログインボタンが反応しない
- 環境: Chrome 120
- 再現手順: 1. トップページ → 2. ログインクリック

**Create on Backlog?** [Yes] [No] [Edit first]
```

### Step 4: Create Task (with approval)
Only create on Backlog after user approval.

## Parsing Logic

### Task Type Detection

| Keywords | Type |
|----------|------|
| 不具合, バグ, エラー, 修正 | Bug |
| 機能追加, 実装, 新規, 作成 | Feature |
| 質問, 確認, 問い合わせ | Question |
| 改善, 最適化, リファクタ | Improvement |

### Priority Detection

| Keywords | Priority |
|----------|----------|
| 至急, 緊急, 即時, ASAP | High |
| 今週中, なるべく早く | Normal |
| 時間あれば, 余裕あれば | Low |

### Deadline Detection

| Pattern | Interpretation |
|---------|----------------|
| 明日まで | tomorrow |
| 今週中 | end of week (Friday) |
| 来週まで | end of next week |
| X月Y日 | specific date |
| YYYY/MM/DD | specific date |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NULAB_SPACE_URL` | Yes | Backlog space (e.g., `yourspace.backlog.com`) |
| `NULAB_API_KEY` | Yes | API key |
| `NULAB_PROJECT_ID` | Yes | Default project key |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/main.py` | Entry point - orchestrates parsing & creation |
| `scripts/task_parser.py` | Parse unstructured input → structured task |
| `scripts/task_creator.py` | Create task on Backlog API |

## Tests

```bash
# Use forward slashes for Git Bash/MINGW64 compatibility
cd ".claude/skills/bk-task" && "../.venv/Scripts/python.exe" -m pytest tests/ -v
```

## Test Cases

See brainstorm file for full test cases (TC-TK01 to TC-TK13).

### Key Test Cases

| ID | Test | Input | Expected |
|----|------|-------|----------|
| TC-TK01 | Full structure | 明日までにログイン画面を田中さんが作成。8時間 | All fields |
| TC-TK02 | Implicit deadline | 今週中に | due = Friday |
| TC-TK03 | ASAP | 至急対応 | priority=High |
| TC-TK04 | Multiple items | 5 bullets | 5 tasks |

## Security

- **Human approval required** for creating tasks
- Never auto-create without explicit user confirmation
- Validate all parsed data before API call
