# Phase 4: Session State

## Overview

- **Priority:** P3
- **Status:** pending
- **Effort:** 30m
- **Depends on:** Phase 1 (config loader)

Track lastProject in temp file for "Continue with X?" prompt.

## Context Links

- [ClaudeKit session state](../../.claude/hooks/lib/ck-config-utils.cjs) - Reference

## Session State Schema

```json
// temp/bk-session-{sessionId}.json
{
  "lastProject": "HB21373",
  "lastAccess": "2026-01-31T19:44:00Z"
}
```

## Requirements

### Functional
- Store lastProject when project is resolved
- Read on session start for "Continue with X?" prompt
- Include lastAccess timestamp for "used 2h ago" message

### Non-Functional
- Use OS temp directory
- Atomic write (write to tmp then rename)
- Auto-cleanup old sessions (> 7 days)

## Implementation

### Add to `bk-config-loader.cjs`

```javascript
const os = require('os');
const path = require('path');

/**
 * Get session temp file path
 * @param {string} sessionId - Session identifier
 * @returns {string} Path to session temp file
 */
function getSessionTempPath(sessionId) {
  return path.join(os.tmpdir(), `bk-session-${sessionId}.json`);
}

/**
 * Read session state from temp file
 * @param {string} sessionId - Session identifier
 * @returns {Object|null} Session state or null
 */
function readSessionState(sessionId) {
  if (!sessionId) return null;
  const tempPath = getSessionTempPath(sessionId);
  try {
    if (!fs.existsSync(tempPath)) return null;
    return JSON.parse(fs.readFileSync(tempPath, 'utf8'));
  } catch (e) {
    return null;
  }
}

/**
 * Write session state atomically
 * @param {string} sessionId - Session identifier
 * @param {Object} state - State object { lastProject, lastAccess }
 * @returns {boolean} Success status
 */
function writeSessionState(sessionId, state) {
  if (!sessionId) return false;
  const tempPath = getSessionTempPath(sessionId);
  const tmpFile = tempPath + '.' + Math.random().toString(36).slice(2);
  try {
    fs.writeFileSync(tmpFile, JSON.stringify(state, null, 2));
    fs.renameSync(tmpFile, tempPath);
    return true;
  } catch (e) {
    try { fs.unlinkSync(tmpFile); } catch (_) {}
    return false;
  }
}

/**
 * Format time ago string
 * @param {string} isoDate - ISO date string
 * @returns {string} Human-readable time ago
 */
function formatTimeAgo(isoDate) {
  const diff = Date.now() - new Date(isoDate).getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return 'just now';
  if (hours === 1) return '1h ago';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
```

## Behavior

1. **On session start:** Check if lastProject still exists
2. **If yes:** "Continue with HB21373? (used 2h ago)"
3. **If multiple projects:** Suggest lastProject first in list

## Todo List

- [ ] Implement `getSessionTempPath()` function
- [ ] Implement `readSessionState()` function
- [ ] Implement `writeSessionState()` function
- [ ] Implement `formatTimeAgo()` helper
- [ ] Export all functions
- [ ] Test read/write cycle
- [ ] Test missing session file (should return null)
- [ ] Test atomic write (temp file then rename)

## Success Criteria

1. Session state persists across hook invocations
2. Atomic write prevents corruption
3. Missing session handled gracefully
4. Time ago formatting works correctly

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Temp dir permissions | Wrap in try-catch, fail silently |
| Concurrent writes | Atomic rename prevents corruption |
| Old stale sessions | Optional cleanup (not critical) |

## Next Steps

After completion:
- Phase 5 reads/writes session state in hooks
- Future: Auto-cleanup sessions older than 7 days
