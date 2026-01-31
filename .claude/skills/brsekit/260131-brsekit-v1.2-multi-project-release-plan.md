# BrseKit v1.1 & v1.2 - Multi-Project Release Plan

**Status:** Needs Revision (Split into 2 releases)
**Created:** 2026-01-31
**Effort:** ~15h total
**Validated:** 2026-01-31

---

## Validation Summary

**Validated:** 2026-01-31
**Questions asked:** 5
**Critical finding:** GitHub repo is v1.0 architecture (mislabeled as v1.1.0)

### Confirmed Decisions

| Decision | Choice |
|----------|--------|
| Release strategy | **Split into two releases** (v1.1 then v1.2) |
| v1.1 scope | Multi-project infra: projects/, lib utilities, --project support |
| v1.2 scope | cc-memory integration: cc-memory/, memory/ |
| Glossary location | Move to `knowledge/` (breaking change) |
| bk-convert update | Use new path with fallback to local glossaries/ |
| cc-memory migration | Auto-prompt on first run |

### Action Items

- [ ] **CRITICAL:** Revise plan to split into v1.1 and v1.2 releases
- [ ] Update objective to reflect v1.0 → v1.1 → v1.2 path
- [ ] Move Phase 1 (cc-memory) and Phase 5 to v1.2 release
- [ ] Add bk-convert glossary path update to v1.1

---

## Objective

~~Update GitHub brsekit-starter from single-project (v1.1.0) to true multi-project architecture with workspace-level cc-memory.~~

**REVISED:**
- **v1.1 Release:** Upgrade from v1.0 to multi-project architecture (projects/, lib/, --project support, knowledge/)
- **v1.2 Release:** Add cc-memory with workspace-level storage

## Target Architecture

```
<workspace>/
├── .claude/skills/           # CODE
│   ├── bk-*/                 # Skills with --project support
│   ├── cc-memory/            # NEW: workspace-level memory
│   └── lib/                  # NEW: shared utilities
│       ├── env_loader.py
│       ├── project_manager.py
│       ├── skill_utils.py
│       └── knowledge_manager.py
│
├── projects/                 # DATA - Per-project
│   ├── README.md
│   └── {PROJECT}/
│       ├── .env
│       ├── context.yaml
│       └── vault/
│
├── knowledge/                # DATA - Shared
│   └── glossary-it-terms.json
│
├── memory/                   # DATA - cc-memory (workspace-level)
│   ├── vault.db
│   ├── config.json
│   └── conversations/archives/
│
└── .env                      # Workspace fallback
```

---

## Phases

### Phase 1: Migrate cc-memory to Workspace Storage (3h)

**Status:** pending

**Files to modify:**

| File | Change |
|------|--------|
| `cc-memory/scripts/memory_db.py` | Update `get_memory_dir()` for workspace detection |
| `cc-memory/scripts/config_manager.py` | Use new path method |
| `cc-memory/SKILL.md` | Update storage docs |

**Key change in memory_db.py:**
```python
@classmethod
def get_memory_dir(cls, workspace_root: Optional[Path] = None) -> Path:
    """Get workspace-level memory directory.

    Priority: workspace/memory/ -> ~/.claude_client/memory/ (legacy)
    """
    if workspace_root:
        return workspace_root / "memory"

    # Detect workspace by CLAUDE.md or .claude/
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".claude").is_dir():
            return parent / "memory"
        if parent == Path.home():
            break

    # Fallback to home directory (legacy)
    return Path.home() / "claude_client" / "memory"
```

**Migration strategy: Auto-prompt on first run**

Khi cc-memory chạy lần đầu trong workspace mới và phát hiện data cũ ở `~/claude_client/memory/`:
1. Hiển thị prompt hỏi user có muốn migrate không
2. Nếu Yes → copy data sang `<workspace>/memory/`
3. Nếu No → bắt đầu fresh, giữ data cũ ở home

```python
# In memory_db.py initialize()
if not memory_dir.exists() and legacy_dir.exists():
    print("Found existing memory at ~/claude_client/memory/")
    print("Would you like to migrate to workspace-level? (y/n)")
    # ... prompt and copy if yes
```

---

### Phase 2: Add lib/ Utilities (2h)

**Status:** pending

