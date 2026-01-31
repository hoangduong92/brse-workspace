"""Knowledge and glossary management with fallback chain."""
import json
from pathlib import Path
from typing import Optional, Dict, List

try:
    import yaml
except ImportError:
    yaml = None


class KnowledgeManager:
    """Manages glossaries with project -> shared fallback."""

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.knowledge_dir = self.workspace_root / "knowledge"
        self.projects_dir = self.workspace_root / "projects"
        self._cache: Dict[str, Dict] = {}

    def _load_json_or_yaml(self, path: Path) -> Dict:
        """Load JSON or YAML file."""
        if not path.exists():
            return {}

        cache_key = str(path)
        if cache_key in self._cache:
            return self._cache[cache_key]

        with open(path, encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                if yaml is None:
                    return {}
                data = yaml.safe_load(f) or {}
            else:
                data = json.load(f)

        self._cache[cache_key] = data
        return data

    def get_glossary(self, project: Optional[str] = None) -> Dict[str, str]:
        """Get merged glossary with project -> shared fallback.

        Returns dict of {term: translation}.
        """
        result = {}

        # 1. Load shared glossary
        shared_path = self.knowledge_dir / "glossary-it-terms.json"
        shared = self._load_json_or_yaml(shared_path)
        if "terms" in shared:
            result.update(shared["terms"])
        else:
            result.update(shared)

        # 2. Load project-specific (overrides shared)
        if project:
            project_path = self.projects_dir / project / "glossary.json"
            project_glossary = self._load_json_or_yaml(project_path)
            if "terms" in project_glossary:
                result.update(project_glossary["terms"])
            else:
                result.update(project_glossary)

        return result

    def get_term(self, term: str, project: Optional[str] = None) -> Optional[str]:
        """Lookup single term with fallback."""
        glossary = self.get_glossary(project)
        # Try exact match first, then case-insensitive
        if term in glossary:
            return glossary[term]
        term_lower = term.lower()
        for key, value in glossary.items():
            if key.lower() == term_lower:
                return value
        return None

    def list_terms(
        self,
        project: Optional[str] = None,
        prefix: Optional[str] = None
    ) -> List[str]:
        """List all terms, optionally filtered by prefix."""
        glossary = self.get_glossary(project)
        terms = list(glossary.keys())
        if prefix:
            terms = [t for t in terms if t.lower().startswith(prefix.lower())]
        return sorted(terms)

    def add_term(self, term: str, translation: str, project: str) -> None:
        """Add term to project glossary."""
        project_path = self.projects_dir / project / "glossary.json"

        # Load existing
        glossary = self._load_json_or_yaml(project_path)
        if "terms" not in glossary:
            glossary["terms"] = {}

        glossary["terms"][term] = translation

        # Save
        project_path.parent.mkdir(parents=True, exist_ok=True)
        with open(project_path, "w", encoding="utf-8") as f:
            json.dump(glossary, f, ensure_ascii=False, indent=2)

        # Invalidate cache
        cache_key = str(project_path)
        if cache_key in self._cache:
            del self._cache[cache_key]

    def clear_cache(self) -> None:
        """Clear cached glossary data."""
        self._cache.clear()
