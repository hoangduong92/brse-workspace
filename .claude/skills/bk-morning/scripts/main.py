#!/usr/bin/env python3
"""Main entry point for bk-morning skill."""
import argparse
import json
import os
import sys

# Add lib path for vault imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from vault import MorningBrief, SyncScheduler


def main():
    """Generate morning brief for BrSE."""
    parser = argparse.ArgumentParser(
        description="Generate morning brief with unread items and overnight updates"
    )
    parser.add_argument(
        "--project", "-p",
        default=os.getenv("BACKLOG_PROJECT_KEY"),
        help="Project key (default: $BACKLOG_PROJECT_KEY)"
    )
    parser.add_argument(
        "--unread-only",
        action="store_true",
        help="Show only unread counts"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output as JSON"
    )
    parser.add_argument(
        "--cutoff",
        type=int,
        default=18,
        help="Cutoff hour for overnight (default: 18)"
    )
    parser.add_argument(
        "--sync-status",
        action="store_true",
        help="Show sync status table"
    )

    args = parser.parse_args()

    if not args.project:
        print("Error: Project key required. Set BACKLOG_PROJECT_KEY or use --project")
        sys.exit(1)

    # Show sync status if requested
    if args.sync_status:
        scheduler = SyncScheduler(args.project)
        print(scheduler.format_status_table())
        return

    # Generate morning brief
    brief = MorningBrief(args.project, cutoff_hour=args.cutoff)

    if args.output_json:
        # JSON output
        data = brief.generate_brief_json()
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    elif args.unread_only:
        # Unread counts only
        unread = brief.get_unread_summary()
        total = sum(unread.values())
        print(f"Total unread: {total}")
        for source, count in unread.items():
            if count > 0:
                print(f"  {source}: {count}")
    else:
        # Full brief
        print(brief.generate_brief())


if __name__ == "__main__":
    main()
