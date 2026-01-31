"""Directory structure manager for BrseKit v2 per-project storage."""
from pathlib import Path
from typing import List, Optional


class DirectoryManager:
    """Manages project directory structure under ~/.brsekit/projects/."""

    # Memory sources that have dedicated folders
    MEMORY_SOURCES = ["backlog", "slack", "email", "meetings"]

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize with base path (default: ~/.brsekit)."""
        self.base_path = base_path or Path.home() / ".brsekit"
        self.projects_path = self.base_path / "projects"
        self.db_path = self.base_path / "db"

    def ensure_base_structure(self) -> None:
        """Create base ~/.brsekit structure if not exists."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.projects_path.mkdir(exist_ok=True)
        self.db_path.mkdir(exist_ok=True)
        (self.db_path / "embeddings").mkdir(exist_ok=True)

    def ensure_project_structure(self, project_key: str) -> Path:
        """Create full project directory tree if not exists.

        Args:
            project_key: Unique project identifier (e.g., 'BKT', 'PROJ-A')

        Returns:
            Path to project root directory
        """
        self.ensure_base_structure()

        project_path = self.projects_path / project_key
        project_path.mkdir(exist_ok=True)

        # Knowledge layer (human-editable)
        knowledge = project_path / "knowledge"
        knowledge.mkdir(exist_ok=True)
        (knowledge / "specs").mkdir(exist_ok=True)

        # Memory layer (auto-synced)
        memory = project_path / "memory"
        memory.mkdir(exist_ok=True)
        for source in self.MEMORY_SOURCES:
            (memory / source).mkdir(exist_ok=True)

        # Templates (user templates)
        (project_path / "templates").mkdir(exist_ok=True)

        # Archive (for old files)
        (project_path / "archive").mkdir(exist_ok=True)

        return project_path

    def get_project_path(self, project_key: str) -> Path:
        """Get path to project folder."""
        return self.projects_path / project_key

    def get_knowledge_path(self, project_key: str) -> Path:
        """Get path to knowledge/ subfolder."""
        return self.projects_path / project_key / "knowledge"

    def get_memory_path(self, project_key: str, source: Optional[str] = None) -> Path:
        """Get path to memory/ subfolder or specific source folder.

        Args:
            project_key: Project identifier
            source: Optional source name (backlog, slack, email, meetings)

        Returns:
            Path to memory folder or memory/source folder
        """
        memory_path = self.projects_path / project_key / "memory"
        if source:
            return memory_path / source
        return memory_path

    def get_templates_path(self, project_key: str) -> Path:
        """Get path to templates/ subfolder."""
        return self.projects_path / project_key / "templates"

    def get_archive_path(self, project_key: str) -> Path:
        """Get path to archive/ subfolder."""
        return self.projects_path / project_key / "archive"

    def get_embeddings_db_path(self, project_key: str) -> Path:
        """Get path to per-project embeddings database."""
        return self.db_path / "embeddings" / f"{project_key}.db"

    def list_projects(self) -> List[str]:
        """List all project keys."""
        if not self.projects_path.exists():
            return []
        return [
            p.name for p in self.projects_path.iterdir()
            if p.is_dir() and not p.name.startswith(".")
        ]

    def project_exists(self, project_key: str) -> bool:
        """Check if project folder exists."""
        return (self.projects_path / project_key).exists()

    def delete_project(self, project_key: str) -> bool:
        """Delete project folder (use with caution).

        Returns:
            True if deleted, False if not found
        """
        import shutil
        project_path = self.projects_path / project_key
        if project_path.exists():
            shutil.rmtree(project_path)
            return True
        return False
