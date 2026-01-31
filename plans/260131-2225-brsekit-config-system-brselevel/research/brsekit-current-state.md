# BrseKit Hooks Current State (v1.0)

**Date:** 2026-01-31
**Purpose:** Document current implementation before v1.1 upgrade

---

## Files

| File | Purpose |
|------|---------|
| `brsekit-session-init.cjs` | Display project status on startup |
| `brsekit-subagent-init.cjs` | Inject project context to subagents |
| `lib/bk-config-utils.cjs` | Shared utilities |

---

## bk-config-utils.cjs Functions

```javascript
scanProjectsDir(basePath)     // → ['HB21373', 'HB21456']
checkEnvVars()                // → { BACKLOG_API_KEY: true, ... }
resolveProject(explicit, base) // → 'HB21373' or { error: 'MULTIPLE_PROJECTS', available: [...] }
formatEnvStatus(envVars)      // → 'API_KEY: ✓ | GEMINI_KEY: ✗'
getVaultPath(project, base)   // → 'projects/HB21373/vault/'
getGlossaryPath(project, base) // → 'projects/HB21373/glossary.json' or null
```

---

## brsekit-session-init.cjs Output

**Single project:**
```
BrseKit: Project HB21373 (auto-selected)
Env: API_KEY: ✓ | GEMINI_KEY: ✗ | WEBHOOK_URL: ✗
```

**Multiple projects:**
```
BrseKit: 2 projects available
├── HB21373
└── HB21456
⚠️ Use --project <name> with skills
Env: API_KEY: ✓ | GEMINI_KEY: ✗ | WEBHOOK_URL: ✗
```

---

## brsekit-subagent-init.cjs Output

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "BrseKit: HB21373 | vault: projects/HB21373/vault/ | glossary: projects/HB21373/glossary.json"
  }
}
```

---

## What's Missing (v1.1 Gaps)

| Feature | Current | Target |
|---------|---------|--------|
| Config file | ❌ None | `.bk.json` cascading |
| brseLevel | ❌ None | L0-L4 system |
| Env persistence | ❌ Display only | Write BK_* to CLAUDE_ENV_FILE |
| Session state | ❌ None | Track lastProject |
| Default project | ❌ None | From config |
| Workflow suggestions | ❌ None | Proactive for L0-L1 |

---

## Constraints

1. **Independence**: BrseKit hooks must not depend on ClaudeKit code
2. **Fail-safe**: Always exit 0, never block Claude
3. **Fast**: < 50ms execution
4. **Security**: Never expose env var values

