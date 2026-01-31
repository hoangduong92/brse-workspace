#!/usr/bin/env python3
"""Entry point for bk-write skill.

Usage:
    python main.py --type email-client --level polite --input data.json
    echo '{"recipient": "田中様"}' | python main.py --type email-client
"""

import argparse
import io
import json
import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))

from japanese_writer import JapaneseWriter, DocumentType
from keigo_helper import KeigoLevel


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate Japanese business documents")
    parser.add_argument(
        "--type", "-t",
        required=True,
        choices=["email-client", "email-internal", "report-issue", "design-doc"],
        help="Document type to generate"
    )
    parser.add_argument(
        "--level", "-l",
        default="polite",
        choices=["casual", "polite", "honorific"],
        help="Keigo formality level (default: polite)"
    )
    parser.add_argument(
        "--input", "-i",
        help="JSON file with document data (use stdin if not provided)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (stdout if not provided)"
    )
    return parser.parse_args()


def load_input(input_path: str | None) -> dict:
    """Load input from file or stdin."""
    if input_path:
        with open(input_path, encoding="utf-8") as f:
            return json.load(f)
    if not sys.stdin.isatty():
        return json.load(sys.stdin)
    return {}


def main():
    """Main entry point."""
    args = parse_args()

    try:
        data = load_input(args.input)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Input file not found - {args.input}", file=sys.stderr)
        sys.exit(1)

    writer = JapaneseWriter()
    try:
        doc_type = DocumentType.from_string(args.type)
        level = KeigoLevel.from_string(args.level)
        result = writer.generate(doc_type=doc_type, level=level, **data)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Document saved to: {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()