---
title: "BrseKit v1.1 Multi-Project Release"
description: "Upgrade v1.0 to multi-project architecture with lib/, projects/, knowledge/ support"
status: completed
priority: P1
effort: 8h
branch: main
tags: [brsekit, release, multi-project, v1.1]
created: 2026-01-31
completed: 2026-01-31
---

# BrseKit v1.1 Multi-Project Architecture Release

## Objective

Upgrade `experiments/brsekit-starter_v1.0/` from single-project v1.0 to multi-project v1.1 architecture.

## Target Architecture

```
brsekit-starter/
├── lib/                          # Shared utilities (NEW)
│   ├── __init__.py
│   ├── env_loader.py             # 3-tier env fallback
│   ├── project_manager.py        # Project discovery
│   ├── skill_utils.py            # --project arg pattern
│   └── knowledge_manager.py      # Glossary with fallback
├── projects/                     # Per-project data (NEW)
│   └── README.md
├── knowledge/                    # Shared knowledge (NEW)
│   └── glossary-it-terms.json
├── bk-*/                         # Skills with --project support
└── metadata.json                 # Version 1.1.0
```

## Implementation Phases

| Phase | Description | Effort | Status |
|-------|-------------|--------|--------|
| 01 | Add lib/ utilities | 1.5h | ✅ completed |
| 02 | Create projects/ structure | 0.5h | ✅ completed |
| 03 | Create knowledge/ structure | 0.5h | ✅ completed |
| 04 | Update bk-init multi-project | 1h | ✅ completed |
| 05 | Add --project to skills | 3h | ✅ completed |
| 06 | Update install scripts | 1h | ✅ completed |
| 07 | Update metadata and docs | 0.5h | ✅ completed |

## Excluded from v1.1 (Deferred to v1.2)

- cc-memory/ skill
- memory/ directory
- Workspace-level memory migration

## Source Files

Copy from local `.claude/skills/`:
- `lib/env_loader.py`
- `lib/project_manager.py`
- `lib/skill_utils.py`
- `lib/knowledge_manager.py`
- `bk-init/scripts/main.py` (multi-project version)

## Success Criteria

- [x] lib/ utilities copied and working
- [x] projects/README.md exists
- [x] knowledge/glossary-it-terms.json exists
- [x] All 7 skills accept --project arg
- [x] bk-init creates projects/{PROJECT}/
- [x] Install scripts create new directories
- [x] metadata.json version 1.1.0

## Related

- [Release Plan](.claude/skills/brsekit/260131-brsekit-v1.2-multi-project-release-plan.md)
