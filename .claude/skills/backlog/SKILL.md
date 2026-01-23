---
name: backlog
description: Automate ticket creation from customer backlog to internal backlog with AI translation (JA ↔ VI) and dynamic task templates
license: MIT
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "\"$CLAUDE_PROJECT_DIR\"/.claude/skills/.venv/Scripts/python \"$CLAUDE_PROJECT_DIR\"/.claude/skills/backlog/scripts/prevent_delete.py"
---

# Backlog Automation

Copy tickets from customer Nulab Backlog to internal backlog with in-conversation JA ↔ VI translation.

## Setup

```bash
# Copy .env.example to .env and fill in your Nulab API key
cp .claude/skills/backlog/.env.example .claude/skills/backlog/.env

# Install dependencies (uses shared venv)
cd .claude/skills && .venv/Scripts/pip install -r backlog/requirements.txt
```

## Usage

```
/backlog <ticket_id> [--type=feature|scenario|issue]
```

**Examples:**
```
/backlog HB21373-123
/backlog HB21373-456 --type=feature
```

## Workflow Instructions (for Claude Code)

When this skill is invoked, follow these steps IN ORDER:

### Step 1: Parse Arguments
Extract ticket_id and optional --type flag from the command arguments.
- Example: `/backlog HB21373-123` → ticket_id = "HB21373-123"
- Example: `/backlog HB21373-456 --type=feature` → ticket_id = "HB21373-456", type = "feature"

### Step 2: Fetch Source Ticket
```bash
cd .claude/skills && .venv/Scripts/python backlog/scripts/fetch_ticket.py <TICKET_ID>
```

### Step 3: Display Original Content
Show the user the original ticket content:

---
**Source Ticket:** [TICKET_ID]

**Summary (原文/Tiêu đề gốc):**
> [original summary]

**Description (説明/Mô tả gốc):**
> [original description]

---

### Step 4: Translate Content (In-Conversation)
YOU (Claude Code) translate the content directly:
- Japanese → Vietnamese
- Vietnamese → Japanese

**Translation rules:**
- Preserve: code blocks, URLs, technical terms, issue IDs, file paths
- Translate naturally, not word-by-word
- Keep markdown formatting

Show translated content:

---
**Translated Summary (翻訳/Bản dịch):**
> [translated summary]

**Translated Description (翻訳/Bản dịch):**
> [translated description]

---

### Step 5: Detect Task Type
Based on keywords in the ticket content:
- **feature**: 機能, 開発, 実装, feature, dev, implement, tính năng, phát triển
- **scenario**: シナリオ, アップロード, scenario, upload, kịch bản, tải lên
- **issue**: 調査, バグ, 修正, investigate, bug, fix, điều tra, lỗi, sửa

Default to **feature** if no pattern matches.
Use the --type flag if user provided it.

### Step 6: Ask User Confirmation
Use AskUserQuestion with options:
- Question: "Create this ticket?"
- Options: "Yes, create ticket" / "No, cancel"
- Include in description:
  - Task Type: [detected/specified type]
  - Subtasks: [4 for feature, 0 for others]
  - Attachments to copy: [count]

### Step 7: Create Ticket (if confirmed)
```bash
cd .claude/skills && .venv/Scripts/python backlog/scripts/create_ticket.py \
  --summary "TRANSLATED_SUMMARY" \
  --description "TRANSLATED_DESCRIPTION" \
  --issue-type-id ISSUE_TYPE_ID \
  --priority-id PRIORITY_ID
```

### Step 8: Copy Attachments (if any)
```bash
cd .claude/skills && .venv/Scripts/python backlog/scripts/copy_attachments.py \
  --source SOURCE_TICKET_ID \
  --dest DEST_TICKET_KEY
```

### Step 9: Create Subtasks (if feature type)
For feature type only, create 4 subtasks:
```bash
cd .claude/skills && .venv/Scripts/python backlog/scripts/create_subtask.py \
  --parent-id PARENT_ID \
  --summary "[Analysis] TRANSLATED_SUMMARY" \
  --issue-type-id ISSUE_TYPE_ID \
  --priority-id PRIORITY_ID
```
Repeat for: [Implementation], [Testing], [Code Review]

### Step 10: Add Reference Comment to Source
```bash
cd .claude/skills && .venv/Scripts/python backlog/scripts/add_comment.py \
  --issue-id SOURCE_TICKET_ID \
  --content "Copied to internal backlog: DEST_TICKET_KEY"
```

### Step 11: Report Result
Show the user:
- Created ticket ID and URL
- Number of subtasks created (if any)
- Number of attachments copied (if any)

## Task Types

| Type | Subtasks | Description |
|------|----------|-------------|
| `feature` | 10 | RPA workflow (Hearing → Spec → Review → Coding → Test → UAT → Release) |
| `scenario` | 0 | Upload scenario |
| `issue` | 0 | Investigate issue |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NULAB_SPACE_URL` | Yes | Nulab space URL (e.g., `hblab.backlogtool.com`) |
| `NULAB_API_KEY` | Yes | Nulab API key |
| `NULAB_PROJECT_ID` | Yes | Nulab project ID (e.g., `HB21373`) |

## Features

- In-conversation translation (JA ↔ VI) by Claude Code
- Interactive workflow with user confirmation
- Dynamic templates by task type
- Auto-subtask creation for feature development
- Attachment copying from source to destination
- Priority preservation from source ticket
