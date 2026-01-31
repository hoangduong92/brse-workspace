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
    """Add --project argument to parser.

    Supports both positional and flag forms:
      command PROJECT
      command --project PROJECT
      command -p PROJECT
    """
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


def setup_project_env(
    project: str,
    workspace_root: Optional[Path] = None
) -> Tuple[ProjectManager, EnvLoader]:
    """Setup project manager and load env vars.

    Returns (ProjectManager, EnvLoader) tuple.
    """
    pm = ProjectManager(workspace_root)
    env = EnvLoader(workspace_root)

    if project and pm.project_exists(project):
        env.load_for_project(project)

    return pm, env


def validate_project_exists(
    project: str,
    workspace_root: Optional[Path] = None
) -> bool:
    """Check if project exists, print error if not."""
    pm = ProjectManager(workspace_root)
    if not pm.project_exists(project):
        print(f"Error: Project '{project}' not found")
        print(f"Run: /bk-init {project} to create it")
        return False
    return True


def get_workspace_root() -> Path:
    """Get workspace root by finding CLAUDE.md or .claude dir."""
    cwd = Path.cwd()

    # Check current and parent directories
    for parent in [cwd] + list(cwd.parents):
        if (parent / "CLAUDE.md").exists() or (parent / ".claude").is_dir():
            return parent
        # Stop at home directory
        if parent == Path.home():
            break

    return cwd


def get_vault_store(project: Optional[str] = None):
    """Get VaultStore instance, optionally scoped to project."""
    # Import here to avoid circular imports
    from vault.store import VaultStore
    from vault.embedder import GeminiEmbedder

    try:
        embedder = GeminiEmbedder()
    except Exception:
        embedder = None

    return VaultStore(embedder=embedder, project=project)
