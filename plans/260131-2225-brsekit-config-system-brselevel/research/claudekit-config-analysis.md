# ClaudeKit Config System Analysis

**Date:** 2026-01-31
**Purpose:** Reference for BrseKit v1.1 config system

---

## Config File Locations

| Type | Path | Purpose |
|------|------|---------|
| Global | `~/.claude/.ck.json` | User preferences |
| Local | `.claude/.ck.json` | Project overrides |

---

## Cascading Logic

```
DEFAULT_CONFIG (hardcoded)
    ↓ deepMerge
~/.claude/.ck.json (global)
    ↓ deepMerge
.claude/.ck.json (local)
    = Final Config
```

**Rule:** Later overrides earlier. Arrays replaced entirely (not concatenated).

---

## Key Functions (ck-config-utils.cjs)

### loadConfig()
- Loads both global + local configs
- Merges with deepMerge()
- Sanitizes paths for security

### writeEnv(envFile, key, value)
- Writes to CLAUDE_ENV_FILE
- Escapes shell special chars
- Format: `export KEY="value"`

### Session State
```javascript
getSessionTempPath(sessionId) // → /tmp/ck-session-{sessionId}.json
readSessionState(sessionId)   // → { activePlan, timestamp, ... }
writeSessionState(sessionId, state) // Atomic write with rename
```

---

## codingLevel Implementation

```javascript
// Config
{ "codingLevel": 2 }  // 0-5 scale, -1 = disabled

// Env var
writeEnv(envFile, 'CK_CODING_LEVEL', codingLevel);
writeEnv(envFile, 'CK_CODING_LEVEL_STYLE', getCodingLevelStyleName(codingLevel));

// Guidelines injected via session-init.cjs
const guidelines = getCodingLevelGuidelines(codingLevel);
if (guidelines) console.log(guidelines);
```

---

## Env Vars Written by session-init.cjs

| Var | Example |
|-----|---------|
| CK_SESSION_ID | abc123 |
| CK_ACTIVE_PLAN | plans/260131-... |
| CK_REPORTS_PATH | c:/path/plans/reports/ |
| CK_CODING_LEVEL | 2 |
| CK_PROJECT_TYPE | nodejs |
| CK_PACKAGE_MANAGER | npm |

---

## Hooks Toggle Pattern

```json
// .ck.json
{
  "hooks": {
    "session-init": true,
    "privacy-block": false
  }
}
```

```javascript
// isHookEnabled() returns true if undefined (default enabled)
if (!isHookEnabled('session-init')) process.exit(0);
```

---

## Key Takeaways for BrseKit v1.1

1. **Use same cascading pattern**: global → project
2. **Use writeEnv()** for CLAUDE_ENV_FILE persistence
3. **brseLevel** should work like codingLevel (0-4 scale)
4. **Session state** uses temp files keyed by sessionId
5. **Hooks toggle** via hooks object in config

