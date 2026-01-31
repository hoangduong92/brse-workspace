"""JA↔VI translation prompt generator with glossary support.

Usage:
    # Text translation (pipe to Claude)
    python scripts/main.py --text "テストを実施しました" | claude -p
    python scripts/main.py --file input.txt --glossary glossaries/default-it-terms.json | claude -p

    # Excel translation (direct via Gemini API)
    python scripts/main.py excel input.xlsx --to ja
    python scripts/main.py excel input.xlsx --to vi --glossary glossaries/custom.json

    # PowerPoint translation (direct via Gemini API)
    python scripts/main.py pptx input.pptx --to ja
    python scripts/main.py pptx input.pptx --to vi --glossary glossaries/custom.json
"""

import argparse
import json
import re
import sys
import io
from pathlib import Path
from typing import Tuple, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'backlog' / 'scripts'))

from language_detector import LanguageDetector
from models import Language
from glossary_manager import GlossaryManager


class TextProcessor:
    """Process text for translation by extracting code blocks and URLs."""

    def __init__(self):
        """Initialize text processor."""
        self.code_blocks: List[str] = []
        self.urls: List[str] = []

    def extract_code_blocks(self, text: str) -> str:
        """Extract code blocks and replace with placeholders.

        Args:
            text: Input text with potential code blocks

        Returns:
            Text with code blocks replaced by [CODE_N] placeholders
        """
        # Pattern for triple-backtick code blocks
        pattern = r'```[\w]*\n(.*?)```'
        matches = list(re.finditer(pattern, text, re.DOTALL))

        result = text
        for i, match in enumerate(reversed(matches)):
            self.code_blocks.insert(0, match.group(0))
            result = result[:match.start()] + f'[CODE_{len(matches)-i-1}]' + result[match.end():]

        # Pattern for inline code
        inline_pattern = r'`([^`]+)`'
        inline_matches = list(re.finditer(inline_pattern, result))

        for i, match in enumerate(reversed(inline_matches)):
            code_index = len(self.code_blocks)
            self.code_blocks.append(match.group(0))
            result = result[:match.start()] + f'[CODE_{code_index}]' + result[match.end():]

        return result

    def extract_urls(self, text: str) -> str:
        """Extract URLs and replace with placeholders.

        Args:
            text: Input text with potential URLs

        Returns:
            Text with URLs replaced by [URL_N] placeholders
        """
        # Pattern for URLs (http/https)
        pattern = r'https?://[^\s\)\]\}]+'
        matches = list(re.finditer(pattern, text))

        result = text
        for i, match in enumerate(reversed(matches)):
            self.urls.insert(0, match.group(0))
            result = result[:match.start()] + f'[URL_{len(matches)-i-1}]' + result[match.end():]

        return result

    def process(self, text: str) -> str:
        """Process text by extracting code blocks and URLs.

        Args:
            text: Input text to process

        Returns:
            Processed text with placeholders
        """
        self.code_blocks = []
        self.urls = []

        text = self.extract_code_blocks(text)
        text = self.extract_urls(text)

        return text

    def get_preservation_note(self) -> str:
        """Get note about preserved elements for prompt.

        Returns:
            Note listing preserved elements
        """
        notes = []
        if self.code_blocks:
            notes.append(f"- {len(self.code_blocks)} code block(s): " + ", ".join(f"[CODE_{i}]" for i in range(len(self.code_blocks))))
        if self.urls:
            notes.append(f"- {len(self.urls)} URL(s): " + ", ".join(f"[URL_{i}]" for i in range(len(self.urls))))

        if notes:
            return "## Preserved Elements (DO NOT translate):\n" + "\n".join(notes) + "\n\n"
        return ""


def build_translation_prompt(
    text: str,
    source_lang: Language,
    target_lang: Language,
    glossary_text: str,
    preservation_note: str
) -> str:
    """Build translation prompt with glossary context.

    Args:
        text: Text to translate
        source_lang: Source language
        target_lang: Target language
        glossary_text: Formatted glossary terms
        preservation_note: Note about preserved elements

    Returns:
        Complete translation prompt
    """
    source_name = "Japanese" if source_lang == Language.JAPANESE else "Vietnamese"
    target_name = "Vietnamese" if target_lang == Language.VIETNAMESE else "Japanese"

    prompt = f"""You are a professional {source_name}↔{target_name} translator for IT projects.

## Glossary (MUST use these exact translations):
{glossary_text}

{preservation_note}## Instructions:
- Translate from {source_name} to {target_name}
- Use glossary terms exactly as specified
- Preserve all [CODE_N] and [URL_N] placeholders exactly as they appear
- Maintain the same formatting and structure
- For technical terms not in glossary, use standard IT terminology

## Text to Translate:
{text}

## Output:
Provide ONLY the translated text without any explanations or notes.
"""
    return prompt


