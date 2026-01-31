#!/usr/bin/env python3
"""bk-recall CLI - Memory layer for BrseKit."""
import argparse
import sys
import os

# Add scripts to path for relative imports
sys.path.insert(0, os.path.dirname(__file__))

from sync_manager import SyncManager
from search_handler import SearchHandler
from summarizer import Summarizer


def cmd_sync(args):
    """Handle sync command."""
    manager = SyncManager()

    if args.source:
        result = manager.sync(
            args.source,
            project_key=args.project,
            limit=args.limit
        )
        print(f"Synced {result.get('synced', 0)} items from {args.source}")
        if result.get("error"):
            print(f"Error: {result['error']}")
    else:
        result = manager.sync_all(limit=args.limit)
        print(f"Total synced: {result.get('total_synced', 0)} items")
        for src, src_result in result.get("sources", {}).items():
            status = f"{src_result.get('synced', 0)} items"
            if src_result.get("error"):
                status += f" (error: {src_result['error']})"
            print(f"  - {src}: {status}")


def cmd_search(args):
    """Handle search command."""
    handler = SearchHandler()
    results = handler.query(
        args.query,
        source=args.source,
        top_k=args.limit
    )
    output = handler.format_results(results, verbose=args.verbose)
    print(output)


def cmd_summary(args):
    """Handle summary command."""
    summarizer = Summarizer()
    summary = summarizer.summarize(
        topic=args.topic,
        source=args.source,
        top_k=args.limit
    )
    print(summary)


def cmd_list(args):
    """Handle list command."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))
    from vault import VaultStore

    store = VaultStore()
    source = args.source or "backlog"
    items = store.list_by_source(source, limit=args.limit)

    if not items:
        print(f"No items found for source: {source}")
        return

    print(f"## Recent items from {source} ({len(items)} shown)\n")
    for item in items:
        title = item.title or "(No title)"
        snippet = item.content[:100].replace("\n", " ") if item.content else ""
        print(f"- **{title}**: {snippet}...")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="bk-recall - Memory layer for BrseKit",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync from sources")
    sync_parser.add_argument("source", nargs="?", help="Source to sync (email, backlog)")
    sync_parser.add_argument("--project", "-p", help="Backlog project key")
    sync_parser.add_argument("--limit", "-l", type=int, default=50, help="Max items")
    sync_parser.set_defaults(func=cmd_sync)

    # search command
    search_parser = subparsers.add_parser("search", help="Search vault")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--source", "-s", help="Filter by source")
    search_parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    search_parser.add_argument("--verbose", "-v", action="store_true", help="Show full content")
    search_parser.set_defaults(func=cmd_search)

    # summary command
    summary_parser = subparsers.add_parser("summary", help="Generate summary")
    summary_parser.add_argument("topic", nargs="?", help="Topic to summarize")
    summary_parser.add_argument("--source", "-s", help="Filter by source")
    summary_parser.add_argument("--limit", "-l", type=int, default=10, help="Max items")
    summary_parser.set_defaults(func=cmd_summary)

    # list command
    list_parser = subparsers.add_parser("list", help="List recent items")
    list_parser.add_argument("--source", "-s", help="Source to list")
    list_parser.add_argument("--limit", "-l", type=int, default=20, help="Max items")
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
