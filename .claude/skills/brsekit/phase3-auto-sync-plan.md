# BrseKit v2 Phase 3: Auto-sync & Unread Detection

## Overview
- **Priority**: Medium
- **Status**: ✅ Complete (2026-01-30)
- **Depends on**: Phase 1 (Storage), Phase 2 (Search)
- **Scope**: Auto-sync từ multiple sources + Unread detection

## Architecture

```
Sources                    BrseKit Memory Layer
─────────                  ───────────────────
Backlog API ──┐
              ├──→ SyncManager ──→ memory/backlog/YYYY-MM-DD.jsonl
Slack API ────┤                 ├→ memory/slack/YYYY-MM-DD.jsonl
              │                 ├→ memory/email/YYYY-MM-DD.jsonl
Gmail API ────┤                 └→ memory/meetings/YYYY-MM-DD.jsonl
              │
Meeting ──────┘
Transcripts
```

## Key Features

### 1. Backlog Comments Sync
- Sync new comments since last_sync
- Track comment_id for incremental sync
- Extract: author, content, timestamp, issue_key

### 2. Unread Detection
- **Cutoff time**: max(last_sync, 18:00 yesterday)
- **Per-source tracking**: Backlog, Slack, Email riêng biệt
- **Summary**: `/bk-morning` shows unread counts

### 3. Meeting Notes Auto-save
- `/bk-capture meeting` auto-saves to memory
- Linked to date-based JSONL files

## Modules to Create/Modify

### 1. Modify `backlog_sync.py` - Add Comments Sync
```python
class BacklogSync:
    def sync_issues(self, project_key: str, since: datetime)
    def sync_comments(self, project_key: str, since: datetime)  # NEW
    def sync_activities(self, project_key: str, since: datetime)

    def _get_new_comments(self, issue_key: str,
                          since: datetime) -> List[Comment]
```

### 2. Create `morning_brief.py` (~100 lines)
```python
class MorningBrief:
    """Generate morning summary for BrSE"""

    def __init__(self, project_key: str)

    def get_unread_summary(self) -> dict
        # {backlog: 5, slack: 3, email: 2}

    def get_overnight_updates(self) -> List[MemoryEntry]
        # Items since 18:00 yesterday

    def get_completed_tasks(self) -> List[dict]
        # Tasks completed by offshore since cutoff

    def get_blockers(self) -> List[dict]
        # Tasks with blocker status

    def generate_brief(self) -> str
        # Formatted markdown summary
```

### 3. Create `sync_scheduler.py` (~60 lines)
```python
class SyncScheduler:
    """Schedule periodic syncs"""

    def __init__(self, project_key: str)

    def sync_all(self)
    def sync_source(self, source: str)

    def get_sync_status(self) -> dict
        # {source: {last_sync, items_count, status}}

    def set_auto_sync(self, enabled: bool, interval_minutes: int = 30)
```

### 4. Modify `bk-recall/sync_manager.py`
```python
# Add project-aware sync
def sync(self, source: str, project_key: str = None, **kwargs):
    if project_key:
        # Use new MemoryStore
        self._sync_to_memory(source, project_key, **kwargs)
    else:
        # Legacy vault sync
        self._sync_to_vault(source, **kwargs)
```

## New Skill: `/bk-morning`

```bash
/bk-morning [--project PROJECT_KEY]
```

**Output:**
```
┌─────────────────────────────────────────────────────┐
│ 📅 Morning Brief - 2026-01-30 (木)                  │
├─────────────────────────────────────────────────────┤
│ 🔔 UNREAD (3 items since 18:00 yesterday)           │
│   • Backlog: 2 new comments                         │
│   • Slack: 1 message                                │
├─────────────────────────────────────────────────────┤
│ ✅ COMPLETED OVERNIGHT                              │
│   • BKT-123: Fix login bug → Ready for UAT         │
│   • BKT-456: API endpoint → Need review            │
├─────────────────────────────────────────────────────┤
│ ⚠️ BLOCKERS                                         │
│   • BKT-789: Waiting for spec clarification        │
├─────────────────────────────────────────────────────┤
│ 👥 MEMBER STATUS (actual hours yesterday)           │
│   • Tanaka: 7.5h ✅                                 │
│   • Nguyen: 5.0h ⚠️ (missing 1h)                   │
└─────────────────────────────────────────────────────┘
```

## Implementation Steps

- [x] 1. Modify `backlog_sync.py` - add comments sync
- [x] 2. Create `morning_brief.py` + tests
- [x] 3. Create `sync_scheduler.py` + tests
- [x] 4. Modify `sync_manager.py` - project-aware
- [x] 5. Create `/bk-morning` skill
- [x] 6. Integration testing (20 tests, 114 total)
- [x] 7. Documentation update (onboarding-guide.md)

## CLI Commands

```bash
# Sync
/bk-recall sync                     # Sync all sources
/bk-recall sync backlog             # Sync Backlog only
/bk-recall sync --since "18:00"     # Sync since specific time

# Morning routine
/bk-morning                         # Full morning brief
/bk-morning --unread-only           # Just unread counts

# Sync status
/bk-recall sync-status              # Show sync state per source
```

## Success Criteria

1. Backlog comments sync incrementally (no duplicates)
2. Unread detection works với cả last_sync và 18:00 cutoff
3. `/bk-morning` generates useful summary in <5 seconds
4. Sync handles rate limits gracefully
5. Member actual hours tracking accurate
6. Auto-sync không block user operations

## Dependencies

- Phase 1: MemoryStore, UnreadDetector
- Phase 2: HybridSearch (for finding blockers)
- Backlog API: `get_issue_comments`, `get_project_activities`

## Estimated Effort

- **New code**: ~260 lines (3 modules)
- **Tests**: ~150 lines
- **Skill setup**: ~50 lines
- **Total**: ~460 lines

---
*Created: 2026-01-30*