def handle_text_translation(args):
    """Handle text translation (pipe to Claude)."""
    # Get input text
    if args.text:
        input_text = args.text
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        input_text = file_path.read_text(encoding='utf-8')
    else:
        print("Error: Either --text or --file must be provided", file=sys.stderr)
        sys.exit(1)

    # Detect language
    source_lang = LanguageDetector.detect(input_text)
    target_lang = LanguageDetector.get_target_language(source_lang)

    # Load glossary
    glossary_manager = GlossaryManager()
    glossary_path = Path(__file__).parent.parent / args.glossary

    if glossary_path.exists():
        try:
            glossary_manager.load(str(glossary_path))
        except Exception as e:
            print(f"Warning: Failed to load glossary: {e}", file=sys.stderr)
    else:
        print(f"Warning: Glossary file not found: {glossary_path}", file=sys.stderr)

    glossary_text = glossary_manager.format_for_prompt()

    # Process text
    processor = TextProcessor()
    processed_text = processor.process(input_text)
    preservation_note = processor.get_preservation_note()

    # Build and output prompt
    prompt = build_translation_prompt(
        processed_text,
        source_lang,
        target_lang,
        glossary_text,
        preservation_note
    )

    print(prompt)


def handle_excel_translation(args):
    """Handle Excel translation (direct via Gemini API)."""
    try:
        from excel_translator import ExcelTranslator
    except ImportError:
        print("Error: Excel translation requires xlwings and openai packages.", file=sys.stderr)
        print("Install with: pip install xlwings openai python-dotenv", file=sys.stderr)
        sys.exit(1)

    # Load glossary if provided
    glossary = {}
    glossary_path = Path(__file__).parent.parent / args.glossary
    if glossary_path.exists():
        try:
            glossary = json.loads(glossary_path.read_text(encoding='utf-8'))
            print(f"Loaded {len(glossary)} glossary terms", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Failed to load glossary: {e}", file=sys.stderr)

    # Translate
    translator = ExcelTranslator(glossary=glossary)
    result = translator.translate_file(args.input, args.output, args.to)

    if result:
        print(f"Translation complete: {result}")
    else:
        print("Translation failed", file=sys.stderr)
        sys.exit(1)


def handle_pptx_translation(args):
    """Handle PowerPoint translation (direct via Gemini API)."""
    try:
        from pptx_translator import PptxTranslator
    except ImportError:
        print("Error: PPTX translation requires python-pptx and openai packages.", file=sys.stderr)
        print("Install with: pip install python-pptx openai python-dotenv", file=sys.stderr)
        sys.exit(1)

    # Load glossary if provided
    glossary = {}
    glossary_path = Path(__file__).parent.parent / args.glossary
    if glossary_path.exists():
        try:
            glossary = json.loads(glossary_path.read_text(encoding='utf-8'))
            print(f"Loaded {len(glossary)} glossary terms", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Failed to load glossary: {e}", file=sys.stderr)

    # Translate
    translator = PptxTranslator(glossary=glossary)
    result = translator.translate_file(args.input, args.output, args.to)

    if result:
        print(f"Translation complete: {result}")
    else:
        print("Translation failed", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for translation prompt generator."""
    # Ensure UTF-8 output on Windows when running as script
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parser = argparse.ArgumentParser(
        description='JA↔VI translation tool with glossary support'
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Text translation (default behavior)
    parser.add_argument(
        '--text',
        type=str,
        help='Text to translate (inline)'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='File containing text to translate'
    )
    parser.add_argument(
        '--glossary',
        type=str,
        default='glossaries/default-it-terms.json',
        help='Path to glossary JSON file (default: glossaries/default-it-terms.json)'
    )

    # Excel subcommand
    excel_parser = subparsers.add_parser('excel', help='Translate Excel files preserving formatting')
    excel_parser.add_argument('input', help='Input Excel file path (.xlsx, .xls)')
    excel_parser.add_argument('--to', choices=['ja', 'vi'], default='ja',
                              help='Target language (default: ja)')
    excel_parser.add_argument('--output', '-o', help='Output file path (default: input/output/)')
    excel_parser.add_argument('--glossary', '-g', default='glossaries/default-it-terms.json',
                              help='Glossary JSON file path')

    # PowerPoint subcommand
    pptx_parser = subparsers.add_parser('pptx', help='Translate PowerPoint files preserving formatting')
    pptx_parser.add_argument('input', help='Input PPTX file path')
    pptx_parser.add_argument('--to', choices=['ja', 'vi'], default='ja',
                             help='Target language (default: ja)')
    pptx_parser.add_argument('--output', '-o', help='Output file path (default: input/output/)')
    pptx_parser.add_argument('--glossary', '-g', default='glossaries/default-it-terms.json',
                             help='Glossary JSON file path')

    args = parser.parse_args()

    # Route to appropriate handler
    if args.command == 'excel':
        handle_excel_translation(args)
    elif args.command == 'pptx':
        handle_pptx_translation(args)
    elif args.text or args.file:
        handle_text_translation(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
