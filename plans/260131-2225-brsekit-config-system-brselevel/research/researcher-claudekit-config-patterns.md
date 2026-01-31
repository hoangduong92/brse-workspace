# ClaudeKit Config System & codingLevel Feature Research

**Date:** 2026-01-31 | **Author:** Researcher | **Max Lines:** 150

## Executive Summary

ClaudeKit (ck-config-utils.cjs) implements a cascading config system supporting global→project overrides. The `codingLevel` feature (-1 to 5) controls coding guideline injection: `-1=disabled`, `0-5=inject corresponding guidelines`. Config persists via JSON files and env vars are written atomically with shell escaping.

---

## 1. Config Loading Architecture

### Cascading Precedence (Lowest → Highest)
1. **DEFAULT_CONFIG** (hardcoded fallback)
2. **GLOBAL_CONFIG** (~/.claude/.ck.json) - user preferences
3. **LOCAL_CONFIG** (./.claude/.ck.json) - project overrides

### Deep Merge Strategy
```javascript
deepMerge(target, source) // source wins
// Arrays: replaced entirely (not concatenated)
// Objects: recursed (but not null)
// Primitives: source overrides target
```

### File Locations
- Local: `./.claude/.ck.json` (project-specific)
- Global: `~/.claude/.ck.json` (user home directory)

---

## 2. codingLevel Feature

### Design
- **Range:** -1 to 5 (default: -1)
- **-1:** Disabled (no injection, saves tokens)
- **0-5:** Inject corresponding level guidelines
- **Purpose:** Control coding output style/quality guidelines per session

### Config Resolution
```javascript
result.codingLevel = merged.codingLevel ?? -1;
// ck-config-utils.cjs line 504
```

### Default Behavior
When no config exists, `getDefaultConfig()` returns `codingLevel: -1` (disabled by default to conserve tokens).

---

## 3. Session State Management

### Temporary Storage
- **Path:** `$TMPDIR/ck-session-{sessionId}.json`
- **Purpose:** Store session-specific overrides (activePlan, etc.)
- **Lifecycle:** Atomic writes with temp file + rename pattern

```javascript
writeSessionState(sessionId, state) {
  // 1. Write to temp file: {path}.{random}
  // 2. Rename atomically to final path
  // 3. Fail-safe cleanup on error
}
```

---

## 4. Plan Resolution with Tracking

### Resolution Order
1. **session** - Explicitly set via set-active-plan.cjs → ACTIVE (directive)
2. **branch** - Matched from git branch → SUGGESTED (hint only, no pollution)
3. ~~mostRecent~~ - REMOVED (was causing stale plan pollution)

### Return Value
```javascript
{ path: string|null, resolvedBy: 'session'|'branch'|null }
```

### Key Insight: session-resolved vs branch-matched
- **Session resolved:** Use plan-specific reports path
- **Branch matched:** Use default reports path (prevents stale plan pollution)

---

## 5. Environment Variable Writing

### Escape Security
```javascript
escapeShellValue(str) {
  // Escapes: \, ", $, `
  // Prevents command injection in shell
}
writeEnv(envFile, key, value) {
  // Appends: export KEY="escaped_value"\n
}
```

### Usage Pattern
Environment variables written to `CLAUDE_ENV_FILE` (provided by Claude runtime).

---

## 6. Path Sanitization & Validation

### Slug Sanitization
- Removes invalid filename chars: `< > : " / \ | ? * \x00-\x1f`
- Replaces non-alphanumeric (except hyphen) with hyphen
- Collapses multiple hyphens
- Max 100 characters

### Path Validation
- Prevents path traversal (`../` attacks)
- Allows absolute paths (consolidated plans feature)
- Blocks null bytes
- Validates relative paths stay within project

---

## 7. Reports Path Resolution

### Logic
```javascript
getReportsPath(planPath, resolvedBy, planConfig, pathsConfig) {
  // If session-resolved: {planPath}/{reportsDir}/
  // Otherwise: {plansDir}/{reportsDir}/
}
```

**Design Decision:** Only session-resolved plans use their custom reports path. Branch-matched plans use default to avoid clutter.

---

## 8. BrseKit Integration (bk-config-utils.cjs)

### Multi-Project Support
- `scanProjectsDir()` - Lists projects/ folders
- `resolveProject()` - Auto-select single or error on multiple
- `checkEnvVars()` - Returns boolean flags (never exposes values)

### Environment Checks
- `BACKLOG_API_KEY`, `GEMINI_API_KEY`, `SLACK_WEBHOOK_URL`
- Security-first: Only flags, never values

---

## Key Patterns

| Pattern | Implementation | Purpose |
|---------|---|---|
| **Cascading Config** | DEFAULT → global → local merge | Project overrides user prefs |
| **Atomic Writes** | Temp file + rename | Prevent corruption |
| **Shell Escaping** | 4-char escape set | Prevent injection |
| **Fail-Safe** | Try-catch, return null/default | Never block startup |
| **Plan Tracking** | resolvedBy field | Distinguish active vs suggested |

---

## Unresolved Questions

1. How does codingLevel (-1 to 5) map to actual guideline injection in hooks/runtime?
2. Where is CLAUDE_ENV_FILE environment variable set in Claude runtime?
3. How does session state survive across agent spawning (subagents)?
