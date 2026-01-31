---
title: "Claude Code Memory Skill"
description: "User-level memory system replicating claude.ai memory feature"
status: pending
priority: P1
effort: 6h
branch: main
tags: [memory, claude-code, skill, hooks]
created: 2026-01-30
---

# CC-Memory Skill Implementation Plan

## Overview

Implement `/memory` skill that provides persistent memory across Claude Code sessions, replicating claude.ai's memory feature at user level.

## Architecture

```
~/claude_client/memory/
├── vault.db                    # SQLite + Gemini embeddings
├── facts.md                    # Core facts (always loaded)
├── conversations/
│   ├── index.json              # Session registry
│   └── archives/               # Archived transcripts
│       └── {date}-{workspace}-{session_id}.jsonl
└── config.json                 # Settings
```

## Key Decisions

1. **Reuse vault lib** - Extend existing `.claude/skills/lib/vault/` for memory storage
2. **Heuristics + Gemini** - Hybrid extraction (fast heuristics, smart Gemini for important sessions)
3. **User-level storage** - `~/claude_client/memory/` separate from project-level data
4. **Lazy loading** - facts.md loaded on SessionStart via hook

## Phase Summary

| Phase | Name | Status | Effort |
|-------|------|--------|--------|
| 0 | Memory Infrastructure | pending | 1.5h |
| 1 | SessionEnd Hook | pending | 1.5h |
| 2 | SessionStart Hook | pending | 0.5h |
| 3 | Skill Commands | pending | 2h |
| 4 | Testing | pending | 0.5h |

## Dependencies

- `.claude/skills/lib/vault/` - SQLite + embeddings (exists)
- `.claude/skills/.venv/` - Python env with google-genai (exists)
- `.claude/hooks/` - Hook infrastructure (exists)
- `GOOGLE_API_KEY` - For Gemini embeddings

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large transcripts | High | Chunked extraction, skip >1MB |
| Gemini rate limits | Medium | Batch processing, fallback to heuristics |
| Stale facts | Low | Manual cleanup via `/memory forget` |

## Next Steps

1. Review phase-00 for memory infrastructure setup
2. Implement MemoryDB extending VaultDB
3. Build SessionEnd hook for fact extraction
