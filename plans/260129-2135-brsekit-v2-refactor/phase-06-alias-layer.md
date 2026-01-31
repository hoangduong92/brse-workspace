# Phase 6: Alias Layer (Backward Compatibility)

## Context Links
- [Phase 2: bk-track](./phase-02-bk-track.md)
- [Phase 3: bk-capture](./phase-03-bk-capture.md)
- [Phase 4: bk-spec](./phase-04-bk-spec.md)

## Overview
- **Priority:** P1
- **Status:** 100% complete (all 6 deprecated skills configured with migration guides)
- **Effort:** 1h
- **Description:** Create alias layer for deprecated skills (zero breaking changes)

## Key Insights
- Users may have existing scripts/workflows using old commands
- Alias layer routes old commands to new skills
- Deprecation warnings guide users to new commands
- Can be removed in v3 after migration period

## Requirements

### Functional
- `/bk-status` → `/bk-track status`
- `/bk-report` → `/bk-track report`
- `/bk-task` → `/bk-capture task`
- `/bk-minutes` → `/bk-capture meeting`
- `/bk-tester` → `/bk-spec test`
- `/bk-translate` → `/bk-convert`
- Show deprecation notice, then execute new command

### Non-Functional
- Zero breaking changes for existing users
- Transparent routing (same flags, same output)
- Clear deprecation messages

## Architecture

```
.claude/skills/
├── bk-status/           # Alias → bk-track
│   └── SKILL.md         # Deprecation notice + routing
├── bk-report/           # Alias → bk-track
│   └── SKILL.md
├── bk-task/             # Alias → bk-capture
│   └── SKILL.md
├── bk-minutes/          # Alias → bk-capture
│   └── SKILL.md
├── bk-tester/           # Alias → bk-spec
│   └── SKILL.md
└── bk-translate/        # Alias → bk-convert
    └── SKILL.md
```

### Alias SKILL.md Pattern
```markdown
---
name: bk-status
description: "[DEPRECATED] Use /bk-track status instead"
deprecated: true
alias_for: bk-track status
---

# bk-status (Deprecated)

**This skill is deprecated. Use `/bk-track status` instead.**

## Migration Guide

Old command:
```
/bk-status --threshold 5
```

New command:
```
/bk-track status --threshold 5
```

## Auto-routing

When you invoke `/bk-status`, it automatically routes to `/bk-track status`.
All flags are preserved.
```

## Related Code Files

### Modify
- `.claude/skills/bk-status/SKILL.md` - Convert to alias
- `.claude/skills/bk-report/SKILL.md` - Convert to alias
- `.claude/skills/bk-task/SKILL.md` - Convert to alias
- `.claude/skills/bk-minutes/SKILL.md` - Convert to alias
- `.claude/skills/bk-tester/SKILL.md` - Convert to alias
- `.claude/skills/bk-translate/SKILL.md` - Convert to alias + rename to bk-convert

### Delete (scripts only, keep SKILL.md for alias)
- `.claude/skills/bk-status/scripts/` - Move to bk-track
- `.claude/skills/bk-report/scripts/` - Move to bk-track
- `.claude/skills/bk-task/scripts/` - Move to bk-capture
- `.claude/skills/bk-minutes/scripts/` - Move to bk-capture
- `.claude/skills/bk-tester/scripts/` - Move to bk-spec

### Create
- `.claude/skills/bk-convert/SKILL.md` - New name for bk-translate
- `.claude/skills/bk-convert/scripts/` - Move from bk-translate

## Implementation Steps

1. **Verify new skills work**
   - Run all tests for bk-track, bk-capture, bk-spec
   - Confirm output matches old skills

2. **Update bk-status SKILL.md**
   - Add deprecated: true frontmatter
   - Add alias_for: bk-track status
   - Write migration guide
   - Keep minimal for routing

3. **Update bk-report SKILL.md**
   - Same pattern as bk-status
   - alias_for: bk-track report

4. **Update bk-task SKILL.md**
   - alias_for: bk-capture task

5. **Update bk-minutes SKILL.md**
   - alias_for: bk-capture meeting

6. **Update bk-tester SKILL.md**
   - alias_for: bk-spec test

7. **Rename bk-translate → bk-convert**
   - Create `.claude/skills/bk-convert/`
   - Move scripts from bk-translate
   - Update SKILL.md
   - Create bk-translate alias pointing to bk-convert

8. **Clean up old scripts**
   - Remove scripts/ from aliased skills
   - Keep SKILL.md for documentation
   - Keep tests/ for reference

9. **Update CLAUDE.md skill index**
   - List new skills as primary
   - Mark deprecated skills

10. **Test all aliases**
    - Verify old commands still work
    - Verify deprecation notice shown
    - Verify output matches

## Todo List

- [ ] Verify bk-track works correctly
- [ ] Verify bk-capture works correctly
- [ ] Verify bk-spec works correctly
- [ ] Update bk-status SKILL.md (alias)
- [ ] Update bk-report SKILL.md (alias)
- [ ] Update bk-task SKILL.md (alias)
- [ ] Update bk-minutes SKILL.md (alias)
- [ ] Update bk-tester SKILL.md (alias)
- [ ] Rename bk-translate to bk-convert
- [ ] Create bk-translate alias
- [ ] Clean up old scripts directories
- [ ] Update CLAUDE.md skill index
- [ ] Test all alias routes

## Success Criteria

- [ ] `/bk-status` routes to `/bk-track status`
- [ ] `/bk-report` routes to `/bk-track report`
- [ ] `/bk-task` routes to `/bk-capture task`
- [ ] `/bk-minutes` routes to `/bk-capture meeting`
- [ ] `/bk-tester` routes to `/bk-spec test`
- [ ] `/bk-translate` routes to `/bk-convert`
- [ ] All flags preserved through routing
- [ ] Deprecation notice displayed

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Flag incompatibility | Low | Test all flag combinations |
| Output format change | Low | Diff test outputs |
| User confusion | Medium | Clear deprecation messages |

## Security Considerations

- No security changes (pass-through routing)
- Same permissions as new skills

## Next Steps

- Monitor deprecation warnings usage
- Plan removal in v3 (6+ months)
- Document migration in changelog
