# Phase 4: cc-memory Integration

## Priority: P2
## Status: pending
## Effort: 2h

## Overview

Integrate cc-memory as first-class skill in BrseKit, keeping user-level storage separate from project vaults.

## Key Insights

- cc-memory uses `~/claude_client/memory/vault.db` - user-level storage
- This is intentional - memories span projects and workspaces
- Should NOT be scoped to projects
- Configure conversation-history path to `memory/conversation-history/`

## Requirements

### Functional
- cc-memory works out of the box in BrseKit
- Memory storage remains at user-level (`~/claude_client/memory/`)
- Conversation archives go to `memory/conversation-history/`
- Hooks auto-save sessions on exit

### Non-functional
- No changes to cc-memory core logic
- Configuration via CLAUDE.md or hooks
- Graceful degradation if embedder unavailable

## Architecture

```
User Home (~/)
└── claude_client/
    └── memory/
        ├── vault.db           # Facts, sessions (user-level)
        └── conversations/
            └── archives/      # Archived transcripts

Workspace
└── memory/
    └── conversation-history/  # Symlink or local archive
```

## Implementation Steps

### 1. Verify cc-memory skill structure

Current files at `.claude/skills/cc-memory/`:
```
cc-memory/
├── SKILL.md
└── scripts/
    ├── __init__.py
    ├── config_manager.py
    ├── fact_extractor.py
    ├── main.py
    ├── memory_db.py
    └── memory_store.py
```

No changes needed to core scripts - they already use `~/claude_client/memory/`.

### 2. Create memory directory structure

```bash
# Create workspace memory dir for local archives (optional)
mkdir -p memory/conversation-history
```

### 3. Update SKILL.md for BrseKit integration

```markdown
# cc-memory

User-level memory for Claude Code sessions.

## Usage

```bash
# Search facts across all sessions
/cc-memory search "project deadline"

# List recent sessions
/cc-memory recent 10

# Add manual fact
/cc-memory add "Project HB21373 uses Nuxt 3"

# Show status
/cc-memory status

# Save current session (manual)
/cc-memory save
```

## Integration with BrseKit

cc-memory operates at USER level, not project level. Facts span all projects.

To find project-specific context, use `/bk-recall search` instead.

## Auto-save with Hooks

Add to `.claude/hooks/session-end.cjs`:

```javascript
// Archive session on exit
const { execSync } = require('child_process');
const sessionId = process.env.CLAUDE_SESSION_ID;
const transcript = process.env.CLAUDE_TRANSCRIPT_PATH;
const workspace = process.cwd();

if (sessionId && transcript) {
  const pythonPath = '.claude/skills/.venv/Scripts/python.exe';
  const scriptPath = '.claude/skills/cc-memory/scripts/main.py';
  execSync(
    `${pythonPath} ${scriptPath} archive --session-id ${sessionId} --transcript "${transcript}" --workspace "${workspace}"`,
    { stdio: 'inherit' }
  );
}
```
```

### 4. Ensure hooks for session archiving

The existing `session-end-memory-archive.cjs` hook should handle this. Verify it exists and is configured.

If not, create:

```javascript
// .claude/hooks/session-end-memory-archive.cjs
const { execSync, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

module.exports = async function(context) {
  const sessionId = process.env.CLAUDE_SESSION_ID || context.sessionId;
  const transcript = process.env.CLAUDE_TRANSCRIPT_PATH || context.transcriptPath;
  const workspace = process.cwd();

  if (!sessionId || !transcript || !fs.existsSync(transcript)) {
    return;
  }

  // Determine Python path
  const isWindows = process.platform === 'win32';
  const venvPython = isWindows
    ? path.join('.claude', 'skills', '.venv', 'Scripts', 'python.exe')
    : path.join('.claude', 'skills', '.venv', 'bin', 'python3');

  const scriptPath = path.join('.claude', 'skills', 'cc-memory', 'scripts', 'main.py');

  if (!fs.existsSync(venvPython)) {
    console.log('cc-memory: venv not found, skipping archive');
    return;
  }

  try {
    spawnSync(venvPython, [
      scriptPath,
      'archive',
      '--session-id', sessionId,
      '--transcript', transcript,
      '--workspace', workspace
    ], { stdio: 'inherit' });
    console.log(`cc-memory: Session ${sessionId.slice(0, 8)} archived`);
  } catch (e) {
    console.error('cc-memory archive error:', e.message);
  }
};
```

### 5. Add cc-memory to brsekit SKILL.md index

Update `.claude/skills/brsekit/SKILL.md`:

```markdown
## BrseKit Skills Index

### Core Skills
- **bk-track** - Project tracking and status reports
- **bk-recall** - Project memory layer (project-scoped)
- **bk-capture** - Task and meeting capture
- **bk-init** - Project initialization

### Translation & Docs
- **bk-convert** - Document translation (Excel, PPT)
- **bk-translate** - Text translation
- **bk-spec** - Specification refinement
- **bk-write** - Japanese business writing

### Memory
- **cc-memory** - User-level memory (cross-project)
  - Search facts: `/cc-memory search "topic"`
  - Recent sessions: `/cc-memory recent`
  - Save session: `/cc-memory save`
```

## Related Code Files

### Verify (no changes)
- `.claude/skills/cc-memory/scripts/main.py`
- `.claude/skills/cc-memory/scripts/memory_db.py`
- `.claude/skills/cc-memory/scripts/memory_store.py`

### Update
- `.claude/skills/cc-memory/SKILL.md` - Add BrseKit integration notes
- `.claude/skills/brsekit/SKILL.md` - Add cc-memory to index

### Create (if missing)
- `.claude/hooks/session-end-memory-archive.cjs`
- `memory/conversation-history/.gitkeep`

## Todo List

- [ ] Verify cc-memory scripts work standalone
- [ ] Update cc-memory SKILL.md with BrseKit notes
- [ ] Add cc-memory to brsekit SKILL.md index
- [ ] Verify/create session-end hook for archiving
- [ ] Create `memory/` directory structure
- [ ] Test session archiving

## Success Criteria

- [ ] `/cc-memory status` shows storage at `~/claude_client/memory/`
- [ ] `/cc-memory search "query"` returns facts from all sessions
- [ ] Session archived on exit (if hook enabled)
- [ ] No conflict with project-scoped bk-recall vault

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hook not triggered | Medium | Test manually with /cc-memory save |
| Embedder unavailable | Low | Falls back to keyword search |
| Path issues on Windows | Low | Use path.join() |

## Next Steps

After Phase 4, proceed to [Phase 5: CLI & Documentation](./phase-05-cli-documentation.md).
