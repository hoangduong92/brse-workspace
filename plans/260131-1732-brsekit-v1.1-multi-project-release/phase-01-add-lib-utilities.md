# Phase 01: Add lib/ Utilities

## Context

- Parent: [plan.md](plan.md)
- Source: `.claude/skills/lib/`
- Target: `experiments/brsekit-starter_v1.0/lib/`

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Priority | P1 |
| Effort | 1.5h |
| Status | pending |

Copy shared utilities from local workspace to brsekit-starter lib/.

## Key Insights

- v1.0 lib/ only has vault/ and `__init__.py`
- Need to add 4 new utility files
- skill_utils.py imports from project_manager and env_loader

## Requirements

### Functional
- Copy env_loader.py (3-tier env fallback)
- Copy project_manager.py (project discovery)
- Copy skill_utils.py (--project arg pattern)
- Copy knowledge_manager.py (glossary with fallback)

### Non-functional
- Maintain import compatibility
- No external dependencies beyond stdlib + dotenv/yaml

## Related Code Files

### Source (copy from)
- `.claude/skills/lib/env_loader.py`
- `.claude/skills/lib/project_manager.py`
- `.claude/skills/lib/skill_utils.py`
- `.claude/skills/lib/knowledge_manager.py`

### Target (copy to)
- `experiments/brsekit-starter_v1.0/lib/env_loader.py`
- `experiments/brsekit-starter_v1.0/lib/project_manager.py`
- `experiments/brsekit-starter_v1.0/lib/skill_utils.py`
- `experiments/brsekit-starter_v1.0/lib/knowledge_manager.py`

## Implementation Steps

1. Copy env_loader.py to target lib/
2. Copy project_manager.py to target lib/
3. Copy skill_utils.py to target lib/
4. Copy knowledge_manager.py to target lib/
5. Update lib/__init__.py to export new modules

## Todo List

- [ ] Copy env_loader.py
- [ ] Copy project_manager.py
- [ ] Copy skill_utils.py
- [ ] Copy knowledge_manager.py
- [ ] Update lib/__init__.py

## Success Criteria

- [ ] All 4 files exist in target lib/
- [ ] No import errors when importing from lib
- [ ] skill_utils can import project_manager and env_loader

## Next Steps

→ Phase 02: Create projects/ structure
