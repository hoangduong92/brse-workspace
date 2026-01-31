# Phase 04: Update bk-init for Multi-Project Support

## Context

- Parent: [plan.md](plan.md)
- Depends on: Phase 01, 02

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Priority | P1 |
| Effort | 1h |
| Status | pending |

Update bk-init to create projects in projects/{PROJECT}/ directory.

## Key Insights

- Current local bk-init already supports multi-project
- Creates: projects/{PROJECT}/.env, context.yaml, vault/
- Needs lib path import adjustments for target

## Requirements

### Functional
- `bk-init HB21373` creates `projects/HB21373/`
- Creates .env, context.yaml, vault/ in project dir
- Interactive wizard for credentials and config

### CLI Usage
```
bk-init HB21373            # Create project in projects/HB21373/
bk-init                    # Interactive wizard (current directory)
bk-init HB21373 --env-only # Only setup .env
```

## Related Code Files

### Source
- `.claude/skills/bk-init/scripts/main.py`
- `.claude/skills/bk-init/scripts/wizard.py`
- `.claude/skills/bk-init/scripts/validator.py`
- `.claude/skills/bk-init/scripts/config_generator.py`
- `.claude/skills/bk-init/scripts/env_setup.py`

### Target
- `experiments/brsekit-starter_v1.0/bk-init/scripts/main.py`
- Other supporting scripts as needed

## Implementation Steps

1. Compare local vs target bk-init/scripts/main.py
2. Copy multi-project main.py to target
3. Update sys.path for lib imports
4. Verify wizard.py and other deps exist
5. Test: bk-init TEST creates projects/TEST/

## Todo List

- [ ] Copy main.py with multi-project support
- [ ] Adjust sys.path imports for target structure
- [ ] Verify all script dependencies exist

## Success Criteria

- [ ] `bk-init PROJECT` creates projects/PROJECT/
- [ ] Created structure has .env, context.yaml, vault/

## Next Steps

→ Phase 05: Add --project support to skills
