# Claude Hooks Environment Variable Persistence Research

**Date:** 2026-01-31
**Status:** Complete
**Token Budget:** 5/5 tool calls used

---

## Executive Summary

Claude Code hooks execute in isolated processes with NO built-in persistence across sessions. Environment variables must be explicitly managed via:
1. **Process.env cascade** (read-only, set before Claude starts)
2. **External .env files** (read via hooks)
3. **Temp files** (session state, deleted on process exit)
4. **Vault/Config directories** (permanent storage)

---

## Current BrseKit Hooks Implementation

### Session Init Hook (`brsekit-session-init.cjs`)

**Trigger:** SessionStart (startup, resume, clear, compact)
**Purpose:** Display project status & env var availability
**Output:** Console.log (no persistence written)

**Key Functions:**
- `scanProjectsDir()` - Lists projects in `projects/` directory
- `checkEnvVars()` - Boolean flags only (SECURITY: never expose values)
- `formatEnvStatus()` - Compact display format

**Design Pattern:** Fail-open (always exit 0, never block Claude)

### Subagent Init Hook (`brsekit-subagent-init.cjs`)

**Trigger:** SubagentStart (when Task tool spawns subagent)
**Purpose:** Inject minimal project context via hookSpecificOutput JSON
**Output:** `{ hookSpecificOutput: { hookEventName: 'SubagentStart', additionalContext: '...' } }`

**Key Functions:**
- `resolveProject()` - Auto-select single project or return error
- `getVaultPath()` - Return `projects/{projectName}/vault/`
- `getGlossaryPath()` - Return glossary.json if exists

**Context Injection:** ~40 tokens in additionalContext (efficient, focused)

---

## Environment Variable Handling Patterns

### 1. Env Var Checking (`checkEnvVars()`)

```javascript
const ENV_VARS = ['BACKLOG_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL'];

function checkEnvVars() {
  return Object.fromEntries(
    ENV_VARS.map((key) => [key, !!process.env[key]])
  );
}
```

**Important:** Returns BOOLEAN FLAGS ONLY - NEVER exposes actual values. This prevents accidental credential leakage in hook output.

### 2. Env Cascade Pattern

From notification hooks README (`.claude/hooks/docs/README.md`):

```
Env Cascade: process.env > ~/.claude/.env > .claude/.env
```

**Precedence:**
1. `process.env` (CLI-set variables, highest priority)
2. `~/.claude/.env` (User home directory, persistent across sessions)
3. `.claude/.env` (Project directory, committed to git)

**Setup Example:**
```bash
cp .claude/hooks/notifications/.env.example ~/.claude/.env
# Edit ~/.claude/.env with credentials
```

### 3. Env Loader Implementation

Notification hooks use `lib/env-loader.cjs` to load .env files:
- Reads from user home directory (`~/.claude/.env`)
- Falls back to project `.claude/.env`
- Merges with existing `process.env`
- Non-blocking (always exits 0)

---

## Persistence Mechanisms Available

### ✓ Working: Env Vars + Process.env Cascade
- Set vars in `~/.claude/.env` (persists across sessions)
- Hooks read via `process.env` (available in hooks & subagents)
- BrseKit uses: `BACKLOG_API_KEY`, `GEMINI_API_KEY`, `SLACK_WEBHOOK_URL`

### ✓ Working: Vault/Config Directories
- Permanent storage at `projects/{projectName}/vault/`
- Subagent hook returns vault path in context
- Subagents can read/write files in vault
- Persists across sessions automatically

### ✓ Working: Temp Files + Throttle Patterns
- Example: `/tmp/ck-noti-throttle.json` (5-minute quiet period)
- Notification hooks write throttle state to temp files
- Pattern: Write temp files within hook, read in next hook invocation
- Limited scope (single process, may not survive across sessions)

### ✗ NOT Working: In-Process Variables
- Hook processes isolated - no shared memory with Claude or subagents
- Process.env in hook ≠ process.env in Claude session
- Must use files or vault for inter-hook communication

---

## Design Patterns for BrseKit

### Pattern 1: Env Vars for Credentials
**Use Case:** API keys, webhook URLs (secrets)

```javascript
// In hook or subagent
const apiKey = process.env.BACKLOG_API_KEY;
if (!apiKey) throw new Error('Set BACKLOG_API_KEY in ~/.claude/.env');
```

**Pros:** Secure (never logged), cascade-based, persistent
**Cons:** Requires manual setup per user/machine

### Pattern 2: Vault for Config State
**Use Case:** Project settings, user preferences (non-secret)

```javascript
// Subagent can read/write to vault
const vaultPath = 'projects/{projectName}/vault/';
const configFile = path.join(vaultPath, 'config.json');
const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
```

**Pros:** Auto-persists, version-controlled (optional), supports complex data
**Cons:** Requires vault initialization, file I/O overhead

### Pattern 3: Temp Files for Session State
**Use Case:** Transient flags, rate-limiting (within single session)

```javascript
// Hook writes throttle state
const throttleFile = '/tmp/ck-noti-throttle.json';
fs.writeFileSync(throttleFile, JSON.stringify({ lastRun: Date.now() }));

// Next hook reads state
if (fs.existsSync(throttleFile)) {
  const state = JSON.parse(fs.readFileSync(throttleFile, 'utf8'));
}
```

**Pros:** Fast, simple, no security concerns
**Cons:** Temp files may be cleaned by OS, not truly cross-session

---

## Key Constraints

| Constraint | Impact | Workaround |
|---|---|---|
| **Hook processes isolated** | No shared memory with Claude | Use env vars, files, vault |
| **No built-in persistence** | Variables lost when hook exits | Write to ~/.claude/.env or vault |
| **Security-first design** | Env values never logged | Use boolean flags in output |
| **Fail-open requirement** | Hooks must never block Claude | Always exit 0, handle errors gracefully |
| **Stdin/Stdout only** | Limited IPC with Claude | Use JSON on stdout, silent on stdin errors |

---

## Implementation Checklist for BrseKit

- [x] Session hook displays env var status (boolean flags)
- [x] Subagent hook injects vault path in additionalContext
- [x] Env cascade pattern: process.env > ~/.claude/.env > .claude/.env
- [x] Config utilities: `checkEnvVars()`, `resolveProject()`, `getVaultPath()`
- [ ] **TODO:** Document how to set env vars for users (`~/.claude/.env` setup)
- [ ] **TODO:** Implement vault initialization helper
- [ ] **TODO:** Add subagent example showing vault read/write pattern

---

## Unresolved Questions

1. **Temp file persistence:** Do temp files written by hooks survive between Claude sessions on different days?
2. **Vault initialization:** When should vault be initialized (on first project creation vs manual)?
3. **Env var migration:** How do we help users migrate from local process.env to ~/.claude/.env?
4. **Cross-session state:** Is there a better pattern than temp files for true cross-session state (besides vault)?
