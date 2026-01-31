# Phase 4: Update settings.json with BrseKit Hooks

## Context Links

- [Current settings.json](.claude/settings.json)
- [Phase 2: Session Hook](./phase-02-session-hook.md)
- [Phase 3: Subagent Hook](./phase-03-subagent-hook.md)

## Overview

| Priority | Status | Effort |
|----------|--------|--------|
| P1 | pending | 15m |

Add BrseKit hooks to `.claude/settings.json`. Hooks run AFTER ClaudeKit hooks (order in array).

## Key Insights

1. Multiple hooks can run on same event (array of hooks)
2. Hooks execute in order defined in array
3. Use `%CLAUDE_PROJECT_DIR%` for Windows compatibility
4. BrseKit hooks should run after ClaudeKit (append to existing)

## Requirements

- Add brsekit-session-init.cjs to SessionStart hooks
- Add brsekit-subagent-init.cjs to SubagentStart hooks
- Preserve all existing ClaudeKit hooks
- Maintain JSON validity

## Related Code Files

**Modify:**
- `.claude/settings.json`

## Implementation Steps

1. Read current settings.json

2. Add BrseKit session hook to SessionStart array:
```json
{
  "type": "command",
  "command": "node \"%CLAUDE_PROJECT_DIR%\"/.claude/hooks/brsekit-session-init.cjs"
}
```

3. Add BrseKit subagent hook to SubagentStart array:
```json
{
  "type": "command",
  "command": "node \"%CLAUDE_PROJECT_DIR%\"/.claude/hooks/brsekit-subagent-init.cjs"
}
```

4. Final SessionStart section should look like:
```json
"SessionStart": [
  {
    "matcher": "startup|resume|clear|compact",
    "hooks": [
      {
        "type": "command",
        "command": "node \"%CLAUDE_PROJECT_DIR%\"/.claude/hooks/session-init.cjs"
      },
      {
        "type": "command",
        "command": "node \"%CLAUDE_PROJECT_DIR%\"/.claude/hooks/brsekit-session-init.cjs"
      }
    ]
  }
]
```

5. Final SubagentStart section should look like:
```json
"SubagentStart": [
  {
    "matcher": "*",
    "hooks": [
      {
        "type": "command",
        "command": "node \"%CLAUDE_PROJECT_DIR%\"/.claude/hooks/subagent-init.cjs"
      },
      {
        "type": "command",
        "command": "node \"%CLAUDE_PROJECT_DIR%\"/.claude/hooks/brsekit-subagent-init.cjs"
      }
    ]
  }
]
```

6. Validate JSON syntax

## Todo List

- [ ] Backup current settings.json
- [ ] Add BrseKit hook to SessionStart hooks array
- [ ] Add BrseKit hook to SubagentStart hooks array
- [ ] Validate JSON syntax
- [ ] Test Claude Code startup

## Success Criteria

1. Valid JSON after modification
2. Both ClaudeKit and BrseKit hooks fire on SessionStart
3. Both hooks fire on SubagentStart
4. No errors in Claude Code startup

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Invalid JSON | Validate before save |
| Hook order wrong | BrseKit after ClaudeKit (append) |
| Path issues on Windows | Use %CLAUDE_PROJECT_DIR% |
