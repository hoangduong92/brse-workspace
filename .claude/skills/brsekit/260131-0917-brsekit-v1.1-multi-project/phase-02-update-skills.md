# Phase 2: Update Skills

## Priority: P1
## Status: pending
## Effort: 5h

## Overview

Add `--project` argument to all bk-* skills and update bk-init to create project structure.

## Key Insights

- Current skills use global env vars directly
- bk-recall already has `--project` param but doesn't scope vault
- bk-track uses `NULAB_PROJECT_ID` env var
- Need consistent CLI pattern across all skills

## Requirements

### Functional
- All bk-* skills accept `--project` or positional project arg
- `bk-init PROJECT` creates `projects/PROJECT/` structure
- Skills load env from project → workspace → system chain
- Error if project specified but doesn't exist (except bk-init)

### Non-functional
- Consistent arg naming: `--project` or `-p`
- Helpful error messages
- Backwards compatible (env var fallback)

## Architecture

```
Command Pattern:
  /bk-track status HB21373
  /bk-track status --project HB21373
  /bk-recall search "keyword" --project HB21373
  /bk-init HB21373

Env Fallback:
  1. projects/HB21373/.env
  2. ./.env
  3. System env
```

## Skills to Update

| Skill | Current State | Changes |
|-------|--------------|---------|
| bk-init | Creates in cwd | Create in `projects/{name}/` |
| bk-track | Uses NULAB_PROJECT_ID | Add --project, scoped vault |
| bk-recall | Has --project but no scope | Scope vault, env chain |
| bk-capture | No project param | Add --project for vault save |
| bk-spec | No project param | Add --project for context |
| bk-convert | No project param | Add --project for glossary |
| bk-morning | No project param | Add --project for brief |

## Implementation Steps

### 1. Create shared helper module

```python
# .claude/skills/lib/skill_utils.py
"""Shared utilities for BrseKit skills."""
import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))

from project_manager import ProjectManager
from env_loader import EnvLoader


def add_project_arg(parser: argparse.ArgumentParser, required: bool = False):
    """Add --project argument to parser."""
    parser.add_argument(
        "project",
        nargs="?" if not required else None,
        help="Project name (e.g., HB21373)"
    )
    parser.add_argument(
        "--project", "-p",
        dest="project_flag",
        help="Project name (alternative to positional)"
    )


def get_project(args) -> Optional[str]:
    """Get project from args (positional or flag)."""
    return getattr(args, "project", None) or getattr(args, "project_flag", None)


def require_project(args) -> str:
    """Get project or exit with error."""
    project = get_project(args)
    if not project:
        print("Error: Project name required")
        print("Usage: command PROJECT or command --project PROJECT")
        sys.exit(1)
    return project


def setup_project_env(project: str, workspace_root: Optional[Path] = None) -> Tuple[ProjectManager, EnvLoader]:
    """Setup project manager and load env vars.

    Returns (ProjectManager, EnvLoader) tuple.
    """
    pm = ProjectManager(workspace_root)
    env = EnvLoader(workspace_root)

    if project and pm.project_exists(project):
        env.load_for_project(project)

    return pm, env


def validate_project_exists(project: str, workspace_root: Optional[Path] = None) -> bool:
    """Check if project exists, print error if not."""
    pm = ProjectManager(workspace_root)
    if not pm.project_exists(project):
        print(f"Error: Project '{project}' not found")
        print(f"Run: /bk-init {project} to create it")
        return False
    return True
```

### 2. Update bk-init

Source: `experiments/brsekit-starter_v1.1/bk-init/scripts/main.py`
Target: `.claude/skills/bk-init/scripts/main.py`

Key changes:
```python
# main.py changes

def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument("project", nargs="?", help="Project name to initialize")
    # ... existing args ...

    args = parser.parse_args()

    # If project given, create in projects/ directory
    if args.project:
        output_dir = Path.cwd() / "projects" / args.project
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(args.output)

    # ... rest of wizard flow ...

    # After config saved, create vault dir
    vault_dir = output_dir / "vault"
    vault_dir.mkdir(exist_ok=True)

    # Copy context.yaml to canonical name
    if (output_dir / "project-context.yaml").exists():
        import shutil
        shutil.copy(
            output_dir / "project-context.yaml",
            output_dir / "context.yaml"
        )
```

