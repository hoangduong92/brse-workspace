"""Glossary management for consistent JA↔VI translation."""

import json
from pathlib import Path
from typing import Dict, Optional


class GlossaryManager:
    """Manage translation glossaries for consistent terminology."""

    def __init__(self):
        """Initialize glossary manager with empty glossary."""
        self.glossary: Dict[str, str] = {}

    def load(self, path: str) -> None:
        """Load glossary from JSON file.

        Args:
            path: Path to JSON glossary file

        Raises:
            FileNotFoundError: If glossary file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        glossary_path = Path(path)
        if not glossary_path.exists():
            raise FileNotFoundError(f"Glossary file not found: {path}")

        with open(glossary_path, 'r', encoding='utf-8') as f:
            self.glossary = json.load(f)

    def add_term(self, ja: str, vi: str) -> None:
        """Add or update term in glossary.

        Args:
            ja: Japanese term
            vi: Vietnamese translation
        """
        self.glossary[ja] = vi

    def remove_term(self, ja: str) -> bool:
        """Remove term from glossary.

        Args:
            ja: Japanese term to remove

        Returns:
            True if term was removed, False if not found
        """
        if ja in self.glossary:
            del self.glossary[ja]
            return True
        return False

    def list_terms(self) -> Dict[str, str]:
        """Get all glossary terms.

        Returns:
            Dictionary of JA→VI term pairs
        """
        return self.glossary.copy()

    def format_for_prompt(self) -> str:
        """Format glossary terms for prompt injection.

        Returns:
            Formatted string of glossary terms, one per line
            Format: "Japanese term → Vietnamese term"
        """
        if not self.glossary:
            return "(No glossary terms loaded)"

        lines = []
        for ja, vi in sorted(self.glossary.items()):
            lines.append(f"{ja} → {vi}")
        return "\n".join(lines)

    def save(self, path: str) -> None:
        """Save glossary to JSON file.

        Args:
            path: Path to save glossary file
        """
        glossary_path = Path(path)
        glossary_path.parent.mkdir(parents=True, exist_ok=True)

        with open(glossary_path, 'w', encoding='utf-8') as f:
            json.dump(self.glossary, f, ensure_ascii=False, indent=2)
