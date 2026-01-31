# Phase 2: Create brsekit-session-init.cjs Session Hook

## Context Links

- [Phase 1: Utility Lib](./phase-01-utility-lib.md) - Dependency
- [ClaudeKit session-init.cjs](.claude/hooks/session-init.cjs) - Pattern reference
- [Brainstorm](../reports/brainstorm-260131-1928-brsekit-hooks-implementation.md)

## Overview

| Priority | Status | Effort |
|----------|--------|--------|
| P1 | pending | 1h |

Create session hook that fires on startup/resume/clear/compact. Outputs project list + env status. Target: ~80-100 tokens output.

## Key Insights

1. console.log() for output (not JSON like subagent)
2. Always exit(0) - fail-open design
3. No env var persistence needed (simpler than ClaudeKit)
4. Different output for 0/1/N projects scenarios

## Requirements

**Input (stdin):**
```json
{ "source": "startup|resume|clear|compact", "session_id": "..." }
```

**Output (stdout) - Case 1 project:**
```
BrseKit: Project HB21373 (auto-selected)
Env: API_KEY ✓ | GEMINI_KEY ✓
```

**Output - Multiple projects:**
```
BrseKit: 3 projects available
├── HB21373
├── HB21456
└── HB21789
⚠️ Use --project <name> with skills
Env: API_KEY ✓ | GEMINI_KEY ✗
```

**Output - No projects:**
```
BrseKit: ⚠️ No projects in projects/
Run: /bk-init to create first project
```

## Related Code Files

**Create:**
- `.claude/hooks/brsekit-session-init.cjs`

**Depend on:**
- `.claude/hooks/lib/bk-config-utils.cjs` (Phase 1)

## Implementation Steps

1. Create file `.claude/hooks/brsekit-session-init.cjs`

2. Add shebang and imports:
```javascript
#!/usr/bin/env node
const fs = require('fs');
const { scanProjectsDir, checkEnvVars, formatEnvStatus } = require('./lib/bk-config-utils.cjs');
```

3. Parse stdin:
```javascript
const stdin = fs.readFileSync(0, 'utf-8').trim();
const data = stdin ? JSON.parse(stdin) : {};
const source = data.source || 'unknown';
```

4. Scan projects + check env:
```javascript
const projects = scanProjectsDir();
const envVars = checkEnvVars();
const envStatus = formatEnvStatus(envVars);
```

5. Output based on project count:
```javascript
if (projects.length === 0) {
  console.log(`BrseKit: ⚠️ No projects in projects/`);
  console.log(`Run: /bk-init to create first project`);
} else if (projects.length === 1) {
  console.log(`BrseKit: Project ${projects[0]} (auto-selected)`);
  console.log(`Env: ${envStatus}`);
} else {
  console.log(`BrseKit: ${projects.length} projects available`);
  projects.forEach((p, i) => {
    const prefix = i === projects.length - 1 ? '└──' : '├──';
    console.log(`${prefix} ${p}`);
  });
  console.log(`⚠️ Use --project <name> with skills`);
  console.log(`Env: ${envStatus}`);
}
```

6. Wrap in try-catch, always exit(0)

## Todo List

- [ ] Create brsekit-session-init.cjs
- [ ] Add stdin parsing
- [ ] Import utility functions
- [ ] Handle 0 projects case
- [ ] Handle 1 project case (auto-select)
- [ ] Handle N projects case (list + warning)
- [ ] Add env status line
- [ ] Wrap in try-catch with exit(0)

## Success Criteria

1. Output < 100 tokens
2. Execution < 100ms
3. Never blocks Claude startup (always exit 0)
4. Clear guidance when --project needed

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Slow scan with many projects | Only list first level, no deep scan |
| Hook crash | try-catch + exit(0) fail-safe |
