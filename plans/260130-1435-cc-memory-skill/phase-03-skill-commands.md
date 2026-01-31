# Phase 3: Skill Commands

## Context Links
- bk-recall pattern: `.claude/skills/bk-recall/scripts/main.py`
- VaultSearch: `.claude/skills/lib/vault/search.py`

## Overview
- **Priority:** P1 (user interface)
- **Status:** pending
- **Effort:** 2h

Implement `/memory` skill commands for search, recent, summarize, add, forget.

## Key Insights

1. Follow bk-recall pattern: main.py with argparse subcommands
2. Reuse VaultSearch for semantic search
3. Gemini for cross-session summarization
4. Simple add/forget for manual fact management

## Requirements

### Functional Commands

| Command | Description |
|---------|-------------|
| `/memory search "query"` | Semantic search across sessions + facts |
| `/memory recent [N]` | List N most recent sessions |
| `/memory summarize "topic"` | Summarize topic across sessions |
| `/memory add "fact"` | Manually add a fact |
| `/memory forget <id>` | Remove a fact by ID |

### Non-Functional
- Response time <3s for search
- Summarize may take longer (Gemini call)
- Clear error messages
- Markdown-formatted output

## Architecture

```
/memory command
    ↓
main.py (CLI router)
    ├── search → SearchHandler (VaultSearch)
    ├── recent → MemoryStore.get_recent_sessions()
    ├── summarize → Summarizer (Gemini)
    ├── add → MemoryStore.add_fact() + FactsWriter
    └── forget → MemoryStore.delete_fact()
```

## Related Code Files

### Create
- `.claude/skills/cc-memory/scripts/main.py` - CLI entry point
- `.claude/skills/cc-memory/scripts/search_handler.py` - Semantic search
- `.claude/skills/cc-memory/scripts/summarizer.py` - Cross-session summarization

### Modify
- None (uses existing infrastructure)

## Implementation Steps

### Step 1: Create main.py

