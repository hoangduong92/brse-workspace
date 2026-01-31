# BrseKit Hooks Implementation - Brainstorm Summary

**Date:** 2026-01-31
**Status:** Approved for Implementation

---

## Problem Statement

Khi Claude Code khởi động, không có context về BrseKit multi-project environment:
- Không biết projects nào tồn tại
- Mỗi skill command cần `--project` flag
- Subagents không có vault/glossary paths
- Lặp lại thao tác, tốn thời gian

---

## Confirmed Requirements

| Requirement | Decision |
|-------------|----------|
| Priority | Convenience + Reliability (equal) |
| Scale | 1-3 projects (small workspace) |
| Architecture | Separate hooks (brsekit-*.cjs) |
| API Keys | Flag only (security-first) |
| Validation | Lazy (validate on skill use) |
| Persistence | No active project persistence |
| Coexistence | Independent with ClaudeKit hooks |
| Auto-select | Yes, when only 1 project |

---

## Chosen Approach: A+ (Minimal with Smart Defaults)

### Session Hook Output (~80-100 tokens)

**Case: 1 project**
```
BrseKit: Project HB21373 (auto-selected)
Env: BACKLOG_API_KEY ✓ | GEMINI_API_KEY ✓
```

**Case: Multiple projects**
```
BrseKit: 3 projects available
├── HB21373
├── HB21456
└── HB21789
⚠️ Use --project <name> with skills
Env: BACKLOG_API_KEY ✓ | GEMINI_API_KEY ✗
```

**Case: No projects**
```
BrseKit: ⚠️ No projects in projects/
Run: /bk-init to create first project
```

### Subagent Hook Output (~40 tokens)

```
BrseKit: HB21373 | vault: projects/HB21373/vault/ | glossary: ✓
```

Or if no project context:
```
BrseKit: --project not specified. Available: HB21373, HB21456, HB21789
```

### Skill Behavior (Fallback Logic)

```javascript
function resolveProject(explicitProject) {
  if (explicitProject) return explicitProject;

  const projects = scanProjectsDir();
  if (projects.length === 1) return projects[0]; // auto-select
  if (projects.length === 0) throw new Error('No projects found');

  // Multiple projects, no explicit → error with suggestions
  throw new Error(`--project required. Available: ${projects.join(', ')}`);
}
```

---

## What Hooks DO

| Action | Session Hook | Subagent Hook |
|--------|--------------|---------------|
| Scan projects/ dir | ✅ | ✅ |
| Check env vars exist | ✅ | ✅ |
| Output project list | ✅ | ✅ |
| Auto-select single project | ✅ | ✅ |
| Warn multiple projects | ✅ | ❌ |

## What Hooks DO NOT

- ❌ Read vault.db
- ❌ Read glossary.json
- ❌ Call Backlog API
- ❌ Remember "active project" across sessions
- ❌ Expose API key values

---

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

---

## Implementation Considerations

### 1. Project Detection
```javascript
// Simple directory scan
function scanProjectsDir() {
  const projectsPath = path.join(process.cwd(), 'projects');
  if (!fs.existsSync(projectsPath)) return [];
  return fs.readdirSync(projectsPath, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
}
```

### 2. Env Var Check
```javascript
// Check existence only, never expose values
function checkEnvVars() {
  return {
    BACKLOG_API_KEY: !!process.env.BACKLOG_API_KEY,
    GEMINI_API_KEY: !!process.env.GEMINI_API_KEY,
    SLACK_WEBHOOK_URL: !!process.env.SLACK_WEBHOOK_URL
  };
}
```

### 3. Settings Configuration
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup|resume|clear|compact",
      "hooks": [{ "type": "command", "command": "node .claude/hooks/brsekit-session-init.cjs" }]
    }],
    "SubagentStart": [{
      "matcher": "*",
      "hooks": [{ "type": "command", "command": "node .claude/hooks/brsekit-subagent-init.cjs" }]
    }]
  }
}
```

---

## Success Metrics

1. **Startup speed**: < 100ms for hook execution
2. **Token efficiency**: < 100 tokens session hook output
3. **Error clarity**: Helpful messages when --project missing
4. **Zero breaking changes**: Existing skills continue to work

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Slow scan with many projects | Cache project list, rescan only on explicit request |
| Hook conflicts with ClaudeKit | Separate files, independent execution |
| Wrong project auto-selected | Only auto-select when exactly 1 project |

---

## Next Steps

1. Implement `bk-config-utils.cjs` với core functions
2. Implement `brsekit-session-init.cjs`
3. Implement `brsekit-subagent-init.cjs`
4. Update `.claude/settings.json`
5. Update existing skills với `resolveProject()` logic
6. Test với multi-project setup

---

## References

- [Original Research Report](.claude/skills/brsekit/260131-brsekit-hooks-research-report.md)
- [ClaudeKit session-init.cjs](.claude/hooks/session-init.cjs)
- [ClaudeKit config utils](.claude/hooks/lib/ck-config-utils.cjs)
