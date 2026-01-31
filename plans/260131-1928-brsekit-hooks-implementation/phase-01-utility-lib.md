# Phase 1: Create bk-config-utils.cjs Utility Library

## Context Links

- [ClaudeKit ck-config-utils.cjs](.claude/hooks/lib/ck-config-utils.cjs) - Reference pattern
- [Brainstorm](../reports/brainstorm-260131-1928-brsekit-hooks-implementation.md)

## Overview

| Priority | Status | Effort |
|----------|--------|--------|
| P1 | pending | 1h |

Create shared utility library with core functions: `scanProjectsDir()`, `checkEnvVars()`, `resolveProject()`. Follows ClaudeKit pattern but independent codebase.

## Key Insights

1. Simple directory scan - no need for deep file reads
2. Env check returns boolean flags only (security-first)
3. Auto-select when exactly 1 project
4. Error with suggestions when multiple projects + no explicit

## Requirements

**Functional:**
- `scanProjectsDir()` - returns array of project names
- `checkEnvVars()` - returns object with boolean flags
- `resolveProject(explicit)` - returns project name or throws

**Non-functional:**
- < 50ms execution time
- No external dependencies (pure Node.js)
- Fail-safe (always exit 0, never block Claude)

## Related Code Files

**Create:**
- `.claude/hooks/lib/bk-config-utils.cjs`

**Reference (read only):**
- `.claude/hooks/lib/ck-config-utils.cjs`

## Implementation Steps

1. Create file `.claude/hooks/lib/bk-config-utils.cjs`

2. Implement `scanProjectsDir()`:
```javascript
function scanProjectsDir(basePath = process.cwd()) {
  const projectsPath = path.join(basePath, 'projects');
  if (!fs.existsSync(projectsPath)) return [];
  return fs.readdirSync(projectsPath, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);
}
```

3. Implement `checkEnvVars()`:
```javascript
const ENV_VARS = ['BACKLOG_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL'];

function checkEnvVars() {
  return Object.fromEntries(
    ENV_VARS.map(key => [key, !!process.env[key]])
  );
}
```

4. Implement `resolveProject(explicit)`:
```javascript
function resolveProject(explicitProject, basePath = process.cwd()) {
  if (explicitProject) return explicitProject;

  const projects = scanProjectsDir(basePath);
  if (projects.length === 1) return projects[0];
  if (projects.length === 0) return { error: 'NO_PROJECTS' };
  return { error: 'MULTIPLE_PROJECTS', available: projects };
}
```

5. Implement `formatEnvStatus()`:
```javascript
function formatEnvStatus(envVars) {
  return Object.entries(envVars)
    .map(([k, v]) => `${k.replace(/_/g, '_').split('_').slice(-2).join('_')}: ${v ? '✓' : '✗'}`)
    .join(' | ');
}
```

6. Export all functions

## Todo List

- [ ] Create bk-config-utils.cjs file
- [ ] Implement scanProjectsDir()
- [ ] Implement checkEnvVars()
- [ ] Implement resolveProject()
- [ ] Implement formatEnvStatus()
- [ ] Add module.exports

## Success Criteria

1. `scanProjectsDir()` returns [] when projects/ missing
2. `scanProjectsDir()` returns project names (not paths)
3. `checkEnvVars()` never exposes actual values
4. `resolveProject()` auto-selects when 1 project
5. `resolveProject()` returns error object when multiple

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| projects/ dir doesn't exist | Return empty array, don't throw |
| Large number of projects | Only list dir names (no deep scan) |
