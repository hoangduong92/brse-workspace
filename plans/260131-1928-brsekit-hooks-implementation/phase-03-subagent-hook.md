# Phase 3: Create brsekit-subagent-init.cjs Subagent Hook

## Context Links

- [Phase 1: Utility Lib](./phase-01-utility-lib.md) - Dependency
- [ClaudeKit subagent-init.cjs](.claude/hooks/subagent-init.cjs) - Pattern reference
- [Brainstorm](../reports/brainstorm-260131-1928-brsekit-hooks-implementation.md)

## Overview

| Priority | Status | Effort |
|----------|--------|--------|
| P2 | pending | 45m |

Create subagent hook that fires when Task tool spawns subagent. Outputs JSON with minimal context. Target: ~40 tokens.

## Key Insights

1. **CRITICAL:** Must return JSON with `hookSpecificOutput.additionalContext`
2. Uses payload.cwd for monorepo support
3. Much smaller output than session hook
4. Provides vault/glossary paths for project

## Requirements

**Input (stdin):**
```json
{ "agent_type": "researcher", "agent_id": "abc123", "cwd": "/path", "session_id": "..." }
```

**Output (stdout) - With project:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "BrseKit: HB21373 | vault: projects/HB21373/vault/ | glossary: ✓"
  }
}
```

**Output - No project context:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "BrseKit: --project not specified. Available: HB21373, HB21456"
  }
}
```

## Related Code Files

**Create:**
- `.claude/hooks/brsekit-subagent-init.cjs`

**Depend on:**
- `.claude/hooks/lib/bk-config-utils.cjs` (Phase 1)

## Implementation Steps

1. Create file `.claude/hooks/brsekit-subagent-init.cjs`

2. Add shebang and imports:
```javascript
#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { scanProjectsDir, resolveProject } = require('./lib/bk-config-utils.cjs');
```

3. Parse stdin with early exit:
```javascript
const stdin = fs.readFileSync(0, 'utf-8').trim();
if (!stdin) process.exit(0);

const payload = JSON.parse(stdin);
const effectiveCwd = payload.cwd?.trim() || process.cwd();
```

4. Resolve project context:
```javascript
const resolved = resolveProject(null, effectiveCwd);
```

5. Build context string:
```javascript
let context;
if (typeof resolved === 'string') {
  // Single project auto-selected
  const vaultPath = `projects/${resolved}/vault/`;
  const glossaryExists = fs.existsSync(path.join(effectiveCwd, `projects/${resolved}/glossary.json`));
  context = `BrseKit: ${resolved} | vault: ${vaultPath} | glossary: ${glossaryExists ? '✓' : '✗'}`;
} else if (resolved.error === 'NO_PROJECTS') {
  context = `BrseKit: No projects configured`;
} else {
  // Multiple projects, no explicit selection
  context = `BrseKit: --project not specified. Available: ${resolved.available.join(', ')}`;
}
```

6. Output JSON:
```javascript
const output = {
  hookSpecificOutput: {
    hookEventName: "SubagentStart",
    additionalContext: context
  }
};
console.log(JSON.stringify(output));
```

7. Wrap in try-catch, always exit(0)

## Todo List

- [ ] Create brsekit-subagent-init.cjs
- [ ] Parse stdin with early exit
- [ ] Get effectiveCwd from payload
- [ ] Resolve project (auto-select if 1)
- [ ] Check glossary.json existence
- [ ] Build context string
- [ ] Output JSON with hookSpecificOutput wrapper
- [ ] Wrap in try-catch with exit(0)

## Success Criteria

1. Output < 40 tokens in additionalContext
2. Valid JSON output with hookSpecificOutput wrapper
3. Never blocks subagent start (always exit 0)
4. Provides vault path when project resolved

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Invalid JSON output | Use JSON.stringify() |
| Missing payload.cwd | Fallback to process.cwd() |
| Glossary check slow | fs.existsSync() is fast enough |
