# Phase 05: Add --project Argument Support to Skills

## Context

- Parent: [plan.md](plan.md)
- Depends on: Phase 01, 04

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Priority | P1 |
| Effort | 3h |
| Status | pending |

Add --project/-p argument to 7 skills using skill_utils pattern.

## Key Insights

- skill_utils.py provides: add_project_arg, get_project, setup_project_env
- Pattern is consistent across all skills
- bk-convert also needs glossary path update for knowledge/

## Requirements

### Pattern to Apply
```python
# At top of main.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))
from skill_utils import add_project_arg, get_project, setup_project_env

# In argparse setup
add_project_arg(parser)

# In main function
project = get_project(args)
if project:
    pm, env_loader = setup_project_env(project)
```

### Skills to Update

| Skill | main.py | Special Notes |
|-------|---------|---------------|
| bk-track | scripts/main.py | Already has --project, needs lib import |
| bk-capture | scripts/main.py | Add --project |
| bk-spec | scripts/main.py | Add --project |
| bk-recall | scripts/main.py | Add --project |
| bk-convert | scripts/main.py | Add --project + knowledge/ glossary |
| bk-morning | scripts/main.py | Add --project |
| bk-write | scripts/main.py | Add --project |

### bk-convert Special Case
```python
# Update glossary_manager.py to use knowledge/ path
from knowledge_manager import KnowledgeManager

km = KnowledgeManager()
glossary = km.get_glossary(project)
```

## Implementation Steps

1. Update bk-track/scripts/main.py - add lib import
2. Update bk-capture/scripts/main.py
3. Update bk-spec/scripts/main.py
4. Update bk-recall/scripts/main.py
5. Update bk-convert/scripts/main.py + glossary path
6. Update bk-morning/scripts/main.py
7. Update bk-write/scripts/main.py

## Todo List

- [ ] bk-track: add lib import for skill_utils
- [ ] bk-capture: add --project support
- [ ] bk-spec: add --project support
- [ ] bk-recall: add --project support
- [ ] bk-convert: add --project + knowledge/ glossary
- [ ] bk-morning: add --project support
- [ ] bk-write: add --project support

## Success Criteria

- [ ] All 7 skills accept --project/-p argument
- [ ] bk-convert uses knowledge/glossary-it-terms.json
- [ ] No import errors

## Next Steps

→ Phase 06: Update install scripts
