#!/usr/bin/env python3
"""bk-capture CLI - Capture tasks and meeting minutes."""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from classifiers import PMClassifier, PriorityDetector
from vault_saver import VaultSaver, CapturedItem


def read_input(input_arg: str) -> str:
    """Read input from file or return as text."""
    if os.path.isfile(input_arg):
        with open(input_arg, "r", encoding="utf-8") as f:
            return f.read()
    return input_arg


def cmd_task(args):
    """Handle task capture command."""
    text = read_input(args.input)

    classifier = PMClassifier()
    priority_detector = PriorityDetector()

    # Classify and detect priority/deadline
    item_type, confidence = classifier.classify(text)
    priority, deadline = priority_detector.detect(text)

    # Create captured item
    item = CapturedItem(
        content=text,
        item_type=item_type.value,
        source="task",
        priority=priority.value,
        deadline=deadline.isoformat() if deadline else None
    )

    # Save to vault (async)
    saver = VaultSaver()
    saver.save([item], source="task")

    # Output
    print("## Captured Task\n")
    print(f"**Type:** {item_type.value} ({confidence:.0%} confidence)")
    print(f"**Priority:** {priority.value}")
    if deadline:
        print(f"**Deadline:** {deadline}")
    print(f"\n**Content:**\n{text[:500]}")

    if not args.no_confirm:
        print("\n---")
        print("Review above. To create on Backlog, run: /bk-capture task --create")


def cmd_meeting(args):
    """Handle meeting minutes capture."""
    text = read_input(args.input)

    classifier = PMClassifier()
    priority_detector = PriorityDetector()

    # Split into lines and classify each
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    items = []

    for line in lines:
        if len(line) < 5:  # Skip very short lines
            continue

        item_type, _ = classifier.classify(line)
        priority, deadline = priority_detector.detect(line)

        items.append(CapturedItem(
            content=line,
            item_type=item_type.value,
            source="meeting",
            priority=priority.value,
            deadline=deadline.isoformat() if deadline else None
        ))

    # Save to vault
    saver = VaultSaver()
    saver.save(items, source="meeting")

    # Group by type
    by_type = {}
    for item in items:
        if item.item_type not in by_type:
            by_type[item.item_type] = []
        by_type[item.item_type].append(item)

    # Output
    print("## Meeting Minutes Capture\n")
    print(f"**Total items:** {len(items)}\n")

    for item_type, type_items in by_type.items():
        print(f"### {item_type.title()} ({len(type_items)})")
        for item in type_items[:5]:
            priority_badge = "[HIGH]" if item.priority == "high" else ""
            print(f"- {priority_badge} {item.content[:80]}")
        print()


def cmd_email(args):
    """Handle email capture."""
    text = read_input(args.input)

    # Email usually becomes task
    classifier = PMClassifier()
    priority_detector = PriorityDetector()

    item_type, confidence = classifier.classify(text)
    priority, deadline = priority_detector.detect(text)

    item = CapturedItem(
        content=text,
        item_type=item_type.value,
        source="email",
        priority=priority.value,
        deadline=deadline.isoformat() if deadline else None
    )

    saver = VaultSaver()
    saver.save([item], source="email")

    print("## Email Captured\n")
    print(f"**Type:** {item_type.value}")
    print(f"**Priority:** {priority.value}")
    if deadline:
        print(f"**Deadline:** {deadline}")
    print(f"\n**Content preview:**\n{text[:300]}...")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="bk-capture - Capture tasks and meeting minutes"
    )
    subparsers = parser.add_subparsers(dest="command")

    # task command
    task_parser = subparsers.add_parser("task", help="Capture task from text")
    task_parser.add_argument("input", help="Text or file path")
    task_parser.add_argument("--no-confirm", action="store_true")
    task_parser.set_defaults(func=cmd_task)

    # meeting command
    meeting_parser = subparsers.add_parser("meeting", help="Capture meeting minutes")
    meeting_parser.add_argument("input", help="Transcript text or file path")
    meeting_parser.set_defaults(func=cmd_meeting)

    # email command
    email_parser = subparsers.add_parser("email", help="Capture email as task")
    email_parser.add_argument("input", help="Email text or file path")
    email_parser.set_defaults(func=cmd_email)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
