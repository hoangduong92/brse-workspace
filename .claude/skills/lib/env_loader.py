"""Environment variable loader with fallback chain."""
import os
from pathlib import Path
from typing import Optional, Dict

try:
    from dotenv import dotenv_values
except ImportError:
    dotenv_values = None


class EnvLoader:
    """Load env vars with project -> workspace -> system fallback."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self._cache: Dict[str, Dict[str, str]] = {}

    def _load_env_file(self, path: Path) -> Dict[str, str]:
        """Load .env file into dict."""
        if str(path) in self._cache:
            return self._cache[str(path)]

        if not path.exists():
            return {}

        if dotenv_values is not None:
            values = dotenv_values(path)
            self._cache[str(path)] = dict(values)
        else:
            # Fallback: parse manually
            values = {}
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        values[key] = value
            self._cache[str(path)] = values

        return self._cache[str(path)]

    def get(
        self,
        key: str,
        project: Optional[str] = None,
        default: Optional[str] = None
    ) -> Optional[str]:
        """Get env var with fallback chain.

        Priority: project .env -> workspace .env -> system env
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

    def clear_cache(self) -> None:
        """Clear cached env values."""
        self._cache.clear()
