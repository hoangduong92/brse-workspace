---
name: bk-recall
description: Memory layer - store, search, and summarize project context from emails, Backlog. Use when searching past context or syncing data.
argument-hint: "<sync|search|summary|list> [query] [--source email|backlog] [--limit N]"
---

# bk-recall

Unified memory skill for BrseKit - store, search, and summarize project context from emails, Backlog, and other sources.

## Usage

```bash
# Sync data from sources
/bk-recall sync              # Sync all configured sources
/bk-recall sync email        # Sync emails only
/bk-recall sync backlog      # Sync Backlog only

# Search across all sources
/bk-recall search "login bug"
/bk-recall search "要件変更" --source email

# Generate context summary
/bk-recall summary
/bk-recall summary "authentication"

# List recent items
/bk-recall list
/bk-recall list --source email --limit 20
```

## Configuration

Set in `.env`:
```
GOOGLE_API_KEY=your-gemini-api-key
BACKLOG_SPACE_URL=your-space.backlog.jp
BACKLOG_API_KEY=your-backlog-api-key
```

For Gmail sync, configure OAuth credentials in `~/.brsekit/gmail_credentials.json`.

## Data Flow

```
Sources → bk-recall sync → Vault (SQLite + embeddings)
                              ↓
User query → bk-recall search → Semantic search → Results
                              ↓
           → bk-recall summary → LLM summarization
```
