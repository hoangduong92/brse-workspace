#!/usr/bin/env python3
"""bk-spec CLI - Requirement analysis and test generation."""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from analyzer import RequirementsAnalyzer, GapDetector
from tester import ViewpointExtractor, TestCaseGenerator


def read_input(input_arg: str) -> str:
    """Read input from file or return as text."""
    if os.path.isfile(input_arg):
        with open(input_arg, "r", encoding="utf-8") as f:
            return f.read()
    return input_arg


def cmd_analyze(args):
    """Handle analyze command."""
    text = read_input(args.input)

    analyzer = RequirementsAnalyzer()
    gap_detector = GapDetector()

    # Analyze requirements
    result = analyzer.analyze(text)
    gaps = gap_detector.detect(text)

    # Output
    print(analyzer.format_analysis(result))
    print()
    print(gap_detector.format_gaps(gaps))


def cmd_test(args):
    """Handle test command."""
    text = read_input(args.input)

    viewpoint = ViewpointExtractor()
    case_gen = TestCaseGenerator()

    doc_type = args.type

    if doc_type in ["viewpoint", "all"]:
        viewpoints = viewpoint.extract(text)
        print(viewpoint.format_table(viewpoints))
        print()

    if doc_type in ["cases", "all"]:
        cases = case_gen.generate(text)
        print(case_gen.format_cases(cases))
        print()

    if doc_type == "plan":
        # Simple test plan output
        print("# テスト計画書 (Test Plan)\n")
        print("## 1. テスト概要")
        print("本テスト計画は、要件に基づくテスト実施方針を定める。\n")
        print("## 2. テスト範囲")
        print("- 機能テスト")
        print("- 境界値テスト")
        print("- 異常系テスト\n")
        print("## 3. テストスケジュール")
        print("- 設計: TBD")
        print("- 実施: TBD")
        print("- 報告: TBD\n")


def cmd_feature(args):
    """Handle feature command."""
    feature = args.feature

    print(f"# Feature Analysis: {feature}\n")

    analyzer = RequirementsAnalyzer()
    viewpoint = ViewpointExtractor()
    case_gen = TestCaseGenerator()

    # Generate analysis for feature
    viewpoints = viewpoint.extract(feature)
    cases = case_gen.generate(feature, feature=feature)

    print("## Viewpoints")
    print(viewpoint.format_table(viewpoints))
    print()
    print("## Test Cases")
    print(case_gen.format_cases(cases))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="bk-spec - Requirement analysis and test generation"
    )
    subparsers = parser.add_subparsers(dest="command")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze requirements")
    analyze_parser.add_argument("input", help="Requirements text or file")
    analyze_parser.set_defaults(func=cmd_analyze)

    # test command
    test_parser = subparsers.add_parser("test", help="Generate test documents")
    test_parser.add_argument("input", help="Requirements text or file")
    test_parser.add_argument("--type", "-t", choices=["plan", "viewpoint", "cases", "all"],
                             default="all", help="Document type")
    test_parser.set_defaults(func=cmd_test)

    # feature command
    feature_parser = subparsers.add_parser("feature", help="Analyze specific feature")
    feature_parser.add_argument("feature", help="Feature name or description")
    feature_parser.set_defaults(func=cmd_feature)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
