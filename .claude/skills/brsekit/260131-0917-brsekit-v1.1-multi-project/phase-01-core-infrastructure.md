# Phase 1: Core Infrastructure

## Priority: P0
## Status: pending
## Effort: 4h

## Overview

Create foundational modules for project discovery, env loading, and project-scoped vault.

## Key Insights

- Current vault uses global `~/.brsekit/vault.db`
- Need per-project vault at `projects/{name}/vault/vault.db`
- cc-memory uses separate `~/claude_client/memory/vault.db` - keep this for user-level
- VaultDB.initialize() already accepts custom db_path - leverage this

## Requirements

### Functional
- Project manager discovers projects in `./projects/` directory
- Env loader chains: project → workspace → system
- Vault supports project-scoped SQLite paths
- All existing vault features work with project scope

### Non-functional
- No breaking changes to existing vault API
- Thread-safe operations
- Graceful fallback when project dir missing

## Architecture

```
lib/
├── project_manager.py   # NEW - Project discovery & management
├── env_loader.py        # NEW - Env fallback chain
└── vault/
    ├── db.py            # UPDATE - Support project-scoped paths
    └── store.py         # UPDATE - Add project param
```

## Related Code Files

### Create
- `.claude/skills/lib/project_manager.py`
- `.claude/skills/lib/env_loader.py`

### Update
- `.claude/skills/lib/vault/db.py` - Add get_project_db_path()
- `.claude/skills/lib/vault/store.py` - Add project param to VaultStore

## Implementation Steps

### 1. Create project_manager.py

```python
# .claude/skills/lib/project_manager.py
"""Project discovery and management for BrseKit multi-project."""
import os
from pathlib import Path
from typing import Optional, List, Dict
import yaml


class ProjectManager:
    """Discovers and manages BrseKit projects."""

    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize with workspace root (defaults to cwd)."""
        self.workspace_root = workspace_root or Path.cwd()
        self.projects_dir = self.workspace_root / "projects"

    def list_projects(self) -> List[str]:
        """List all project names in projects/ directory."""
        if not self.projects_dir.exists():
            return []
        return [
            d.name for d in self.projects_dir.iterdir()
            if d.is_dir() and (d / "context.yaml").exists()
        ]

    def get_project_path(self, project: str) -> Optional[Path]:
        """Get path to project directory."""
        path = self.projects_dir / project
        return path if path.exists() else None

    def get_context(self, project: str) -> Optional[Dict]:
        """Load project context.yaml."""
        path = self.get_project_path(project)
        if not path:
            return None
        context_file = path / "context.yaml"
        if not context_file.exists():
            return None
        with open(context_file, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_vault_path(self, project: str) -> Path:
        """Get path to project's vault directory."""
        return self.projects_dir / project / "vault"

    def get_vault_db_path(self, project: str) -> Path:
        """Get path to project's vault.db file."""
        vault_dir = self.get_vault_path(project)
        vault_dir.mkdir(parents=True, exist_ok=True)
        return vault_dir / "vault.db"

    def project_exists(self, project: str) -> bool:
        """Check if project directory exists."""
        return (self.projects_dir / project).is_dir()

    def create_project_structure(self, project: str) -> Path:
        """Create project directory structure."""
        project_path = self.projects_dir / project
        project_path.mkdir(parents=True, exist_ok=True)
        (project_path / "vault").mkdir(exist_ok=True)
        return project_path
```

### 2. Create env_loader.py