```python
#!/usr/bin/env python3
"""cc-memory CLI - User-level memory for Claude Code."""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from memory_store import MemoryStore, Fact
from search_handler import MemorySearchHandler
from summarizer import MemorySummarizer
from facts_writer import FactsWriter

def cmd_search(args):
    """Search across sessions and facts."""
    handler = MemorySearchHandler()
    results = handler.query(args.query, top_k=args.limit)
    output = handler.format_results(results, verbose=args.verbose)
    print(output)

def cmd_recent(args):
    """List recent sessions."""
    store = MemoryStore()
    sessions = store.get_recent_sessions(limit=args.limit)

    if not sessions:
        print("No sessions found.")
        return

    print(f"## Recent Sessions ({len(sessions)})\n")
    for s in sessions:
        date = s.start_time.strftime("%Y-%m-%d %H:%M") if s.start_time else "Unknown"
        workspace = os.path.basename(s.workspace) if s.workspace else "Unknown"
        summary = s.summary[:60] + "..." if s.summary and len(s.summary) > 60 else (s.summary or "No summary")
        print(f"- **{date}** | {workspace} | {s.message_count} msgs")
        print(f"  {summary}")
        print(f"  ID: `{s.session_id[:8]}`")
        print()

def cmd_summarize(args):
    """Summarize topic across sessions."""
    summarizer = MemorySummarizer()
    summary = summarizer.summarize(
        topic=args.topic,
        max_sessions=args.limit
    )
    print(summary)

def cmd_add(args):
    """Manually add a fact."""
    store = MemoryStore()
    fact = Fact(
        id=None,
        content=args.fact,
        source_session=None,  # Manual entry
        confidence=1.0,
        category=args.category or "manual"
    )
    fact_id = store.add_fact(fact)

    # Also update facts.md
    writer = FactsWriter()
    writer.append_facts([fact], "manual")

    print(f"Added fact: {args.fact}")
    print(f"ID: {fact_id}")

def cmd_forget(args):
    """Remove a fact by ID."""
    store = MemoryStore()
    success = store.delete_fact(args.id)

    if success:
        print(f"Removed fact: {args.id}")
        print("Note: facts.md not updated. Run `/memory sync` to refresh.")
    else:
        print(f"Fact not found: {args.id}")

def cmd_sync(args):
    """Sync facts.md with database."""
    store = MemoryStore()
    writer = FactsWriter()

    facts = store.get_all_facts()

    # Rewrite facts.md from database
    writer.facts_path.parent.mkdir(parents=True, exist_ok=True)

    content = "# Memory Facts\n\nFacts extracted from Claude Code sessions.\n\n"

    by_category = {}
    for fact in facts:
        cat = fact.category or "general"
        by_category.setdefault(cat, []).append(fact)

    for category, cat_facts in by_category.items():
        content += f"## {category.title()}\n\n"
        for fact in cat_facts:
            conf = f"[{fact.confidence:.0%}]" if fact.confidence < 1 else ""
            src = f"(session: {fact.source_session[:8]})" if fact.source_session else "(manual)"
            content += f"- {fact.content} {conf} {src}\n"
        content += "\n"

    with open(writer.facts_path, "w") as f:
        f.write(content)

    print(f"Synced {len(facts)} facts to facts.md")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="cc-memory - User-level memory for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # search
    search_p = subparsers.add_parser("search", help="Search memory")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--limit", "-l", type=int, default=10)
    search_p.add_argument("--verbose", "-v", action="store_true")
    search_p.set_defaults(func=cmd_search)

    # recent
    recent_p = subparsers.add_parser("recent", help="Recent sessions")
    recent_p.add_argument("limit", nargs="?", type=int, default=5)
    recent_p.set_defaults(func=cmd_recent)

    # summarize
    sum_p = subparsers.add_parser("summarize", help="Summarize topic")
    sum_p.add_argument("topic", help="Topic to summarize")
    sum_p.add_argument("--limit", "-l", type=int, default=10)
    sum_p.set_defaults(func=cmd_summarize)

    # add
    add_p = subparsers.add_parser("add", help="Add fact manually")
    add_p.add_argument("fact", help="Fact content")
    add_p.add_argument("--category", "-c", help="Fact category")
    add_p.set_defaults(func=cmd_add)

    # forget
    forget_p = subparsers.add_parser("forget", help="Remove fact")
    forget_p.add_argument("id", help="Fact ID")
    forget_p.set_defaults(func=cmd_forget)

    # sync
    sync_p = subparsers.add_parser("sync", help="Sync facts.md")
    sync_p.set_defaults(func=cmd_sync)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)

if __name__ == "__main__":
    main()
```

### Step 2: Create search_handler.py

```python
"""Search handler for memory - semantic search across sessions and facts."""
import os
import sys
from typing import List, Optional
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
from vault import VaultSearch, GeminiEmbedder, SearchResult

from memory_store import MemoryStore

@dataclass
class MemorySearchResult:
    content: str
    source: str  # "fact", "session"
    session_id: Optional[str]
    score: float
    metadata: dict

class MemorySearchHandler:
    """Semantic search across memory."""

    def __init__(self):
        self.embedder = None
        self.search = None
        self.store = MemoryStore()

    def _ensure_initialized(self):
        if self.embedder is None:
            self.embedder = GeminiEmbedder()
            self.search = VaultSearch(self.embedder)

    def query(
        self,
        text: str,
        top_k: int = 10,
        min_score: float = 0.3
    ) -> List[MemorySearchResult]:
        """Search memory for matching items."""
        self._ensure_initialized()

        # Search vault (includes embedded facts)
        vault_results = self.search.query_by_source(text, "memory", top_k, min_score)

        results = []
        for r in vault_results:
            # Determine if fact or session
            is_fact = r.item.id.startswith("fact:")
            results.append(MemorySearchResult(
                content=r.item.content,
                source="fact" if is_fact else "session",
                session_id=r.item.metadata.get("source_session") if r.item.metadata else None,
                score=r.score,
                metadata=r.item.metadata or {}
            ))

        return results

    def format_results(self, results: List[MemorySearchResult], verbose: bool = False) -> str:
        """Format search results as markdown."""
        if not results:
            return "No results found in memory."

        lines = [f"## Memory Search Results ({len(results)})\n"]

        for i, r in enumerate(results, 1):
            lines.append(f"### {i}. [{r.source.upper()}] Score: {r.score:.2f}")

            if r.session_id:
                lines.append(f"- Session: `{r.session_id[:8]}`")

            if verbose:
                lines.append(f"\n```\n{r.content[:500]}\n```")
            else:
                preview = r.content[:150].replace("\n", " ")
                lines.append(f"- {preview}...")

            lines.append("")

        return "\n".join(lines)
```

