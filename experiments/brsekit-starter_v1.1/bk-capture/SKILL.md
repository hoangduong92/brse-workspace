---
name: bk-capture
description: Capture tasks and meeting minutes from text, emails, transcripts. Use when parsing tasks, meeting notes, or unstructured input.
argument-hint: "<task|meeting|email> <text or file> [--lang ja|en|vi]"
---

# bk-capture

Unified capture skill - parse unstructured input into tasks, meeting minutes, and action items. Auto-saves to vault.

## Usage

```bash
# Parse text into tasks
/bk-capture task "明日までにログイン機能を実装してください"
/bk-capture task email.txt

# Parse meeting transcript
/bk-capture meeting transcript.txt
/bk-capture meeting recording.mp4  # Transcribe + parse

# Parse email into tasks
/bk-capture email customer-email.txt
```

## Features

- Japanese/Vietnamese/English text parsing
- Deadline detection (明日, 今週中, by Friday)
- Priority detection (至急, ASAP, 優先度高)
- Auto-classification (Task/Issue/Risk/Question)
- Auto-save to vault for context memory
- Human approval before Backlog creation

## Migration

```bash
# Old: /bk-task "input"
# New: /bk-capture task "input"

# Old: /bk-minutes transcript.txt
# New: /bk-capture meeting transcript.txt
```
