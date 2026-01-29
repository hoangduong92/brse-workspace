#!/usr/bin/env python3
"""
bk-tester: Generate Japanese test documentation from requirements.

Usage:
    python scripts/main.py --input requirements.md --type all
    python scripts/main.py --input requirements.md --type plan
    python scripts/main.py --input requirements.md --type viewpoint
    python scripts/main.py --input requirements.md --type cases
    python scripts/main.py --input requirements.md --type report
"""

import argparse
import sys
import io
from pathlib import Path

from viewpoint_extractor import extract_viewpoints
from test_case_generator import generate_test_cases
from test_plan_generator import generate_test_plan
from report_generator import generate_test_report


def read_file(filepath: str) -> str:
    """Read file content."""
    try:
        path = Path(filepath)
        if not path.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        return path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Japanese test documentation from requirements"
    )
    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='Path to requirements document'
    )
    parser.add_argument(
        '--type',
        '-t',
        required=True,
        choices=['all', 'plan', 'viewpoint', 'cases', 'report'],
        help='Type of document to generate'
    )
    parser.add_argument(
        '--project',
        '-p',
        default='プロジェクト',
        help='Project name (default: プロジェクト)'
    )
    parser.add_argument(
        '--viewpoints',
        '-v',
        help='Path to viewpoints document (for test cases generation)'
    )
    parser.add_argument(
        '--results',
        '-r',
        help='Path to test results (for report generation)'
    )

    args = parser.parse_args()

    # Read requirements
    requirements = read_file(args.input)

    # Read optional inputs
    viewpoints = None
    if args.viewpoints:
        viewpoints = read_file(args.viewpoints)

    test_results = None
    if args.results:
        test_results = read_file(args.results)

    # Generate prompts based on type
    if args.type == 'plan':
        prompt = generate_test_plan(requirements, args.project)
        print(prompt)

    elif args.type == 'viewpoint':
        prompt = extract_viewpoints(requirements)
        print(prompt)

    elif args.type == 'cases':
        prompt = generate_test_cases(requirements, viewpoints)
        print(prompt)

    elif args.type == 'report':
        prompt = generate_test_report(requirements, test_results, args.project)
        print(prompt)

    elif args.type == 'all':
        print("# Generating all test documents", file=sys.stderr)
        print("\n## 1. Test Plan", file=sys.stderr)
        print("Run: python scripts/main.py --input {} --type plan | claude -p > test_plan.md".format(args.input), file=sys.stderr)
        print("\n## 2. Test Viewpoints", file=sys.stderr)
        print("Run: python scripts/main.py --input {} --type viewpoint | claude -p > viewpoints.md".format(args.input), file=sys.stderr)
        print("\n## 3. Test Cases", file=sys.stderr)
        print("Run: python scripts/main.py --input {} --type cases --viewpoints viewpoints.md | claude -p > test_cases.md".format(args.input), file=sys.stderr)
        print("\n## 4. Test Report", file=sys.stderr)
        print("Run: python scripts/main.py --input {} --type report | claude -p > test_report.md".format(args.input), file=sys.stderr)
        print("\nUse --type to generate specific documents.", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    # Ensure UTF-8 encoding for stdout on Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    main()