**Copy from local to brsekit-starter:**

| Source | Target |
|--------|--------|
| `.claude/skills/lib/env_loader.py` | `lib/env_loader.py` |
| `.claude/skills/lib/project_manager.py` | `lib/project_manager.py` |
| `.claude/skills/lib/skill_utils.py` | `lib/skill_utils.py` |
| `.claude/skills/lib/knowledge_manager.py` | `lib/knowledge_manager.py` |

---

### Phase 3: Update bk-init for Multi-Project (2h)

**Status:** pending

**Copy from local:**
- `bk-init/scripts/main.py` (multi-project version)

**Key features:**
- `bk-init HB21373` → creates `projects/HB21373/`
- Creates: `.env`, `context.yaml`, `vault/`

---

### Phase 4: Add --project Support to Skills (3h)

**Status:** pending

**Skills to update:**
- bk-track
- bk-capture
- bk-spec
- bk-recall
- bk-convert
- bk-morning
- bk-write

**Pattern:**
```python
from skill_utils import add_project_arg, get_project, setup_project_env

add_project_arg(parser)  # Adds --project/-p and positional
project = get_project(args)
if project:
    pm, env_loader = setup_project_env(project)
```

---

### Phase 5: Add cc-memory to brsekit-starter (2h)

**Status:** pending

**Copy entire cc-memory/ folder with updated files from Phase 1**

---

### Phase 6: Create Directory Structure & Docs (2h)

**Status:** pending

**Create:**
- `projects/README.md` - First-run instructions
- `knowledge/glossary-it-terms.json` - Copy from local
- `memory/.gitkeep` - Placeholder

**Update:**
- `README.md` - Multi-project examples
- `metadata.json` - Version 1.2.0, add cc-memory

---

### Phase 7: Update Install Scripts (1h)

**Status:** pending

**Add to install.sh/ps1:**
- Create `projects/` with README.md
- Create `memory/` structure
- Create `knowledge/` with glossary
- Post-install message about `/bk-init`

---

## Critical Files

| File | Purpose |
|------|---------|
| `cc-memory/scripts/memory_db.py` | Workspace storage migration |
| `lib/skill_utils.py` | Project arg pattern |
| `lib/env_loader.py` | 3-tier env fallback |
| `bk-init/scripts/main.py` | Multi-project init |

---

## Verification

```bash
# 1. Fresh install
./install.sh
ls projects/     # Should have README.md
ls memory/       # Should exist
ls knowledge/    # Should have glossary

# 2. Create project
/bk-init TEST_PROJECT
ls projects/TEST_PROJECT/  # .env, context.yaml, vault/

# 3. Test skill with project
/bk-track status TEST_PROJECT

# 4. Test cc-memory workspace storage
/memory status
# Output: Storage: <workspace>/memory/
```

---

## Success Criteria

- [ ] `bk-init HB21373` creates `projects/HB21373/`
- [ ] All bk-* skills accept `--project` arg
- [ ] Env fallback: project → workspace → system
- [ ] cc-memory uses `<workspace>/memory/`
- [ ] cc-memory falls back to home if no workspace
- [ ] Fresh install creates all DATA directories
- [ ] metadata.json version 1.2.0 with cc-memory

---

## Decisions Made

| Decision | Choice |
|----------|--------|
| cc-memory migration | Auto-prompt on first run |
| GitHub release | Create `v1.2-multi-project` branch, then merge to main |

## Git Workflow

```bash
# 1. Clone brsekit-starter
git clone https://github.com/brsekit/brsekit-starter.git
cd brsekit-starter

# 2. Create feature branch
git checkout -b v1.2-multi-project

# 3. Apply all changes (Phase 1-7)
# ...

# 4. Commit and push
git add .
git commit -m "feat: multi-project architecture v1.2"
git push origin v1.2-multi-project

# 5. Create PR to main (or merge directly)
```

---

## Related Documents

- [brsekit-v2-roadmap.md](./brsekit-v2-roadmap.md)
- [phase1-storage-infrastructure-plan.md](./phase1-storage-infrastructure-plan.md)
- [phase2-semantic-search-plan.md](./phase2-semantic-search-plan.md)
- [phase3-auto-sync-plan.md](./phase3-auto-sync-plan.md)