### 3. Update bk-track

Source: `experiments/brsekit-starter_v1.1/bk-track/scripts/main.py`
Target: `.claude/skills/bk-track/scripts/main.py`

Key changes:
```python
# At start of cmd_status():

def cmd_status(args):
    from skill_utils import get_project, setup_project_env, validate_project_exists
    from vault import VaultStore, TimeLogStore

    project = get_project(args)

    if project:
        if not validate_project_exists(project):
            return
        pm, env = setup_project_env(project)
        # Override env vars from project
        space_url = env.get("NULAB_SPACE_URL", project)
        api_key = env.get("NULAB_API_KEY", project)
    else:
        # Fallback to global env (backwards compat)
        load_brsekit_env()
        space_url = os.getenv("NULAB_SPACE_URL")
        api_key = os.getenv("NULAB_API_KEY")
        project = os.getenv("NULAB_PROJECT_ID") or args.project

    # Use project-scoped vault for time logs
    if project:
        time_log_store = TimeLogStore(project=project)
    else:
        time_log_store = TimeLogStore()
```

### 4. Update bk-recall

Source: `experiments/brsekit-starter_v1.1/bk-recall/scripts/main.py`
Target: `.claude/skills/bk-recall/scripts/main.py`

Key changes:
```python
# Update imports at top
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
from skill_utils import get_project, setup_project_env, validate_project_exists

# In cmd_sync():
def cmd_sync(args):
    project = get_project(args)

    if project:
        if not validate_project_exists(project):
            return
        pm, env = setup_project_env(project)

    manager = SyncManager(project=project)  # Pass project
    # ...

# In cmd_search():
def cmd_search(args):
    project = get_project(args)
    handler = SearchHandler(project=project)  # Pass project
    # ...

# Update SyncManager and SearchHandler to accept project param
```

### 5. Update bk-capture

Source: `experiments/brsekit-starter_v1.1/bk-capture/scripts/main.py`
Target: `.claude/skills/bk-capture/scripts/main.py`

Key changes:
```python
# Add --project to parser
parser.add_argument("--project", "-p", help="Project to save to")

# In vault_saver.py:
def save_to_vault(item, project: Optional[str] = None):
    from vault import VaultStore
    store = VaultStore(project=project)
    # ...
```

### 6. Update remaining skills

Apply same pattern to:
- **bk-spec**: Add --project for loading project context
- **bk-convert**: Add --project for glossary lookup
- **bk-morning**: Add --project for brief generation

## Related Code Files

### Create
- `.claude/skills/lib/skill_utils.py`

### Update
- `.claude/skills/bk-init/scripts/main.py`
- `.claude/skills/bk-track/scripts/main.py`
- `.claude/skills/bk-recall/scripts/main.py`
- `.claude/skills/bk-recall/scripts/sync_manager.py`
- `.claude/skills/bk-recall/scripts/search_handler.py`
- `.claude/skills/bk-capture/scripts/main.py`
- `.claude/skills/bk-capture/scripts/vault_saver.py`
- `.claude/skills/bk-spec/scripts/main.py`
- `.claude/skills/bk-convert/scripts/main.py`
- `.claude/skills/bk-morning/scripts/main.py`

## Todo List

- [ ] Create `lib/skill_utils.py`
- [ ] Update bk-init for project structure
- [ ] Update bk-track with --project
- [ ] Update bk-recall with scoped vault
- [ ] Update bk-capture with --project
- [ ] Update bk-spec with --project
- [ ] Update bk-convert with --project
- [ ] Update bk-morning with --project
- [ ] Update SKILL.md docs for each

## Success Criteria

- [ ] `/bk-init HB21373` creates `projects/HB21373/` with context.yaml, .env, vault/
- [ ] `/bk-track status HB21373` loads env from `projects/HB21373/.env`
- [ ] `/bk-recall search "query" --project HB21373` searches project vault
- [ ] Commands without --project still work (backwards compat)

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing workflows | High | Keep env var fallback |
| Inconsistent arg handling | Medium | Use shared skill_utils |
| Import path issues | Low | Test all skills |

## Next Steps

After Phase 2, proceed to [Phase 3: Knowledge Layer](./phase-03-knowledge-layer.md).
