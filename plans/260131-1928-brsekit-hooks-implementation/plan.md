---
title: "BrseKit Hooks Implementation"
description: "Multi-project context injection hooks for BrseKit toolkit"
status: completed
priority: P2
effort: 4.5h
branch: main
tags: [brsekit, hooks, context-injection]
created: 2026-01-31
validated: 2026-01-31
---

# BrseKit Hooks Implementation Plan

## Overview

Implement Claude Code hooks for BrseKit multi-project environment. Session hook scans `projects/` dir, checks env vars, auto-selects single project. Subagent hook injects minimal context (~40 tokens).

**Key decisions:**
- Separate hooks from ClaudeKit (independent coexistence)
- Lazy validation (no file reads at startup)
- API keys: flag only (never expose values)
- Auto-select when 1 project

## Phases

| Phase | Description | Effort | Status |
|-------|-------------|--------|--------|
| [Phase 1](./phase-01-utility-lib.md) | Create bk-config-utils.cjs | 1h | ✅ done |
| [Phase 2](./phase-02-session-hook.md) | Create brsekit-session-init.cjs | 1h | ✅ done |
| [Phase 3](./phase-03-subagent-hook.md) | Create brsekit-subagent-init.cjs | 45m | ✅ done |
| [Phase 4](./phase-04-settings-integration.md) | Update settings.json | 15m | ✅ done |
| [Phase 5](./phase-05-testing.md) | Test multi-project setup | 1h | ✅ done |
| [Phase 6](./phase-06-documentation.md) | Update SKILL.md | 30m | ✅ done |

## File Structure

```
.claude/
├── hooks/
│   ├── brsekit-session-init.cjs    # Session hook
│   ├── brsekit-subagent-init.cjs   # Subagent hook
│   └── lib/
│       ├── ck-config-utils.cjs     # Existing ClaudeKit
│       └── bk-config-utils.cjs     # NEW: BrseKit utils
└── settings.json                    # Add BrseKit hooks
```

## Dependencies

- ClaudeKit hooks pattern (reference only, no code sharing)
- `projects/` directory structure (may not exist)
- Environment variables: BACKLOG_API_KEY, GEMINI_API_KEY, SLACK_WEBHOOK_URL

## Success Criteria

1. Startup speed: < 100ms hook execution
2. Token efficiency: < 100 tokens session, < 40 tokens subagent
3. Zero breaking changes to existing skills
4. Error clarity: helpful messages when --project missing

## Research Reports

- [ClaudeKit Hooks Analysis](./research/researcher-claudekit-hooks-analysis.md)
- [BrseKit Skills Analysis](./research/researcher-brsekit-skills-analysis.md)
- [Brainstorm Summary](../reports/brainstorm-260131-1928-brsekit-hooks-implementation.md)

---

## Validation Summary

**Validated:** 2026-01-31
**Questions asked:** 5

### Confirmed Decisions

1. **Glossary check**: Keep, but output PATH instead of ✓/✗
   - Subagent output: `glossary: projects/X/glossary.json` (path for agent to use)
2. **Hidden folders**: Ignore (filter out folders starting with `.`)
3. **Hook chain**: Independent execution (BrseKit runs even if ClaudeKit fails)
4. **Output style**: Use emoji (✓ ✗ ⚠️) for compact display
5. **Documentation**: Add Phase 6 to update SKILL.md

### Action Items

- [ ] Update Phase 3: Change glossary output from `✓/✗` to actual path
- [ ] Update Phase 1: Add hidden folder filter to `scanProjectsDir()`
- [ ] Create Phase 6: Update SKILL.md with hook behavior
