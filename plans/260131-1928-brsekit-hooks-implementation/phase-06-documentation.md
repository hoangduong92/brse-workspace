# Phase 6: Update SKILL.md Documentation

## Context Links

- [Phase 1-5](./plan.md) - All implementation phases
- [BrseKit SKILL.md](.claude/skills/brsekit/SKILL.md)

## Overview

| Priority | Status | Effort |
|----------|--------|--------|
| P2 | pending | 30m |

Document hook behavior in SKILL.md so users understand auto-select, warnings, and --project requirement.

## Key Insights

1. Users need to know hooks exist and what they do
2. Document when --project is required vs auto-selected
3. Explain env var status display

## Requirements

Add sections to SKILL.md:
- Hook behavior overview
- Auto-select explanation
- --project requirement explanation
- Subagent context format

## Implementation Steps

1. Add "## Hooks" section to SKILL.md

2. Document session hook behavior:
```markdown
## Hooks

BrseKit hooks inject project context automatically at session start.

### Session Start Hook
- Scans `projects/` directory
- Shows available projects
- Auto-selects if only 1 project
- Warns if multiple projects (use --project)
- Shows env var status (✓/✗)
```

3. Document subagent hook:
```markdown
### Subagent Hook
- Injects minimal context for spawned agents
- Provides vault path and glossary path
- Helps agents access project resources
```

4. Document --project behavior:
```markdown
### --project Flag

| Scenario | Behavior |
|----------|----------|
| 1 project | Auto-selected, --project optional |
| 2+ projects | --project required |
| 0 projects | Error, run /bk-init |
```

## Todo List

- [ ] Add Hooks section to SKILL.md
- [ ] Document session hook output format
- [ ] Document subagent hook output format
- [ ] Add --project behavior table
- [ ] Review and simplify

## Success Criteria

1. Users understand hook behavior without reading code
2. Clear when --project is needed
3. Consistent with actual implementation
