#!/usr/bin/env python3
"""CC-Memory CLI - User-level memory for Claude Code."""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows encoding for Unicode output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add script dir and lib to path
_script_dir = Path(__file__).parent
sys.path.insert(0, str(_script_dir))
sys.path.insert(0, str(_script_dir.parent.parent / "lib"))

from memory_db import MemoryDB
from memory_store import MemoryStore, Session, Fact
from config_manager import ConfigManager
from fact_extractor import FactExtractor

# Try to import Gemini embedder
try:
    from vault import GeminiEmbedder
    EMBEDDER_AVAILABLE = True
except ImportError:
    EMBEDDER_AVAILABLE = False


def get_store() -> MemoryStore:
    """Get memory store with optional embedder."""
    embedder = None
    if EMBEDDER_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
        try:
            embedder = GeminiEmbedder()
        except Exception:
            pass
    return MemoryStore(embedder)


def cmd_search(args):
    """Search facts semantically."""
    store = get_store()
    query = " ".join(args.query)
    results = store.search_facts(query, top_k=args.limit)

    if not results:
        print(f"No results found for: {query}")
        return

    print(f"\n## Search Results for: \"{query}\"\n")
    for i, r in enumerate(results, 1):
        score_pct = int(r.score * 100)
        print(f"**{i}. [{r.fact.category or 'general'}]** {r.fact.content}")
        print(f"   Score: {score_pct}% | ID: `{r.fact.id}`")
        if r.session:
            print(f"   Session: {r.session.workspace_name or r.session.workspace}")
            print(f"   Resume: `claude --resume {r.session.session_id[:8]}`")
        print()


def cmd_recent(args):
    """List recent sessions."""
    store = get_store()
    sessions = store.get_recent_sessions(limit=args.limit)

    if not sessions:
        print("No sessions recorded yet.")
        return

    print(f"\n## Recent Sessions ({len(sessions)})\n")
    for s in sessions:
        time_str = s.start_time.strftime("%Y-%m-%d %H:%M") if s.start_time else "Unknown"
        ws_name = s.workspace_name or Path(s.workspace).name
        print(f"**{ws_name}** - {time_str}")
        print(f"   Messages: {s.message_count} | ID: `{s.session_id[:8]}`")
        if s.summary:
            print(f"   Summary: {s.summary[:100]}...")
        print(f"   Resume: `claude --resume {s.session_id}`")
        print()


def cmd_summarize(args):
    """Summarize facts about a topic."""
    store = get_store()
    topic = " ".join(args.topic)
    results = store.search_facts(topic, top_k=20, min_score=0.2)

    if not results:
        print(f"No facts found about: {topic}")
        return

    print(f"\n## Summary: {topic}\n")

    # Group by category
    by_category = {}
    for r in results:
        cat = r.fact.category or "general"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(r.fact)

    for category, facts in sorted(by_category.items()):
        print(f"### {category.title()}")
        for fact in facts[:5]:  # Max 5 per category
            print(f"- {fact.content}")
        print()


def cmd_add(args):
    """Manually add a fact."""
    store = get_store()
    content = " ".join(args.content)
    category = args.category or "context"

    fact = Fact(
        id=None,
        content=content,
        source_session=None,
        confidence=1.0,
        category=category
    )
    fact_id = store.add_fact(fact)

    print(f"✓ Fact added: `{fact_id}`")
    print(f"  Category: {category}")
    print(f"  Content: {content}")


def cmd_forget(args):
    """Delete a fact by ID."""
    store = get_store()
    success = store.delete_fact(args.fact_id)

    if success:
        print(f"✓ Fact deleted: `{args.fact_id}`")
    else:
        print(f"✗ Fact not found: `{args.fact_id}`")


def cmd_status(args):
    """Show memory status."""
    store = get_store()
    config = ConfigManager()

    session_count = store.count_sessions()
    fact_count = store.count_facts()
    memory_dir = MemoryDB.get_memory_dir()

    print("\n## Memory Status\n")
    print(f"**Storage:** `{memory_dir}`")
    print(f"**Sessions:** {session_count}")
    print(f"**Facts:** {fact_count}")
    print(f"**Extract Method:** {config.get('extract_method')}")
    print(f"**Auto Extract:** {config.get('auto_extract')}")

    # Check embedder
    embedder_status = "Available" if EMBEDDER_AVAILABLE and os.getenv("GOOGLE_API_KEY") else "Unavailable"
    print(f"**Semantic Search:** {embedder_status}")

    # Database size
    db_path = memory_dir / "vault.db"
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print(f"**Database Size:** {size_mb:.2f} MB")


def cmd_export(args):
    """Export facts to markdown."""
    store = get_store()
    path = store.export_facts_to_markdown()
    print(f"✓ Facts exported to: `{path}`")