### Step 3: Create summarizer.py

```python
"""Summarize topics across sessions using Gemini."""
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))
from memory_store import MemoryStore
from search_handler import MemorySearchHandler

class MemorySummarizer:
    """Summarize topics across memory."""

    def __init__(self):
        self.store = MemoryStore()
        self.search = MemorySearchHandler()

    def summarize(
        self,
        topic: str,
        max_sessions: int = 10
    ) -> str:
        """Summarize a topic across sessions."""
        # Search for relevant content
        results = self.search.query(topic, top_k=max_sessions * 2)

        if not results:
            return f"No information found about: {topic}"

        # Collect content for summarization
        content_pieces = []
        session_ids = set()

        for r in results:
            content_pieces.append(r.content)
            if r.session_id:
                session_ids.add(r.session_id)

        combined = "\n---\n".join(content_pieces[:15])  # Limit for API

        # Generate summary with Gemini
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

            prompt = f"""Summarize what the user knows/decided about: "{topic}"

Based on these excerpts from past Claude Code sessions:

{combined}

Provide a concise summary (3-5 bullet points) of key information about this topic.
Focus on decisions, preferences, and important context."""

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            summary = response.text
            summary += f"\n\n*Based on {len(session_ids)} session(s)*"
            return summary

        except Exception as e:
            # Fallback: return raw matches
            fallback = f"## Matches for: {topic}\n\n"
            for r in results[:5]:
                fallback += f"- {r.content[:200]}...\n"
            fallback += f"\n*Gemini summarization failed: {e}*"
            return fallback
```

### Step 4: Create SKILL.md

```markdown
---
name: cc-memory
description: User-level memory - search past sessions, recall facts. Use for context from previous conversations.
argument-hint: "<search|recent|summarize|add|forget> [query] [--limit N]"
---

# cc-memory

Claude Code memory skill - persistent context across sessions.

## Commands

### Search
Search across past sessions and extracted facts.
```
/memory search "authentication approach"
/memory search "database decision" --limit 5 --verbose
```

### Recent
List recent sessions with summaries.
```
/memory recent
/memory recent 10
```

### Summarize
Generate summary of a topic across sessions.
```
/memory summarize "project architecture"
```

### Add
Manually add a fact to memory.
```
/memory add "User prefers TypeScript"
/memory add "Always use PostgreSQL" --category preference
```

### Forget
Remove a fact from memory.
```
/memory forget abc123
```

### Sync
Refresh facts.md from database.
```
/memory sync
```

## How It Works

1. **SessionEnd**: Transcript archived, facts extracted via heuristics + Gemini
2. **SessionStart**: facts.md loaded into context
3. **Search**: Semantic search via Gemini embeddings
4. **Summarize**: Gemini generates cross-session summary

## Storage

All data stored at `~/claude_client/memory/`:
- `vault.db` - SQLite with embeddings
- `facts.md` - Human-readable facts
- `config.json` - Settings
- `conversations/archives/` - Archived transcripts
```

## Todo List

- [ ] Create main.py CLI router
- [ ] Implement cmd_search with MemorySearchHandler
- [ ] Implement cmd_recent
- [ ] Implement cmd_summarize with Gemini
- [ ] Implement cmd_add and cmd_forget
- [ ] Implement cmd_sync
- [ ] Create search_handler.py
- [ ] Create summarizer.py
- [ ] Update SKILL.md
- [ ] Test all commands

## Success Criteria

- [ ] `/memory search` returns relevant results
- [ ] `/memory recent` lists sessions
- [ ] `/memory summarize` generates Gemini summary
- [ ] `/memory add` stores fact in DB and facts.md
- [ ] `/memory forget` removes fact
- [ ] `/memory sync` rebuilds facts.md
