# Phase 3: Env Persistence

## Overview

- **Priority:** P2
- **Status:** pending
- **Effort:** 30m
- **Depends on:** Phase 1 (config loader)

Write BK_* env vars to CLAUDE_ENV_FILE for skills and bash commands.

## Context Links

- [ClaudeKit writeEnv()](../../.claude/hooks/lib/ck-config-utils.cjs) - Reference

## Env Vars to Write

| Var | Purpose | Example |
|-----|---------|---------|
| `BK_BRSE_LEVEL` | Output verbosity | `2` |
| `BK_PROJECTS_PATH` | Projects directory | `projects` |
| `BK_ACTIVE_PROJECT` | Current project | `HB21373` |
| `BK_VAULT_PATH` | Project vault | `projects/HB21373/vault/` |
| `BK_GLOSSARY_PATH` | Project glossary | `projects/HB21373/glossary.json` |

## Requirements

### Functional
- Write to CLAUDE_ENV_FILE (from process.env)
- Escape shell special chars in values
- Only write if CLAUDE_ENV_FILE is set

### Non-Functional
- Append mode (don't overwrite existing vars)
- Handle missing values gracefully (skip)

## Implementation

### File: `.claude/hooks/lib/bk-env-writer.cjs`

```javascript
/**
 * BrseKit Env Writer
 *
 * Writes BK_* env vars to CLAUDE_ENV_FILE
 * Independent from ClaudeKit (no imports from ck-config-utils)
 */

const fs = require('fs');

/**
 * Escape shell special characters for env file values
 * Handles: backslash, double quote, dollar sign, backtick
 */
function escapeShellValue(str) {
  if (typeof str !== 'string') return String(str);
  return str
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\$/g, '\\$')
    .replace(/`/g, '\\`');
}

/**
 * Write env var to CLAUDE_ENV_FILE
 * @param {string} key - Env var name
 * @param {string|number} value - Env var value
 */
function writeEnv(key, value) {
  const envFile = process.env.CLAUDE_ENV_FILE;
  if (!envFile || value === null || value === undefined) return;

  const escaped = escapeShellValue(String(value));
  fs.appendFileSync(envFile, `export ${key}="${escaped}"\n`);
}

/**
 * Write all BrseKit env vars
 * @param {Object} vars - Object with var names and values
 */
function writeBkEnvVars(vars) {
  Object.entries(vars).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      writeEnv(key, value);
    }
  });
}

module.exports = { escapeShellValue, writeEnv, writeBkEnvVars };
```

## Todo List

- [ ] Create `bk-env-writer.cjs` file
- [ ] Implement `escapeShellValue()` function
- [ ] Implement `writeEnv()` function
- [ ] Implement `writeBkEnvVars()` helper
- [ ] Test with special chars in values
- [ ] Test when CLAUDE_ENV_FILE not set (should skip)
- [ ] Test null/undefined values (should skip)

## Success Criteria

1. `writeEnv('BK_LEVEL', 2)` appends `export BK_LEVEL="2"` to env file
2. Shell special chars escaped correctly
3. No errors when CLAUDE_ENV_FILE not set
4. Null/undefined values skipped

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| CLAUDE_ENV_FILE not set | Check before writing, skip if missing |
| Write permissions | Wrap in try-catch, fail silently |
| Special chars break shell | Escape all shell-sensitive chars |

## Next Steps

After completion:
- Phase 5 calls writeBkEnvVars() from session-init hook
- Skills read BK_* vars from environment
