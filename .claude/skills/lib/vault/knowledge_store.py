"""Knowledge store - human-editable files for glossary, FAQ, rules, specs."""
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .directory_manager import DirectoryManager


@dataclass
class GlossaryEntry:
    """A glossary term definition."""
    term: str
    definition: str
    aliases: List[str] = field(default_factory=list)
    category: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dict."""
        return {
            "term": self.term,
            "definition": self.definition,
            "aliases": self.aliases,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GlossaryEntry":
        """Create from dict."""
        return cls(
            term=data["term"],
            definition=data["definition"],
            aliases=data.get("aliases", []),
            category=data.get("category"),
        )


class KnowledgeStore:
    """Store for human-editable knowledge files."""

    GLOSSARY_FILE = "glossary.json"
    FAQ_FILE = "faq.md"
    RULES_FILE = "rules.md"
    SPECS_DIR = "specs"

    def __init__(self, project_key: str, base_path: Optional[Path] = None):
        """Initialize knowledge store for a project.

        Args:
            project_key: Unique project identifier
            base_path: Optional base path (default: ~/.brsekit)
        """
        self.project_key = project_key
        self.dir_manager = DirectoryManager(base_path)
        self.dir_manager.ensure_project_structure(project_key)
        self.knowledge_path = self.dir_manager.get_knowledge_path(project_key)

    # ========== Glossary Operations ==========

    def get_glossary(self) -> Dict[str, GlossaryEntry]:
        """Load glossary.json as dict keyed by term."""
        glossary_path = self.knowledge_path / self.GLOSSARY_FILE

        if not glossary_path.exists():
            return {}

        with open(glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        result = {}
        for entry_data in data.get("terms", []):
            entry = GlossaryEntry.from_dict(entry_data)
            result[entry.term] = entry
            # Also index by aliases
            for alias in entry.aliases:
                result[alias] = entry

        return result

    def get_glossary_list(self) -> List[GlossaryEntry]:
        """Get glossary as list (unique entries only)."""
        glossary_path = self.knowledge_path / self.GLOSSARY_FILE

        if not glossary_path.exists():
            return []

        with open(glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [GlossaryEntry.from_dict(e) for e in data.get("terms", [])]

    def _save_glossary(self, entries: List[GlossaryEntry]) -> None:
        """Save glossary to file."""
        glossary_path = self.knowledge_path / self.GLOSSARY_FILE
        data = {"terms": [e.to_dict() for e in entries]}

        with open(glossary_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_term(
        self,
        term: str,
        definition: str,
        aliases: Optional[List[str]] = None,
        category: Optional[str] = None,
    ) -> bool:
        """Add or update a glossary term.

        Returns:
            True if added, False if updated existing
        """
        entries = self.get_glossary_list()

        # Check if term already exists
        for i, entry in enumerate(entries):
            if entry.term == term:
                # Update existing
                entries[i] = GlossaryEntry(
                    term=term,
                    definition=definition,
                    aliases=aliases or entry.aliases,
                    category=category or entry.category,
                )
                self._save_glossary(entries)
                return False

        # Add new
        entries.append(GlossaryEntry(
            term=term,
            definition=definition,
            aliases=aliases or [],
            category=category,
        ))
        self._save_glossary(entries)
        return True

    def remove_term(self, term: str) -> bool:
        """Remove a glossary term.

        Returns:
            True if removed, False if not found
        """
        entries = self.get_glossary_list()
        original_len = len(entries)

        entries = [e for e in entries if e.term != term]

        if len(entries) < original_len:
            self._save_glossary(entries)
            return True
        return False

    def search_glossary(self, query: str) -> List[GlossaryEntry]:
        """Search glossary by term, alias, or definition."""
        query_lower = query.lower()
        entries = self.get_glossary_list()

        results = []
        for entry in entries:
            if (
                query_lower in entry.term.lower()
                or query_lower in entry.definition.lower()
                or any(query_lower in alias.lower() for alias in entry.aliases)
            ):
                results.append(entry)

        return results

    # ========== FAQ Operations ==========

    def get_faq(self) -> str:
        """Load faq.md content."""
        faq_path = self.knowledge_path / self.FAQ_FILE

        if not faq_path.exists():
            return ""

        with open(faq_path, "r", encoding="utf-8") as f:
            return f.read()

    def update_faq(self, content: str) -> None:
        """Write faq.md content."""
        faq_path = self.knowledge_path / self.FAQ_FILE

        with open(faq_path, "w", encoding="utf-8") as f:
            f.write(content)

    def append_faq(self, question: str, answer: str) -> None:
        """Append a Q&A to FAQ file."""
        current = self.get_faq()

        new_entry = f"\n## Q: {question}\n\n{answer}\n"

        self.update_faq(current + new_entry)

    # ========== Rules Operations ==========

    def get_rules(self) -> str:
        """Load rules.md content."""
        rules_path = self.knowledge_path / self.RULES_FILE

        if not rules_path.exists():
            return ""

        with open(rules_path, "r", encoding="utf-8") as f:
            return f.read()

    def update_rules(self, content: str) -> None:
        """Write rules.md content."""
        rules_path = self.knowledge_path / self.RULES_FILE

        with open(rules_path, "w", encoding="utf-8") as f:
            f.write(content)

    # ========== Specs Operations ==========

    def list_specs(self) -> List[str]:
        """List spec files in specs/ folder."""
        specs_path = self.knowledge_path / self.SPECS_DIR

        if not specs_path.exists():
            return []

        return [
            f.stem for f in specs_path.glob("*.md")
            if not f.name.startswith(".")
        ]

    def get_spec(self, name: str) -> Optional[str]:
        """Read spec file content.

        Args:
            name: Spec name (without .md extension)

        Returns:
            Spec content or None if not found
        """
        spec_path = self.knowledge_path / self.SPECS_DIR / f"{name}.md"

        if not spec_path.exists():
            return None

        with open(spec_path, "r", encoding="utf-8") as f:
            return f.read()

    def save_spec(self, name: str, content: str) -> None:
        """Write spec file.

        Args:
            name: Spec name (without .md extension)
            content: Spec content
        """
        specs_path = self.knowledge_path / self.SPECS_DIR
        specs_path.mkdir(exist_ok=True)

        spec_path = specs_path / f"{name}.md"

        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(content)

    def delete_spec(self, name: str) -> bool:
        """Delete spec file.

        Returns:
            True if deleted, False if not found
        """
        spec_path = self.knowledge_path / self.SPECS_DIR / f"{name}.md"

        if spec_path.exists():
            spec_path.unlink()
            return True
        return False

    def search_specs(self, query: str) -> List[str]:
        """Search specs by content.

        Returns:
            List of spec names that contain the query
        """
        query_lower = query.lower()
        results = []

        for spec_name in self.list_specs():
            content = self.get_spec(spec_name)
            if content and query_lower in content.lower():
                results.append(spec_name)

        return results
