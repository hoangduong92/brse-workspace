# Phase 1: bk-recall (Memory + Search + Summary)

## Context Links
- [Phase 0: Vault Infrastructure](./phase-00-vault-infrastructure.md)
- [Vault Patterns Research](./research/researcher-vault-patterns-report.md)

## Overview
- **Priority:** P0
- **Status:** 100% complete (63 tests passing)
- **Effort:** 4h
- **Description:** Unified memory skill - store, search, summarize project context

## Key Insights
- Vault is invisible infrastructure; bk-recall is user-facing
- Sync priority: email → meeting → slack → backlog → gchat
- Auto-invoked by bk-capture for storage, bk-spec for context
- Summary feature for quick context overview

## Requirements

### Functional
- `/bk-recall sync [source]` - Sync data from sources
- `/bk-recall search <query>` - Semantic search across all sources
- `/bk-recall summary [topic]` - Generate context summary
- `/bk-recall list [--source X]` - List recent items

### Non-Functional
- Search latency <200ms for typical queries
- Summarization via Claude/Gemini
- Incremental sync (only new items)

## Architecture

```
.claude/skills/bk-recall/
├── SKILL.md
├── requirements.txt
├── scripts/
│   ├── main.py           # CLI entry point
│   ├── sync_manager.py   # Orchestrate source syncs
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── email_sync.py
│   │   ├── slack_sync.py
│   │   ├── backlog_sync.py
│   │   └── gchat_sync.py
│   ├── search_handler.py # Search interface
│   └── summarizer.py     # Context summarization
└── tests/
    ├── test_sync.py
    └── test_search.py
```

### Data Flow
```
User: /bk-recall sync email
         ↓
    sync_manager.py
         ↓
    email_sync.py (fetch new emails)
         ↓
    lib/vault/store.py (save with embedding)
         ↓
    sync_tracker.py (update last_synced)
```

## Related Code Files

### Create
- `.claude/skills/bk-recall/SKILL.md`
- `.claude/skills/bk-recall/requirements.txt`
- `.claude/skills/bk-recall/scripts/main.py`
- `.claude/skills/bk-recall/scripts/sync_manager.py`
- `.claude/skills/bk-recall/scripts/sources/__init__.py`
- `.claude/skills/bk-recall/scripts/sources/email_sync.py`
- `.claude/skills/bk-recall/scripts/sources/slack_sync.py`
- `.claude/skills/bk-recall/scripts/sources/backlog_sync.py`
- `.claude/skills/bk-recall/scripts/search_handler.py`
- `.claude/skills/bk-recall/scripts/summarizer.py`
- `.claude/skills/bk-recall/tests/test_sync.py`
- `.claude/skills/bk-recall/tests/test_search.py`

### Reuse
- `.claude/skills/common/backlog/client.py` (Backlog API)
- `.claude/skills/lib/vault/*` (vault infrastructure)

## Implementation Steps

1. **Create skill structure**
   - Create directories and SKILL.md
   - Define CLI interface in SKILL.md

2. **Implement main.py CLI (50 lines)**
   - argparse: sync, search, summary, list subcommands
   - Route to appropriate handlers
   - Output formatting (Markdown)

3. **Implement sync_manager.py (60 lines)**
   - `SyncManager` class
   - `sync(source: str)` - dispatch to source-specific syncer
   - `sync_all()` - sync all configured sources
   - Progress reporting

4. **Implement email_sync.py (80 lines)**
   - IMAP/Gmail API integration
   - Fetch emails since last_synced
   - Extract: subject, body, sender, date
   - Convert to VaultItem, save to vault

5. **Implement slack_sync.py (60 lines)**
   - Slack conversations API
   - Fetch messages since last_synced
   - Handle threads
   - Convert to VaultItem

6. **Implement backlog_sync.py (50 lines)**
   - Reuse `common/backlog/client.py`
   - Fetch recent comments, issue updates
   - Convert to VaultItem

7. **Implement search_handler.py (40 lines)**
   - `search(query: str, source: Optional[str], top_k: int) -> list[SearchResult]`
   - Format results as Markdown
   - Include source, title, snippet, date

8. **Implement summarizer.py (50 lines)**
   - `summarize(topic: Optional[str]) -> str`
   - Fetch relevant items via search
   - Generate summary via Claude/Gemini prompt
   - Return structured summary

9. **Write tests (TDD)**
   - test_sync.py: mock API responses
   - test_search.py: verify result formatting

## Todo List

- [ ] Create bk-recall skill directory
- [ ] Write SKILL.md documentation
- [ ] Implement CLI (main.py)
- [ ] Implement SyncManager
- [ ] Implement email_sync.py
- [ ] Implement slack_sync.py (stub)
- [ ] Implement backlog_sync.py
- [ ] Implement search_handler.py
- [ ] Implement summarizer.py
- [ ] Write unit tests
- [ ] Integration test with vault

## Success Criteria

- [ ] `/bk-recall sync email` fetches and stores emails
- [ ] `/bk-recall search "login bug"` returns relevant results
- [ ] `/bk-recall summary` generates coherent context summary
- [ ] Incremental sync works (no duplicates)
- [ ] All tests pass

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Email auth complexity | Medium | Support App Passwords, OAuth |
| Slack rate limits | Low | Batch requests, respect limits |
| Large mailboxes | Medium | Limit to last N days on first sync |

## Security Considerations

- OAuth tokens stored securely (keyring or encrypted file)
- No plain-text passwords in config
- Vault content encrypted at rest (optional Phase 8)

## Next Steps

- Phase 3: bk-capture (auto-save to vault via bk-recall)
- Phase 4: bk-spec (query bk-recall for context)
