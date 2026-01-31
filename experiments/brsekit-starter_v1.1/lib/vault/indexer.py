"""Background content indexer for BrseKit v2 semantic search."""
import gzip
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .directory_manager import DirectoryManager
from .embedding_store import EmbeddingStore
from .embedder import GeminiEmbedder
from .metadata_db import MetadataDB


class Indexer:
    """Background indexer for knowledge and memory content."""

    def __init__(
        self,
        project_key: str,
        embedder: Optional[GeminiEmbedder] = None,
    ):
        """Initialize indexer for project.

        Args:
            project_key: Project identifier
            embedder: Optional embedder instance (lazy init if None)
        """
        self.project_key = project_key
        self.dir_manager = DirectoryManager()
        self.embedding_store = EmbeddingStore(project_key, embedder)
        MetadataDB.initialize()

    def index_knowledge(self) -> Dict[str, int]:
        """Index all knowledge files (glossary, FAQ, rules, specs).

        Returns:
            Dict with counts: {glossary, faq, rules, specs}
        """
        knowledge_path = self.dir_manager.get_knowledge_path(self.project_key)
        counts = {"glossary": 0, "faq": 0, "rules": 0, "specs": 0}

        if not knowledge_path.exists():
            return counts

        # Index glossary.json
        glossary_path = knowledge_path / "glossary.json"
        if glossary_path.exists():
            counts["glossary"] = self._index_glossary(glossary_path)

        # Index faq.md
        faq_path = knowledge_path / "faq.md"
        if faq_path.exists():
            counts["faq"] = self._index_markdown(faq_path, "faq")

        # Index rules.md
        rules_path = knowledge_path / "rules.md"
        if rules_path.exists():
            counts["rules"] = self._index_markdown(rules_path, "rules")

        # Index specs/
        specs_path = knowledge_path / "specs"
        if specs_path.exists() and specs_path.is_dir():
            for spec_file in specs_path.glob("*.md"):
                count = self._index_markdown(spec_file, "specs")
                counts["specs"] += count

        return counts

    def _index_glossary(self, path: Path) -> int:
        """Index glossary.json file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                glossary = json.load(f)

            count = 0
            for term, data in glossary.items():
                # Handle both simple and structured glossary
                if isinstance(data, str):
                    content = f"{term}: {data}"
                    metadata = {"term": term}
                else:
                    definition = data.get("definition", "")
                    aliases = data.get("aliases", [])
                    category = data.get("category", "")
                    content = f"{term}: {definition}"
                    if aliases:
                        content += f" (also: {', '.join(aliases)})"
                    metadata = {
                        "term": term,
                        "aliases": aliases,
                        "category": category,
                    }

                item_id = f"glossary:{term.lower().replace(' ', '_')}"
                self.embedding_store.index_item(
                    item_id=item_id,
                    content=content,
                    source="glossary",
                    layer="knowledge",
                    metadata=metadata,
                )
                count += 1

            return count
        except (json.JSONDecodeError, IOError):
            return 0

    def _index_markdown(self, path: Path, source: str) -> int:
        """Index markdown file, splitting by sections."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Split by headers
            sections = self._split_markdown_sections(content)

            count = 0
            for i, (header, body) in enumerate(sections):
                if not body.strip():
                    continue

                item_id = f"{source}:{path.stem}:{i}"
                section_content = f"{header}\n{body}" if header else body

                self.embedding_store.index_item(
                    item_id=item_id,
                    content=section_content,
                    source=source,
                    layer="knowledge",
                    metadata={"file": path.name, "section": header or f"section_{i}"},
                )
                count += 1

            return count
        except IOError:
            return 0

    def _split_markdown_sections(self, content: str) -> List[tuple]:
        """Split markdown content by headers.

        Returns:
            List of (header, body) tuples
        """
        lines = content.split("\n")
        sections = []
        current_header = ""
        current_body = []

        for line in lines:
            if line.startswith("#"):
                # Save previous section
                if current_body:
                    sections.append((current_header, "\n".join(current_body)))
                current_header = line.lstrip("#").strip()
                current_body = []
            else:
                current_body.append(line)

        # Save last section
        if current_body:
            sections.append((current_header, "\n".join(current_body)))

        return sections

    def index_memory(
        self,
        source: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """Index memory entries from JSONL files.

        Args:
            source: Filter by source (backlog, slack, email, meetings)
            since: Only index entries after this timestamp

        Returns:
            Dict with counts per source
        """
        memory_path = self.dir_manager.get_memory_path(self.project_key, "")
        counts = {}

        if not memory_path.exists():
            return counts

        sources = [source] if source else ["backlog", "slack", "email", "meetings"]

        for src in sources:
            src_path = memory_path / src
            if not src_path.exists():
                continue

            count = 0
            # Process both .jsonl and .jsonl.gz files
            for pattern in ["*.jsonl", "*.jsonl.gz"]:
                for file_path in src_path.glob(pattern):
                    count += self._index_jsonl_file(file_path, src, since)

            counts[src] = count

        return counts

    def _index_jsonl_file(
        self,
        path: Path,
        source: str,
        since: Optional[datetime],
    ) -> int:
        """Index a single JSONL file."""
        count = 0
        is_gzip = path.suffix == ".gz"

        try:
            open_func = gzip.open if is_gzip else open
            with open_func(path, "rt", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Check timestamp filter
                    if since:
                        ts = entry.get("timestamp") or entry.get("synced_at")
                        if ts:
                            entry_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            if entry_time < since:
                                continue

                    # Build content for indexing
                    item_id = entry.get("id") or f"{source}:{path.stem}:{count}"
                    content = self._build_entry_content(entry, source)

                    if content:
                        self.embedding_store.index_item(
                            item_id=item_id,
                            content=content,
                            source=source,
                            layer="memory",
                            metadata=self._extract_metadata(entry),
                        )
                        count += 1

        except IOError:
            pass

        return count

    def _build_entry_content(self, entry: Dict[str, Any], source: str) -> str:
        """Build searchable content from entry based on source type."""
        parts = []

        if source == "backlog":
            # Issue/task content
            if entry.get("issueKey"):
                parts.append(f"[{entry['issueKey']}]")
            if entry.get("summary"):
                parts.append(entry["summary"])
            if entry.get("description"):
                parts.append(entry["description"])
            if entry.get("comment"):
                parts.append(f"Comment: {entry['comment']}")

        elif source == "slack":
            if entry.get("channel"):
                parts.append(f"#{entry['channel']}")
            if entry.get("user"):
                parts.append(f"@{entry['user']}:")
            if entry.get("text"):
                parts.append(entry["text"])

        elif source == "email":
            if entry.get("subject"):
                parts.append(f"Subject: {entry['subject']}")
            if entry.get("from"):
                parts.append(f"From: {entry['from']}")
            if entry.get("body"):
                parts.append(entry["body"])

        elif source == "meetings":
            if entry.get("title"):
                parts.append(entry["title"])
            if entry.get("summary"):
                parts.append(entry["summary"])
            if entry.get("notes"):
                parts.append(entry["notes"])
            if entry.get("action_items"):
                items = entry["action_items"]
                if isinstance(items, list):
                    parts.append("Action items: " + "; ".join(items))

        else:
            # Generic content extraction
            if entry.get("content"):
                parts.append(entry["content"])
            elif entry.get("text"):
                parts.append(entry["text"])

        return " ".join(parts)

    def _extract_metadata(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metadata from entry."""
        metadata = {}

        # Common fields
        for key in ["timestamp", "synced_at", "source", "issueKey", "channel", "from"]:
            if key in entry:
                metadata[key] = entry[key]

        return metadata

    def reindex_all(self) -> Dict[str, Any]:
        """Full reindex of all knowledge and memory content.

        Returns:
            Dict with index statistics
        """
        knowledge_counts = self.index_knowledge()
        memory_counts = self.index_memory()

        return {
            "knowledge": knowledge_counts,
            "memory": memory_counts,
            "total": sum(knowledge_counts.values()) + sum(memory_counts.values()),
            "indexed_at": datetime.now().isoformat(),
        }

    def get_index_status(self) -> Dict[str, Any]:
        """Get current index status.

        Returns:
            Dict with index statistics
        """
        stats = self.embedding_store.get_stats()
        return {
            "project_key": self.project_key,
            "total_items": stats["total_items"],
            "items_with_embedding": stats["items_with_embedding"],
            "sources": stats["sources"],
            "last_indexed": stats["last_indexed"],
        }
