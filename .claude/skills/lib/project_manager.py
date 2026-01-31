"""Project discovery and management for BrseKit multi-project."""
import os
from pathlib import Path
from typing import Optional, List, Dict

try:
    import yaml
except ImportError:
    yaml = None


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
        if yaml is None:
            return None
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

    def get_env_path(self, project: str) -> Path:
        """Get path to project's .env file."""
        return self.projects_dir / project / ".env"

    def get_glossary_path(self, project: str) -> Path:
        """Get path to project's glossary.json file."""
        return self.projects_dir / project / "glossary.json"
