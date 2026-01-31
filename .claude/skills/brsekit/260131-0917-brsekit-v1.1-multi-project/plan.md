---
title: "BrseKit v1.1 Multi-Project Architecture"
description: "Refactor BrseKit to support explicit project management with per-project vaults"
status: completed
priority: P1
effort: 16h
branch: main
tags: [brsekit, multi-project, vault, refactor]
created: 2026-01-31
completed: 2026-01-31
---

# BrseKit v1.1 Multi-Project Architecture

## Overview

Refactor BrseKit from single-project implicit mode to explicit multi-project architecture.

**Core Principle**: No `.active` file - always require explicit project: `/bk-track status HB21373`

## Target Structure

```
<workspace>/
├── .claude/skills/                   # CODE
│   ├── bk-track/
│   ├── bk-capture/
│   ├── bk-spec/
│   ├── bk-recall/
│   ├── bk-convert/
│   ├── bk-init/
│   ├── bk-morning/
│   ├── bk-write/
│   ├── brsekit/
│   ├── cc-memory/                    # Included in kit
│   ├── common/
│   └── lib/
│
├── projects/                         # DATA - Per-project
│   ├── HB21373/
│   │   ├── .env                      # BACKLOG_API_KEY, SLACK_TOKEN
│   │   ├── context.yaml              # Project config
│   │   └── vault/                    # Project-specific memory
│   └── ABC/
│
├── knowledge/                        # DATA - Shared
│   └── glossary-it-terms.json
│
├── memory/                           # DATA - Memory layer
│   ├── lib/                          # SQLite + embeddings
│   └── conversation-history/         # cc-memory
│
├── .env                              # Workspace credentials
└── CLAUDE.md
```

## Phases

| Phase | Description | Effort | Status |
|-------|-------------|--------|--------|
| [01](./phase-01-core-infrastructure.md) | Core Infrastructure | 4h | ✅ complete |
| [02](./phase-02-update-skills.md) | Update Skills | 5h | ✅ complete |
| [03](./phase-03-knowledge-layer.md) | Knowledge Layer | 2h | ✅ complete |
| [04](./phase-04-cc-memory-integration.md) | cc-memory Integration | 2h | ✅ complete |
| [05](./phase-05-cli-documentation.md) | CLI & Documentation | 3h | ✅ complete |

## Key Decisions

1. **No .active file** - Explicit project arg required
2. **Env fallback**: `projects/{name}/.env` → `.env` → System env
3. **Single SQLite DB** with `project` column for cross-project search
4. **Knowledge fallback**: Project-specific → Shared IT terms
5. **cc-memory** integrated as first-class skill

## Dependencies

- Source: `experiments/brsekit-starter_v1.1/`
- Vault lib: `.claude/skills/lib/vault/`
- Target: `.claude/skills/` (update in place)

## Success Criteria

- [x] All bk-* commands accept `--project` or positional arg
- [x] `bk-init HB21373` creates `projects/HB21373/` structure
- [x] Vault stores data in `projects/{name}/vault/` SQLite
- [x] Env vars load from project → workspace → system
- [x] Knowledge glossaries fallback correctly
- [x] cc-memory works with user-level storage
- [ ] All existing tests pass (manual verification needed)
