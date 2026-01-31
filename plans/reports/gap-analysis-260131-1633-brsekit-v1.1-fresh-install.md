# GAP Analysis: BrseKit v1.1 Fresh Install Experience

**Date:** 2026-01-31
**Status:** Analysis Complete
**Scope:** Compare target structure in plan vs actual state when user downloads kit

---

## Executive Summary

| Category | Status | Notes |
|----------|--------|-------|
| CODE (skills) | ✅ Complete | All bk-* skills present |
| DATA (projects) | ⚠️ Partial | Structure correct, no sample project |
| DATA (knowledge) | ✅ Complete | glossary-it-terms.json exists |
| DATA (memory) | ❌ Mismatch | Plan vs actual implementation differ |
| Install scripts | ⚠️ Partial | Don't create data directories |
| Documentation | ⚠️ Partial | Fresh user onboarding unclear |

---

## Target Structure (from plan.md)

```
<workspace>/
├── .claude/skills/           # CODE
│   ├── bk-track/
│   ├── bk-capture/
│   ├── bk-spec/
│   ├── bk-recall/
│   ├── bk-convert/
│   ├── bk-init/
│   ├── bk-morning/
│   ├── bk-write/
│   ├── brsekit/
│   ├── cc-memory/
│   ├── common/
│   └── lib/
│
├── projects/                  # DATA - Per-project
│   └── {PROJECT}/
│       ├── .env
│       ├── context.yaml
│       └── vault/
│
├── knowledge/                 # DATA - Shared
│   └── glossary-it-terms.json
│
├── memory/                    # DATA - Memory layer
│   ├── lib/                   # SQLite + embeddings
│   └── conversation-history/  # cc-memory
│
├── .env
└── CLAUDE.md
```

---

## Current State Analysis

### ✅ CODE Layer - Complete

| Component | Status | Path |
|-----------|--------|------|
| bk-track | ✅ | .claude/skills/bk-track/ |
| bk-capture | ✅ | .claude/skills/bk-capture/ |
| bk-spec | ✅ | .claude/skills/bk-spec/ |
| bk-recall | ✅ | .claude/skills/bk-recall/ |
| bk-convert | ✅ | .claude/skills/bk-convert/ |
| bk-init | ✅ | .claude/skills/bk-init/ |
| bk-morning | ✅ | .claude/skills/bk-morning/ |
| bk-write | ✅ | .claude/skills/bk-write/ |
| brsekit | ✅ | .claude/skills/brsekit/ |
| cc-memory | ✅ | .claude/skills/cc-memory/ |
| common | ✅ | .claude/skills/common/ |
| lib/vault | ✅ | .claude/skills/lib/vault/ |

### ⚠️ DATA Layer - projects/

| Status | Details |
|--------|---------|
| Directory exists | ✅ `projects/` folder present |
| Sample project | ❌ No BrseKit sample (only `solo-builder-12months/`) |
| bk-init creates | ✅ `bk-init HB21373` → `projects/HB21373/{.env, context.yaml, vault/}` |

**GAP:** Fresh user won't have any project until they run `bk-init PROJECT`.

### ✅ DATA Layer - knowledge/

| Status | Details |
|--------|---------|
| Directory exists | ✅ |
| glossary-it-terms.json | ✅ Present with IT terminology |

### ❌ DATA Layer - memory/

**CRITICAL DISCREPANCY:**

| Plan says | Actual implementation |
|-----------|----------------------|
| `<workspace>/memory/` | `~/claude_client/memory/` |
| `memory/lib/` - SQLite | `~/claude_client/memory/vault.db` |
| `memory/conversation-history/` | `~/claude_client/memory/conversations/archives/` |

**Analysis:** cc-memory stores at **user level** (`~/claude_client/memory/`), NOT workspace level.

**Options:**
1. **Accept current**: User-level storage is intentional (cross-project memory)
2. **Update plan**: Plan incorrectly shows workspace-level memory
3. **Change implementation**: Move to workspace level

**Recommendation:** Option 2 - Update plan. User-level memory makes sense for cc-memory (cross-project).

---

## GAPs for Fresh Install Experience

### GAP 1: No Sample Project

**Problem:** User downloads kit, has no projects to test with.

**Current:** User must run `/bk-init HB21373` to create first project.

**Solution options:**
1. Add sample project `projects/DEMO/` with fake data
2. Add README in `projects/` explaining first step
3. Make bk-init auto-run on first use

**Recommendation:** Option 2 - Add `projects/README.md` with quick start.

### GAP 2: Install Scripts Don't Create DATA Directories

**Problem:** `install.sh` / `install.ps1` only set up CODE (Python venv, npm deps).

**Missing:**
- Don't create `projects/` directory
- Don't create `knowledge/` directory
- Don't run `bk-init` wizard

**Solution:** Add post-install step or separate `bk-init` first-run detection.

### GAP 3: Plan-Reality Mismatch on memory/

**Problem:** Plan shows `memory/` at workspace level, but cc-memory uses `~/claude_client/memory/`.

**Solution:** Update plan.md to reflect actual implementation.

### GAP 4: Onboarding Documentation Gap

**Problem:** Fresh user doesn't know what to do first.

**Current flow:**
1. Clone/download kit
2. Run `install.sh` or `install.ps1`
3. ??? (unclear)
4. Start using

**Should be:**
1. Clone/download kit
2. Run install script
3. Run `/bk-init HB21373` (clear instruction)
4. Set credentials
5. Start using `/bk-track status HB21373`

---

## Recommended Actions

### Priority 1: Fix Plan-Reality Mismatch

- [ ] Update `plan.md` to remove `memory/` directory (cc-memory uses user-level)
- [ ] Or decide to migrate cc-memory to workspace-level

### Priority 2: Improve Fresh Install UX

- [ ] Add `projects/.gitkeep` or `projects/README.md` with instructions
- [ ] Add post-install message: "Next: Run /bk-init YOUR_PROJECT"
- [ ] Consider first-run detection in bk-init

### Priority 3: Documentation

- [ ] Create `GETTING_STARTED.md` in brsekit folder
- [ ] Add onboarding checklist

---

## Verification Commands

```bash
# Current structure check
ls -la .claude/skills/ | grep "^d"
ls -la projects/
ls -la knowledge/
ls -la memory/  # Should not exist (user-level instead)

# Fresh install simulation
# 1. Delete projects/
rm -rf projects/

# 2. Run bk-init
/bk-init HB21373

# 3. Verify created structure
ls -la projects/HB21373/
```

---

## Unresolved Questions

1. Should cc-memory move to workspace-level `memory/` or stay at user-level `~/claude_client/memory/`?
2. Should we include a DEMO project with sample data?
3. Should install script auto-prompt for `bk-init` after completion?
