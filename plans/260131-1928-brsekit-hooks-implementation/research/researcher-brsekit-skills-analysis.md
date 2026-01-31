# BrseKit Skills Structure Analysis

**Date:** 2026-01-31
**Status:** Complete
**Scope:** Understanding project resolution patterns for hooks implementation

## Executive Summary

BrseKit uses a **project-scoped, multi-project architecture** without active project files. Skills receive project names via CLI args and resolve paths/env dynamically. `resolveProject()` logic should live in a utility module as a **helper function**, not a core component.

## Key Findings

### 1. Skills Structure
- **Location:** `.claude/skills/brsekit/` (main definition) + individual `bk-*` skill directories
- **Entry point:** Each skill has `scripts/main.py` with argparse-based CLI
- **Pattern:** CLI arg parsing → validation → environment setup → execution
- **Shared utilities:** `.claude/skills/lib/` contains reusable modules

### 2. Project Resolution Flow

**Current approach** (from `skill_utils.py` + `bk-track/main.py`):

```python
# Pattern 1: Use skill_utils helpers
project = get_project(args)  # Get from positional or --project flag
if validate_project_exists(project):
    pm, env = setup_project_env(project)
    env_val = env.get("KEY", project)

# Pattern 2: Fallback to global env
load_brsekit_env()  # Load .claude/skills/brsekit/.env
api_key = os.getenv("NULAB_API_KEY")
```

### 3. Where resolveProject() Should Live

**Recommended location:** `.claude/skills/lib/project_resolver.py`

**Rationale:**
- Centralizes project resolution logic
- Reusable across all bk-* skills (capture, track, recall, etc.)
- Follows single-responsibility principle
- Complements existing utilities (skill_utils.py, project_manager.py)

### 4. Existing Project Handling Utilities

| Module | Function | Purpose |
|--------|----------|---------|
| `project_manager.py` | `list_projects()` | Discover projects in projects/ |
| `project_manager.py` | `get_project_path()` | Get projects/{name} path |
| `project_manager.py` | `get_context()` | Load context.yaml |
| `env_loader.py` | `get()` | Get env with fallback chain |
| `env_loader.py` | `get_all()` | Get all merged env vars |
| `skill_utils.py` | `get_project()` | Extract project from args |
| `skill_utils.py` | `validate_project_exists()` | Check project exists + error |
| `skill_utils.py` | `setup_project_env()` | Initialize PM + EnvLoader |

### 5. Multi-Project Architecture Details

**Project directory structure:**
```
projects/
└── {project_name}/
    ├── .env                 # Project-specific vars
    ├── context.yaml         # Project config
    ├── glossary.json        # Project terms (optional)
    └── vault/               # Project memory
        └── vault.db
```

**Environment fallback chain** (EnvLoader):
1. `projects/{project}/.env` (highest priority)
2. Workspace-level `.env` (.claude/skills/brsekit/.env)
3. System environment variables

**No `.active` file** → Always specify project explicitly:
- `/bk-track status HB21373`
- `/bk-recall search "query" --project HB21373`

### 6. How Skills Currently Handle --project

**bk-track pattern:**
```python
# 1. Get from args (positional or flag)
project = getattr(args, "project", None) or getattr(args, "project_flag", None)

# 2. Setup project env
if project and setup_project_env:
    if validate_project_exists(project):
        pm, env = setup_project_env(project)
        api_key = env.get("NULAB_API_KEY", project)
    else:
        # Fallback: treat as Backlog project key, use global env
        load_brsekit_env()

# 3. Fallback if no project specified
if not project:
    load_brsekit_env()
    api_key = os.getenv("NULAB_API_KEY")
```

**bk-recall pattern:**
```python
# Simpler: passes project to SyncManager
result = manager.sync(args.source, project_key=args.project)
```

### 7. Integration Points for resolveProject()

**Should handle:**
- Parse CLI args (positional + flags)
- Validate project exists
- Load project context.yaml
- Setup environment fallback chain
- Detect workspace root (CLAUDE.md / .claude directory)
- Handle errors gracefully (return type/tuple)

**Should NOT do:**
- Execute domain logic
- Create/modify projects (use ProjectManager instead)
- Load vault/database (use VaultStore instead)

## Unresolved Questions

1. Should `resolveProject()` return `(pm, env, project_path)` tuple or custom dataclass?
2. How to handle projects/ directory doesn't exist (fresh workspace)?
3. Should resolve honor env vars that don't have project dirs (legacy mode)?
4. Integration with hooks: Where should hook call `resolveProject()`—in wrapper or skill entrypoint?

## Recommended Next Steps

1. Create `project_resolver.py` in `.claude/skills/lib/`
2. Implement `resolveProject(args, workspace_root=None)` function
3. Refactor bk-* skills to use new utility
4. Document in SKILL.md with examples
5. Add to skill_utils for backwards compatibility
