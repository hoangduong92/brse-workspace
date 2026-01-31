---
title: "BrseKit v1.1 Config System + brseLevel"
description: "Add .bk.json config cascading, brseLevel L0-L4, env persistence, session state"
status: completed
priority: P2
effort: 4h
branch: main
tags: [brsekit, hooks, config, infrastructure]
created: 2026-01-31
---

# BrseKit v1.1 Config System + brseLevel

## Overview

Add configuration infrastructure to BrseKit hooks, enabling:
- `.bk.json` config cascading (global → project)
- brseLevel L0-L4 verbosity control
- BK_* env var persistence to CLAUDE_ENV_FILE
- Session state tracking (lastProject)

## Architecture Constraint

**IMPORTANT:** BrseKit hooks MUST remain independent from ClaudeKit.
- Implement patterns similar to ck-config-utils.cjs but in separate files
- NO imports from ClaudeKit code

## Phases

| Phase | File | Status | Effort |
|-------|------|--------|--------|
| 1 | [Config Loader Infrastructure](phase-01-config-loader-infrastructure.md) | pending | 1h |
| 2 | [brseLevel System](phase-02-brselevel-system.md) | pending | 1h |
| 3 | [Env Persistence](phase-03-env-persistence.md) | pending | 30m |
| 4 | [Session State](phase-04-session-state.md) | pending | 30m |
| 5 | [Hook Integration](phase-05-hook-integration.md) | pending | 1h |

## Dependencies

- Phase 2-4 depend on Phase 1 (config loader)
- Phase 5 depends on Phase 1-4

## Key Files

| File | Action |
|------|--------|
| `.claude/hooks/lib/bk-config-loader.cjs` | Create |
| `.claude/hooks/lib/bk-env-writer.cjs` | Create |
| `.claude/hooks/brsekit-session-init.cjs` | Modify |
| `.claude/hooks/brsekit-subagent-init.cjs` | Modify |
| `.claude/skills/brsekit/SKILL.md` | Modify |

## Research

- [ClaudeKit Config Analysis](research/claudekit-config-analysis.md)
- [BrseKit Current State](research/brsekit-current-state.md)
- [Brainstorm Summary](../reports/brainstorm-260131-2214-brsekit-config-system-brselevel.md)

---

## Validation Summary

**Validated:** 2026-01-31
**Questions asked:** 6

### Confirmed Decisions

| Decision | User Choice |
|----------|-------------|
| Default brseLevel (no config) | `-1` (disabled, brseLevel not reflected in system) |
| Skill integration | **MUST respect** BK_BRSE_LEVEL |
| Session state tracking | **Include in v1.1** |
| Guidelines injection | **Always inject** on session start |
| Config file name | `.bk.json` |
| File structure | **Keep separate files** (bk-config-loader.cjs, bk-env-writer.cjs) |

### Action Items

- [ ] **Phase 1:** Change DEFAULT_CONFIG.brseLevel from `2` to `-1` (disabled)
- [ ] **Phase 2:** Add logic: if brseLevel is -1, skip guidelines injection
- [ ] **Phase 5:** Update skills documentation to show MUST requirement for BK_BRSE_LEVEL

### Key Insight

When brseLevel is `-1` (no config), the system behaves as if brseLevel doesn't exist - no guidelines, no level-based formatting. This is opt-in behavior.
