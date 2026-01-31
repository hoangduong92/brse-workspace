# BrseKit Config System + brseLevel - Brainstorm Summary

**Date:** 2026-01-31
**Status:** Brainstormed, pending plan creation
**Related:** [BrseKit Hooks Plan](../260131-1928-brsekit-hooks-implementation/plan.md)

---

## Problem Statement

BrseKit hooks (v1.0) thiếu các best practices từ ClaudeKit:
- Không có config file để customize behavior
- Không có level system cho different BrSE skill levels
- Không persist env vars cho skills/bash commands
- Không track session state

---

## Confirmed Decisions

| Feature | Decision |
|---------|----------|
| Config file | `.bk.json` với cascading: global → project |
| Level system | brseLevel L0-L4 (like codingLevel) |
| Env persistence | Write BK_* vars to CLAUDE_ENV_FILE |
| Session state | Track last used project only |
| Workflow suggestions | Proactive for juniors (L0-L1) |

---

## Config Cascading

```
1. DEFAULT (hardcoded in hook)
   └── brseLevel: 2, hooks: enabled

2. ~/.claude/.bk.json (global/user-level)
   └── User's preferred brseLevel

3. .claude/.bk.json (workspace/project-level)
   └── Project-specific defaults
```

**Merge rule:** Later overrides earlier (project > global > default)

---

## brseLevel Definition

| Level | Name | Verbosity | Guidance | Workflow |
|-------|------|-----------|----------|----------|
| L0 | Intern | Very detailed | Step-by-step | Proactive suggestions |
| L1 | Junior | Detailed | Tips + warnings | Proactive suggestions |
| L2 | Mid | Balanced | When relevant | Ask before suggesting |
| L3 | Senior | Concise | Minimal | On-demand only |
| L4 | Lead | Raw/compact | None | On-demand only |

---

## Config Schema (Proposed)

```json
{
  "brseLevel": 2,
  "hooks": {
    "session-init": true,
    "subagent-init": true
  },
  "defaults": {
    "project": "HB21373",
    "language": "vi"
  },
  "envVars": [
    "BACKLOG_API_KEY",
    "GEMINI_API_KEY",
    "SLACK_WEBHOOK_URL"
  ]
}
```

---

## Env Vars to Write

| Var | Purpose | Example |
|-----|---------|---------|
| `BK_BRSE_LEVEL` | Output verbosity control | `2` |
| `BK_PROJECTS_PATH` | Projects directory | `./projects` |
| `BK_ACTIVE_PROJECT` | Auto-selected/default project | `HB21373` |
| `BK_VAULT_PATH` | Project vault path | `./projects/HB21373/vault` |
| `BK_GLOSSARY_PATH` | Project glossary path | `./projects/HB21373/glossary.json` |

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Claude Code Session                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Config Layer          Hooks Layer           Skills Layer            │
│  ─────────────         ───────────           ────────────            │
│                                                                       │
│  .bk.json         →    session-init.cjs  →   /bk-morning             │
│  - brseLevel           - Load config         - Read BK_BRSE_LEVEL    │
│  - defaults            - Write env vars      - Format by level       │
│                        - Output context                              │
│                                                                       │
│                        subagent-init.cjs →   Subagents               │
│                        - Read env vars       - Access paths          │
│                        - Inject context      - Use level             │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## brseLevel Impact on Skills

### /bk-morning Example

**L0-L1:**
```markdown
## Morning Brief - HB21373

### Overnight Updates (3 items)
Đây là các updates từ team JP. Review và respond trong buổi sáng.

1. **ABC-123**: Customer reported bug
   - Severity: High
   - 💡 Tip: High = respond within 2h
   - Action: Acknowledge → Investigate → Update
```

**L3-L4:**
```markdown
## Brief - HB21373
- 3 updates (1 high)
- 1 blocker: API auth
```

---

## Session State

```javascript
// temp/bk-session-{sessionId}.json
{
  "lastProject": "HB21373",
  "lastAccess": "2026-01-31T19:44:00Z"
}
```

**Behavior:**
- On session start: Check if lastProject still exists
- If yes: "Continue with HB21373? (used 2h ago)"
- If multiple projects: Suggest lastProject first

---

## Implementation Scope

### v1.0 (Current Hooks Plan)
- Basic hooks without config
- No brseLevel
- No env persistence

### v1.1 (This Brainstorm)
- `.bk.json` config support
- brseLevel L0-L4
- Env var persistence
- Session state (last project)

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `.claude/hooks/lib/bk-config-loader.cjs` | Create | Load + merge configs |
| `.claude/hooks/lib/bk-env-writer.cjs` | Create | Write BK_* env vars |
| `.claude/hooks/brsekit-session-init.cjs` | Modify | Add config loading |
| `.claude/hooks/brsekit-subagent-init.cjs` | Modify | Read env vars |
| `.claude/skills/brsekit/SKILL.md` | Modify | Document brseLevel |

---

## Open Questions

1. How should skills access brseLevel? (env var vs config read)
2. Should brseLevel affect skill logic or just output formatting?
3. Backward compatibility: What if .bk.json doesn't exist?

---

## Next Steps

1. Complete v1.0 hooks implementation first
2. Create separate plan for Config System (v1.1)
3. Research codingLevel implementation in ClaudeKit for reference

---

## References

- [ClaudeKit Hooks Analysis](../260131-1928-brsekit-hooks-implementation/research/researcher-claudekit-hooks-analysis.md)
- [BrseKit Hooks Plan](../260131-1928-brsekit-hooks-implementation/plan.md)
- [ClaudeKit ck-config-utils.cjs](.claude/hooks/lib/ck-config-utils.cjs)
