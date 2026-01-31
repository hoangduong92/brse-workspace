# Phase 5: Hook Integration

## Overview

- **Priority:** P1
- **Status:** pending
- **Effort:** 1h
- **Depends on:** Phase 1-4

Integrate config, brseLevel, env persistence, and session state into hooks.

## Context Links

- [brsekit-session-init.cjs](../../.claude/hooks/brsekit-session-init.cjs)
- [brsekit-subagent-init.cjs](../../.claude/hooks/brsekit-subagent-init.cjs)

## Files to Modify

| File | Changes |
|------|---------|
| `brsekit-session-init.cjs` | Load config, write env vars, inject guidelines |
| `brsekit-subagent-init.cjs` | Read env vars instead of recomputing paths |
| `SKILL.md` | Document brseLevel system |

## Implementation

### brsekit-session-init.cjs

```javascript
const {
  loadConfig,
  isHookEnabled,
  getBrseLevelGuidelines,
  readSessionState,
  writeSessionState
} = require('./lib/bk-config-loader.cjs');
const { writeBkEnvVars } = require('./lib/bk-env-writer.cjs');
const { scanProjectsDir, resolveProject, ... } = require('./lib/bk-config-utils.cjs');

function main() {
  // Check if hook is enabled
  if (!isHookEnabled('session-init')) {
    process.exit(0);
  }

  // Load config
  const config = loadConfig();
  const brseLevel = config.brseLevel ?? 2;

  // Parse stdin for sessionId
  const stdin = parseStdin();
  const sessionId = stdin?.sessionId;

  // Check session state for lastProject
  const sessionState = readSessionState(sessionId);

  // Resolve project (with default from config)
  const defaultProject = config.defaults?.project;
  const projects = scanProjectsDir();
  const resolved = resolveProject(defaultProject);

  // Build env vars
  const envVars = {
    BK_BRSE_LEVEL: brseLevel,
    BK_PROJECTS_PATH: 'projects',
    BK_ACTIVE_PROJECT: typeof resolved === 'string' ? resolved : null,
    BK_VAULT_PATH: typeof resolved === 'string' ? getVaultPath(resolved) : null,
    BK_GLOSSARY_PATH: typeof resolved === 'string' ? getGlossaryPath(resolved) : null
  };

  // Write to CLAUDE_ENV_FILE
  writeBkEnvVars(envVars);

  // Output project status (existing logic)
  outputProjectStatus(projects, resolved);

  // Inject brseLevel guidelines
  const guidelines = getBrseLevelGuidelines(brseLevel);
  if (guidelines) {
    console.log(guidelines);
  }

  // Update session state
  if (sessionId && typeof resolved === 'string') {
    writeSessionState(sessionId, {
      lastProject: resolved,
      lastAccess: new Date().toISOString()
    });
  }
}
```

### brsekit-subagent-init.cjs

```javascript
// BEFORE: Recompute paths every time
const resolved = resolveProject(null, effectiveCwd);
const vaultPath = getVaultPath(resolved, effectiveCwd);

// AFTER: Read from env vars if available
const activeProject = process.env.BK_ACTIVE_PROJECT;
const vaultPath = process.env.BK_VAULT_PATH;
const glossaryPath = process.env.BK_GLOSSARY_PATH;

if (activeProject && vaultPath) {
  // Use env vars (faster, no disk scan)
  context = `BrseKit: ${activeProject} | vault: ${vaultPath} | glossary: ${glossaryPath || 'none'}`;
} else {
  // Fallback to existing logic
  const resolved = resolveProject(null, effectiveCwd);
  // ... existing code
}
```

### SKILL.md Updates

Add section:
```markdown
## brseLevel System

| Level | Name | Verbosity |
|-------|------|-----------|
| L0 | Intern | Very detailed |
| L1 | Junior | Detailed |
| L2 | Mid | Balanced (default) |
| L3 | Senior | Concise |
| L4 | Lead | Raw/compact |

Configure in `.claude/.bk.json`:
```json
{ "brseLevel": 2 }
```
```

## Todo List

- [ ] Update session-init: import from bk-config-loader
- [ ] Update session-init: check isHookEnabled()
- [ ] Update session-init: load config and get brseLevel
- [ ] Update session-init: call writeBkEnvVars()
- [ ] Update session-init: inject guidelines
- [ ] Update session-init: read/write session state
- [ ] Update subagent-init: read from env vars first
- [ ] Update subagent-init: fallback to existing logic
- [ ] Update SKILL.md: document brseLevel
- [ ] Test full flow with .bk.json present
- [ ] Test full flow without .bk.json (defaults)

## Success Criteria

1. Session-init outputs brseLevel guidelines
2. BK_* env vars written to CLAUDE_ENV_FILE
3. Subagent-init uses env vars when available
4. Session state persists lastProject
5. Hook disabled when `hooks.session-init: false`
6. SKILL.md documents brseLevel

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking existing behavior | Test with and without config |
| Performance regression | Measure execution time (< 50ms) |
| Env vars not available | Fallback to existing logic |

## Security Considerations

- Never log env var values (security)
- Sanitize paths from config (prevent traversal)
- Escape shell chars in env values

## Next Steps

After completion:
- Skills can read BK_BRSE_LEVEL for output formatting
- Users can configure brseLevel in .bk.json
- Session remembers lastProject
