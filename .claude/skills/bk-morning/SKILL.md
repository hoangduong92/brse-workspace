---
name: bk-morning
description: Morning brief for BrSE - unread counts, overnight updates, blockers, and completed tasks. Use when starting work or checking morning status.
argument-hint: "[--project PROJECT_KEY] [--unread-only] [--json]"
---

# bk-morning

Generate morning brief for BrSE with unread items, overnight updates, completed tasks, and blockers.

## Quick Start

```bash
/bk-morning                          # Full morning brief
/bk-morning --unread-only            # Just unread counts
/bk-morning --json                   # Output as JSON
/bk-morning --project MYPROJ         # Specific project
```

## Output Example

```
┌─────────────────────────────────────────────────────┐
│ 📅 Morning Brief - 2026-01-30 (木)                  │
├─────────────────────────────────────────────────────┤
│ 🔔 UNREAD (3 items since 18:00 yesterday)           │
│   • Backlog: 2 new items                            │
│   • Slack: 1 message                                │
├─────────────────────────────────────────────────────┤
│ ✅ COMPLETED OVERNIGHT                              │
│   • BKT-123: Fix login bug → Ready for UAT          │
│   • BKT-456: API endpoint → Need review             │
├─────────────────────────────────────────────────────┤
│ ⚠️ BLOCKERS                                         │
│   • BKT-789: Waiting for spec clarification         │
└─────────────────────────────────────────────────────┘
```

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--project` | `-p` | `$BACKLOG_PROJECT_KEY` | Project key |
| `--unread-only` | | `false` | Show only unread counts |
| `--json` | | `false` | Output as JSON |
| `--cutoff` | | `18` | Cutoff hour (default: 18:00) |

## Requirements

- **Phase 1 & 2** storage infrastructure must be set up
- **BACKLOG_PROJECT_KEY** environment variable (or use `--project`)
- Synced data via `/bk-recall sync`

## Related Commands

```bash
# Sync before morning brief
/bk-recall sync

# Check sync status
/bk-recall sync-status

# Search for specific items
/bk-recall search "query"
```

## How It Works

1. Reads from **MemoryStore** (JSONL files in `~/.brsekit/projects/{project}/memory/`)
2. Uses **UnreadDetector** for cutoff time logic:
   - Cutoff = max(last_sync, 18:00 yesterday)
3. Aggregates data from:
   - Backlog (issues, comments)
   - Slack messages
   - Email threads
   - Meeting notes
