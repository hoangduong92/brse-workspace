# Phase 1: Config Loader Infrastructure

## Overview

- **Priority:** P1 (foundation for all other phases)
- **Status:** pending
- **Effort:** 1h

Create `bk-config-loader.cjs` with deepMerge and cascading config loading.

## Context Links

- [ClaudeKit ck-config-utils.cjs](../../.claude/hooks/lib/ck-config-utils.cjs) - Reference implementation
- [BrseKit bk-config-utils.cjs](../../.claude/hooks/lib/bk-config-utils.cjs) - Existing utilities

## Requirements

### Functional
- Load `.bk.json` from global (`~/.claude/.bk.json`) and local (`.claude/.bk.json`)
- Merge with cascading: DEFAULT → global → local
- Arrays replaced entirely (not concatenated)
- Return merged config object

### Non-Functional
- < 50ms execution
- Fail-safe: return DEFAULT_CONFIG on any error
- No dependency on ClaudeKit code

## Config Schema

```json
{
  "brseLevel": 2,
  "hooks": {
    "session-init": true,
    "subagent-init": true
  },
  "defaults": {
    "project": "HB21373",
    "language": "vi"
  },
  "envVars": [
    "BACKLOG_API_KEY",
    "GEMINI_API_KEY",
    "SLACK_WEBHOOK_URL"
  ]
}
```

## Implementation

### File: `.claude/hooks/lib/bk-config-loader.cjs`

```javascript
/**
 * BrseKit Config Loader
 *
 * Loads .bk.json with cascading: DEFAULT → global → local
 * Independent from ClaudeKit (no imports from ck-config-utils)
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const LOCAL_CONFIG_PATH = '.claude/.bk.json';
const GLOBAL_CONFIG_PATH = path.join(os.homedir(), '.claude', '.bk.json');

const DEFAULT_CONFIG = {
  brseLevel: 2,  // Mid-level (balanced)
  hooks: {
    'session-init': true,
    'subagent-init': true
  },
  defaults: {
    project: null,
    language: 'vi'
  },
  envVars: ['BACKLOG_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL']
};

// deepMerge, loadConfigFromPath, loadConfig, isHookEnabled functions
```

## Todo List

- [ ] Create `bk-config-loader.cjs` file
- [ ] Implement `deepMerge()` function
- [ ] Implement `loadConfigFromPath()` function
- [ ] Implement `loadConfig()` with cascading
- [ ] Implement `isHookEnabled()` function
- [ ] Add JSDoc comments
- [ ] Test with missing configs (should return defaults)
- [ ] Test with partial configs (should merge correctly)

## Success Criteria

1. `loadConfig()` returns merged config from all sources
2. Missing configs handled gracefully (no errors)
3. Arrays replaced entirely during merge
4. `isHookEnabled('session-init')` returns correct boolean
5. No imports from ClaudeKit code

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| JSON parse errors | Wrap in try-catch, return DEFAULT_CONFIG |
| File not found | Return null from loadConfigFromPath |
| Invalid config values | Use defaults for missing/invalid fields |

## Next Steps

After completion:
- Phase 2 uses `loadConfig()` to get brseLevel
- Phase 3 uses config for env var list
- Phase 5 integrates into hooks