def cmd_archive(args):
    """Archive current session (for hook integration)."""
    import shutil

    session_id = args.session_id
    transcript_path = args.transcript
    workspace = args.workspace or os.getcwd()

    if not transcript_path or not Path(transcript_path).exists():
        print(f"✗ Transcript not found: {transcript_path}")
        return

    store = get_store()
    memory_dir = MemoryDB.get_memory_dir()
    archives_dir = memory_dir / "conversations" / "archives"
    archives_dir.mkdir(parents=True, exist_ok=True)

    # Copy transcript to archives
    date_str = datetime.now().strftime("%Y%m%d")
    ws_name = Path(workspace).name
    archive_name = f"{date_str}-{ws_name}-{session_id[:8]}.jsonl"
    archive_path = archives_dir / archive_name
    shutil.copy(transcript_path, archive_path)

    # Parse transcript for message count and content
    content = ""
    message_count = 0
    try:
        with open(transcript_path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if "content" in entry:
                        content += entry.get("content", "") + "\n"
                        message_count += 1
                except json.JSONDecodeError:
                    pass
    except Exception:
        pass

    # Extract facts if auto_extract enabled
    config = ConfigManager()
    session_summary = None

    if config.get("auto_extract") and content and message_count >= config.get("min_session_messages", 5):
        extractor = FactExtractor(config)
        result = extractor.extract(content, session_id)

        for fact in result.facts:
            store.add_fact(fact)

        session_summary = result.session_summary
        print(f"  Extracted {len(result.facts)} facts ({result.method})")

    # Save session record
    session = Session(
        session_id=session_id,
        workspace=workspace,
        workspace_name=ws_name,
        start_time=datetime.now(),
        end_time=datetime.now(),
        summary=session_summary,
        message_count=message_count,
        archived_path=str(archive_path)
    )
    store.add_session(session)

    print(f"✓ Session archived: `{session_id[:8]}`")
    print(f"  Workspace: {ws_name}")
    print(f"  Messages: {message_count}")
    print(f"  Archive: {archive_path}")


def cmd_save(args):
    """Save current session to memory (uses env vars or finds transcript)."""
    import glob

    # Try to get session info from environment
    session_id = os.getenv("CK_SESSION_ID") or os.getenv("CLAUDE_SESSION_ID")
    workspace = os.getcwd()

    if not session_id:
        # Try to find the most recent transcript in Claude's data directory
        claude_dir = Path.home() / ".claude" / "projects"
        if claude_dir.exists():
            # Find project hash from workspace
            # Claude uses a hash of the workspace path
            import hashlib
            workspace_hash = hashlib.md5(workspace.encode()).hexdigest()[:8]

            # Find matching project folder or any recent transcript
            transcripts = list(claude_dir.glob("**/chat_*.jsonl"))
            if transcripts:
                # Get most recent
                transcripts.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                transcript_path = transcripts[0]
                # Extract session ID from filename
                session_id = transcript_path.stem.replace("chat_", "")
                print(f"Found recent transcript: {transcript_path.name}")
            else:
                print("✗ No transcripts found. Run from an active Claude Code session.")
                return
        else:
            print("✗ Claude data directory not found.")
            return

    # Find transcript path
    transcript_path = None
    claude_dir = Path.home() / ".claude" / "projects"
    if claude_dir.exists():
        # Search for transcript with this session ID
        matches = list(claude_dir.glob(f"**/chat_{session_id}*.jsonl"))
        if matches:
            transcript_path = str(matches[0])
        else:
            # Try to find any recent transcript
            transcripts = list(claude_dir.glob("**/chat_*.jsonl"))
            if transcripts:
                transcripts.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                transcript_path = str(transcripts[0])

    if not transcript_path or not Path(transcript_path).exists():
        print(f"✗ Transcript not found for session: {session_id}")
        return

    # Create args object for cmd_archive
    class ArchiveArgs:
        pass

    archive_args = ArchiveArgs()
    archive_args.session_id = session_id
    archive_args.transcript = transcript_path
    archive_args.workspace = workspace

    cmd_archive(archive_args)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CC-Memory - User-level memory for Claude Code"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # search
    p_search = subparsers.add_parser("search", help="Search facts semantically")
    p_search.add_argument("query", nargs="+", help="Search query")
    p_search.add_argument("--limit", "-l", type=int, default=10, help="Max results")

    # recent
    p_recent = subparsers.add_parser("recent", help="List recent sessions")
    p_recent.add_argument("limit", nargs="?", type=int, default=10, help="Number of sessions")

    # summarize
    p_summarize = subparsers.add_parser("summarize", help="Summarize topic")
    p_summarize.add_argument("topic", nargs="+", help="Topic to summarize")

    # add
    p_add = subparsers.add_parser("add", help="Add a fact manually")
    p_add.add_argument("content", nargs="+", help="Fact content")
    p_add.add_argument("--category", "-c", help="Fact category")

    # forget
    p_forget = subparsers.add_parser("forget", help="Delete a fact")
    p_forget.add_argument("fact_id", help="Fact ID to delete")

    # status
    subparsers.add_parser("status", help="Show memory status")

    # export
    subparsers.add_parser("export", help="Export facts to markdown")

    # archive (for hook integration)
    p_archive = subparsers.add_parser("archive", help="Archive a session")
    p_archive.add_argument("--session-id", required=True, help="Session ID")
    p_archive.add_argument("--transcript", required=True, help="Transcript path")
    p_archive.add_argument("--workspace", help="Workspace path")

    # save (manual save current session - uses env vars)
    p_save = subparsers.add_parser("save", help="Save current session to memory")
    p_save.add_argument("--extract", "-e", action="store_true", help="Extract facts from session")

    args = parser.parse_args()

    if not args.command:
        # Default to status
        args.command = "status"

    # Route to command handler
    handlers = {
        "search": cmd_search,
        "recent": cmd_recent,
        "summarize": cmd_summarize,
        "add": cmd_add,
        "forget": cmd_forget,
        "status": cmd_status,
        "export": cmd_export,
        "archive": cmd_archive,
        "save": cmd_save,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
