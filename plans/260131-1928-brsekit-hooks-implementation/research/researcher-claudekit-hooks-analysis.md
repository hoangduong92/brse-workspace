# ClaudeKit Hooks Implementation Analysis

## Q1: Input/Output Mechanisms

### session-init.cjs - Input (stdin)
```javascript
const stdin = fs.readFileSync(0, 'utf-8').trim();
const data = stdin ? JSON.parse(stdin) : {};
// Expects: { source: 'startup|resume|clear|compact', session_id: string }
```

### session-init.cjs - Output (stdout)
```javascript
console.log(`Session ${source}. ${buildContextOutput(...)}`);
// Also outputs context, warnings, coding level guidelines
```

### Env Var Persistence (CLAUDE_ENV_FILE)
```javascript
const envFile = process.env.CLAUDE_ENV_FILE;
writeEnv(envFile, 'CK_SESSION_ID', sessionId);
// Appends: export KEY="value\n" to env file
// Escapes: backslash, quotes, $, backticks
```

---

## Q2: session-init.cjs Flow

1. **Early exit** if hook disabled in config (line 28)
2. **Load config** from .claude/.ck.json (cascading: DEFAULT → global → local)
3. **Detect project** type, package manager, framework
4. **Resolve plan** - checks session state → branch match → (mostRecent removed)
5. **Compute naming pattern** - date + issue + {slug}
6. **Write env vars** (~40 vars: paths, git info, project type, etc.)
7. **Output context** - session info + guidelines + coding level rules
8. **Fail-safe exit(0)** - non-blocking (always succeeds)

---

## Q3: subagent-init.cjs Flow

Fires on SubagentStart (when Task tool spawns subagent).

**Input payload:**
```javascript
{ agent_type, agent_id, cwd, session_id }
```

**Output format (CRITICAL):**
```javascript
{
  hookSpecificOutput: {
    hookEventName: "SubagentStart",
    additionalContext: "... markdown context ..."
  }
}
```

**Context injection (~200 tokens):**
- Subagent ID & CWD
- Plan + task list ID
- Language config (thinking + response)
- Rules (YAGNI/KISS/DRY + Python venv)
- Naming templates (report + plan dir)
- Trust verification (if enabled)
- Agent-specific context

**Key difference from session-init:**
- Uses `payload.cwd` to resolve git paths (monorepo support)
- Returns JSON with hookSpecificOutput wrapper
- Minimal context (200 tokens vs 350)

---

## Q4: ck-config-utils.cjs Structure

**800+ lines, modular sections:**

### Config Loading (lines 12-540)
- `loadConfig()` - cascading merge DEFAULT → global → local
- `sanitizeConfig()` - path validation, prevent escape attacks
- `deepMerge()` - recursive object merge

### Path/Slug Utils (lines 166-361)
- `sanitizeSlug()` - remove invalid filename chars, limit length
- `extractSlugFromBranch()` - regex pattern matching
- `normalizePath()` - trim, remove trailing slashes
- `sanitizePath()` - prevent path traversal

### Plan Resolution (lines 292-338)
```javascript
function resolvePlanPath(sessionId, config) {
  // Resolution order: 'session' (temp file) → 'branch' (git match)
  // Returns: { path, resolvedBy }
}
```

### Environment Handling (lines 556-563)
```javascript
function writeEnv(envFile, key, value) {
  fs.appendFileSync(envFile, `export ${key}="${escapeShellValue(value)}"\n`);
}
```

### Naming Pattern Resolution (lines 695-734)
```javascript
function resolveNamingPattern(planConfig, gitBranch) {
  // Substitutes {date}, {issue}, keeps {slug} for agents
  // Returns: "251212-1830-GH-88-{slug}" or "251212-1830-{slug}"
}
```

---

## Q5: Hook Registration (.claude/settings.json)

**Pattern:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          { "type": "command", "command": "node path/to/hook.cjs" }
        ]
      }
    ],
    "SubagentStart": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "node path/to/hook.cjs" }
        ]
      }
    ]
  }
}
```

**Hook lifecycle events:**
- SessionStart (startup|resume|clear|compact)
- SubagentStart (all subagents)
- UserPromptSubmit (dev-rules-reminder, usage-awareness)
- PreToolUse (scout-block, privacy-block, descriptive-name)
- PostToolUse (post-edit-simplify-reminder)
- Stop, SessionEnd

---

## Q6: Key Differences (session vs subagent)

| Aspect | session-init | subagent-init |
|--------|-------------|---------------|
| **Trigger** | SessionStart (startup/resume/clear/compact) | SubagentStart (Task tool) |
| **Input** | stdin JSON with source, session_id | stdin JSON with agent_type, cwd, session_id |
| **Output** | console.log() text (context + warnings) | JSON with hookSpecificOutput.additionalContext |
| **Env vars** | ~40 vars written to CLAUDE_ENV_FILE | None (reads from env) |
| **Token size** | ~350 tokens | ~200 tokens (optimized) |
| **CWD handling** | process.cwd() for base dir | payload.cwd for monorepo support |
| **Plan resolution** | session > branch (mostRecent removed) | Same as session |
| **Fail mode** | exit(0) non-blocking | exit(0) non-blocking + JSON fail-safe |

---

## Critical Insights for BrseKit

1. **Config cascading** - DEFAULT → global (~/.claude/.ck.json) → local (.claude/.ck.json). Local overrides all.

2. **Session state** - Temp files at `os.tmpdir()/ck-session-{sessionId}.json` track active plans across sessions.

3. **Naming pattern** - Agents use env var `CK_NAME_PATTERN` (pre-resolved with date/issue) and substitute {slug}.

4. **Hook disabling** - Set `hooks.{ "hook-name": false }` in config to skip execution.

5. **Fail-safe design** - Hooks always exit(0); errors logged but never block Claude Code execution.

6. **Token efficiency** - subagent-init optimized for ~200 tokens by reusing session-computed env vars.

7. **Validation** - `validateNamingPattern()` ensures {slug} exists and no unresolved placeholders remain.

8. **Security** - Path traversal blocked (`sanitizePath()`), shell escaping in `escapeShellValue()`.

---

## Unresolved Questions

None. All hook mechanisms documented in code with clear patterns for BrseKit implementation.