```python
# .claude/skills/lib/env_loader.py
"""Environment variable loader with fallback chain."""
import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import dotenv_values


class EnvLoader:
    """Load env vars with project → workspace → system fallback."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self._cache: Dict[str, Dict[str, str]] = {}

    def _load_env_file(self, path: Path) -> Dict[str, str]:
        """Load .env file into dict."""
        if str(path) in self._cache:
            return self._cache[str(path)]

        if not path.exists():
            return {}

        values = dotenv_values(path)
        self._cache[str(path)] = dict(values)
        return self._cache[str(path)]

    def get(self, key: str, project: Optional[str] = None, default: Optional[str] = None) -> Optional[str]:
        """Get env var with fallback chain.

        Priority: project .env → workspace .env → system env
        """
        # 1. Project-level .env
        if project:
            project_env = self.workspace_root / "projects" / project / ".env"
            project_values = self._load_env_file(project_env)
            if key in project_values:
                return project_values[key]

        # 2. Workspace-level .env
        workspace_env = self.workspace_root / ".env"
        workspace_values = self._load_env_file(workspace_env)
        if key in workspace_values:
            return workspace_values[key]

        # 3. System environment
        return os.environ.get(key, default)

    def load_for_project(self, project: str) -> None:
        """Load project env vars into os.environ (for backwards compat)."""
        # Project .env
        project_env = self.workspace_root / "projects" / project / ".env"
        for key, value in self._load_env_file(project_env).items():
            os.environ.setdefault(key, value)

        # Workspace .env (lower priority)
        workspace_env = self.workspace_root / ".env"
        for key, value in self._load_env_file(workspace_env).items():
            os.environ.setdefault(key, value)

    def get_all(self, project: Optional[str] = None) -> Dict[str, str]:
        """Get all env vars merged with fallback."""
        result = dict(os.environ)

        # Workspace-level (can be overridden)
        workspace_env = self.workspace_root / ".env"
        result.update(self._load_env_file(workspace_env))

        # Project-level (highest priority)
        if project:
            project_env = self.workspace_root / "projects" / project / ".env"
            result.update(self._load_env_file(project_env))

        return result
```

### 3. Update lib/vault/db.py

Add project-scoped DB initialization:

```python
# Add to VaultDB class:

@classmethod
def get_project_db_path(cls, project: str, workspace_root: Optional[Path] = None) -> Path:
    """Get database path for specific project."""
    root = workspace_root or Path.cwd()
    vault_dir = root / "projects" / project / "vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir / "vault.db"

@classmethod
def initialize_for_project(cls, project: str, workspace_root: Optional[Path] = None):
    """Initialize database for specific project."""
    db_path = cls.get_project_db_path(project, workspace_root)
    cls.initialize(db_path)
```

### 4. Update lib/vault/store.py

Add project param:

```python
# Update VaultStore.__init__:

def __init__(self, embedder: Optional[GeminiEmbedder] = None, project: Optional[str] = None):
    """Initialize store with optional embedder and project scope."""
    self.embedder = embedder
    self.project = project
    if project:
        VaultDB.initialize_for_project(project)
    else:
        VaultDB.initialize()
```

### 5. Add project column to vault_items (migration)

```python
# Add to VaultDB._init_schema() - after vault_items CREATE:

# Add project column if not exists (SQLite migration)
cursor.execute("PRAGMA table_info(vault_items)")
columns = [row[1] for row in cursor.fetchall()]
if "project" not in columns:
    cursor.execute("ALTER TABLE vault_items ADD COLUMN project TEXT")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vault_project ON vault_items(project)")
```

## Todo List

- [ ] Create `lib/project_manager.py`
- [ ] Create `lib/env_loader.py`
- [ ] Update `lib/vault/db.py` with project methods
- [ ] Update `lib/vault/store.py` with project param
- [ ] Add project column migration to schema
- [ ] Write unit tests for ProjectManager
- [ ] Write unit tests for EnvLoader
- [ ] Test vault with project scope

## Success Criteria

- [ ] `ProjectManager().list_projects()` returns list of project names
- [ ] `EnvLoader().get("API_KEY", project="HB21373")` follows fallback chain
- [ ] `VaultStore(project="HB21373")` uses `projects/HB21373/vault/vault.db`
- [ ] Existing global vault still works without project param

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing vault | High | Keep default behavior unchanged |
| SQLite migration fails | Medium | Handle missing column gracefully |
| Path issues on Windows | Low | Use pathlib consistently |

## Next Steps

After completing Phase 1, proceed to [Phase 2: Update Skills](./phase-02-update-skills.md) to add `--project` arg to all bk-* commands.
