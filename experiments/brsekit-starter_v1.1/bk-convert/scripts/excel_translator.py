"""Excel translator module - JA↔VI translation preserving formatting.

Uses xlwings (COM automation) for 100% format preservation including shapes.
Requires Excel installation (Windows/macOS only).

Usage:
    python scripts/excel_translator.py input.xlsx --to ja
    python scripts/excel_translator.py input.xlsx --to vi --glossary glossaries/custom.json
"""

import os
import sys
import time
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

# Platform check
if sys.platform not in ('win32', 'darwin'):
    print("⚠️ Excel translation requires Windows or macOS with Excel installed.")
    sys.exit(1)

try:
    import xlwings as xw
    from openai import OpenAI
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install xlwings openai python-dotenv")
    sys.exit(1)

# Load environment
load_dotenv()

# Constants
API_DELAY = 2  # seconds between API calls
BATCH_SIZE = 100  # max cells per batch


class ExcelTranslator:
    """Translate Excel files while preserving formatting."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        glossary: Optional[Dict[str, str]] = None,
        system_prompt: Optional[str] = None
    ):
        """Initialize translator.

        Args:
            api_key: Gemini API key (or from GEMINI_API_KEY env)
            glossary: Dictionary of term translations
            system_prompt: Custom system prompt for translation
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable required")

        self.client = OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=self.api_key,
        )
        self.glossary = glossary or {}
        self.system_prompt = system_prompt or self._load_default_prompt()

    def _load_default_prompt(self) -> str:
        """Load default system prompt from file."""
        prompt_file = Path(__file__).parent / "excel_system_prompt.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding='utf-8')
        return self._get_fallback_prompt()

    def _get_fallback_prompt(self) -> str:
        """Fallback prompt if file not found."""
        return """You are a specialized IT translator for software specifications and testing scenarios.
Your goal is to translate explanations while STRICTLY PRESERVING all technical identifiers.

CORE RULES:
1. Translate descriptive sentences, instructions, and general flow
2. DO NOT translate column names, file names, sheet names
3. DO NOT translate validation messages or error codes
4. Keep logic values: "NG", "OK", "True", "False", "Null"
5. Keep formats: "yyyy/mm/dd", "HH:mm"
6. Segments separated by "|||" must stay separated by "|||"

Output ONLY the translation, nothing else."""

    @staticmethod
    def clean_text(text: Any) -> str:
        """Clean and normalize text."""
        if not text or not isinstance(text, str):
            return ""
        return ' '.join(str(text).split()).strip()

    @staticmethod
    def should_translate(text: str) -> bool:
        """Check if text needs translation."""
        text = ExcelTranslator.clean_text(text)
        if not text or len(text) < 2:
            return False
        if re.match(r'^[\d\s,.\-]+$', text):  # numbers only
            return False
        if text.startswith('='):  # formula
            return False
        return True

    def _build_user_prompt(self, texts: List[str], target_lang: str) -> str:
        """Build user prompt with glossary context."""
        direction = "Vietnamese to Japanese" if target_lang == "ja" else "Japanese to Vietnamese"
        separator = "|||"
        combined = separator.join(texts)

        # Add glossary context if available
        glossary_note = ""
        if self.glossary:
            terms = "\n".join(f"- {k} → {v}" for k, v in list(self.glossary.items())[:50])
            glossary_note = f"\n\nGLOSSARY (use these exact translations):\n{terms}\n"

        return f"""Translate from {direction}, keeping segments separated by '|||'.
{glossary_note}
TEXT:
{combined}"""

    def translate_batch(self, texts: List[str], target_lang: str = "ja") -> List[str]:
        """Translate a batch of texts.

        Args:
            texts: List of texts to translate
            target_lang: Target language ('ja' or 'vi')

        Returns:
            List of translated texts
        """
        if not texts:
            return []

        try:
            response = self.client.chat.completions.create(
                model="gemini-2.5-flash-lite",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": self._build_user_prompt(texts, target_lang)}
                ]
            )

            translated = response.choices[0].message.content
            parts = translated.split("|||")

            # Handle count mismatch
            if len(parts) != len(texts):
                print(f"⚠️ Translation count mismatch: {len(parts)} vs {len(texts)}")
                if len(parts) < len(texts):
                    parts.extend(texts[len(parts):])
                else:
                    parts = parts[:len(texts)]

            time.sleep(API_DELAY)
            return parts

        except Exception as e:
            print(f"❌ Translation error: {e}")
            return texts  # fallback to original

    def _extract_shape_text(self, shape: Any) -> Optional[str]:
        """Extract text from Excel shape using multiple methods."""
        methods = [
            lambda s: s.TextFrame.Characters().Text if hasattr(s, 'TextFrame') and s.TextFrame.HasText else None,
            lambda s: s.TextFrame2.TextRange.Text if hasattr(s, 'TextFrame2') else None,
            lambda s: s.AlternativeText if hasattr(s, 'AlternativeText') and s.AlternativeText else None,
            lambda s: s.OLEFormat.Object.Text if hasattr(s, 'OLEFormat') and hasattr(s.OLEFormat, 'Object') and hasattr(s.OLEFormat.Object, 'Text') else None,
            lambda s: s.TextEffect.Text if hasattr(s, 'TextEffect') and hasattr(s.TextEffect, 'Text') else None,
        ]

        for method in methods:
            try:
                text = method(shape)
                if text:
                    return text
            except:
                continue
        return None

    def _update_shape_text(self, shape: Any, text: str) -> bool:
        """Update shape text using multiple methods."""
        methods = [
            lambda s, t: setattr(s.TextFrame.Characters(), 'Text', t) if hasattr(s, 'TextFrame') and s.TextFrame.HasText else None,
            lambda s, t: setattr(s.TextFrame2.TextRange, 'Text', t) if hasattr(s, 'TextFrame2') else None,
            lambda s, t: setattr(s, 'AlternativeText', t) if hasattr(s, 'AlternativeText') else None,
            lambda s, t: setattr(s.TextEffect, 'Text', t) if hasattr(s, 'TextEffect') and hasattr(s.TextEffect, 'Text') else None,
        ]

        for method in methods:
            try:
                method(shape, text)
                return True
            except:
                continue
        return False

    def translate_file(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        target_lang: str = "ja"
    ) -> Optional[str]:
        """Translate Excel file.

        Args:
            input_path: Path to input Excel file
            output_path: Path to output file (auto-generated if None)
            target_lang: Target language ('ja' or 'vi')

        Returns:
            Output file path or None on error
        """
        input_path = Path(input_path)
        if not input_path.exists():
            print(f"❌ File not found: {input_path}")
            return None

        # Generate output path
        if not output_path:
            output_dir = input_path.parent / "output"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{input_path.stem}-translated{input_path.suffix}"
        output_path = Path(output_path)

        print(f"\n🔄 Processing: {input_path.name}")
        print(f"🎯 Target: {'Japanese' if target_lang == 'ja' else 'Vietnamese'}")

        app = xw.App(visible=False)
        wb = None

        try:
            wb = app.books.open(str(input_path))

            for sheet in wb.sheets:
                print(f"📋 Sheet: {sheet.name}")
                texts_to_translate = []
                cell_refs = []

                # Collect cell texts
                used_range = sheet.used_range
                if used_range.count > 1 or used_range.value is not None:
                    for cell in used_range:
                        val = str(cell.value) if cell.value is not None else ""
                        if val and self.should_translate(val):
                            texts_to_translate.append(self.clean_text(val))
                            cell_refs.append(('cell', cell))

                # Collect shape texts
                try:
                    shapes = sheet.api.Shapes
                    if shapes.Count > 0:
                        print(f"📊 Found {shapes.Count} shapes")
                        for i in range(1, shapes.Count + 1):
                            try:
                                shape = shapes.Item(i)
                                text = self._extract_shape_text(shape)
                                if text and self.should_translate(text):
                                    texts_to_translate.append(self.clean_text(text))
                                    cell_refs.append(('shape', sheet, i))
                            except Exception as e:
                                continue
                except Exception as e:
                    print(f"⚠️ Shape processing error: {e}")

                if not texts_to_translate:
                    print(f"   ✅ No text to translate")
                    continue

                # Batch translate
                total_batches = (len(texts_to_translate) - 1) // BATCH_SIZE + 1
                print(f"   📦 {len(texts_to_translate)} texts in {total_batches} batches")

                for i in range(0, len(texts_to_translate), BATCH_SIZE):
                    batch_texts = texts_to_translate[i:i+BATCH_SIZE]
                    batch_refs = cell_refs[i:i+BATCH_SIZE]
                    batch_num = i // BATCH_SIZE + 1

                    print(f"   🔄 Batch {batch_num}/{total_batches}")
                    translated = self.translate_batch(batch_texts, target_lang)

                    # Update cells/shapes
                    for j, ref in enumerate(batch_refs):
                        if j >= len(translated) or not translated[j]:
                            continue

                        try:
                            if ref[0] == 'cell':
                                ref[1].value = translated[j]
                            elif ref[0] == 'shape':
                                _, sheet_obj, shape_idx = ref
                                shape = sheet_obj.api.Shapes.Item(shape_idx)
                                self._update_shape_text(shape, translated[j])
                        except Exception as e:
                            print(f"   ⚠️ Update error: {e}")

            # Save
            print(f"\n💾 Saving: {output_path}")
            wb.save(str(output_path))
            print(f"✅ Done: {output_path}")
            return str(output_path)

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

        finally:
            if wb:
                try:
                    wb.close()
                except:
                    pass
            if app:
                try:
                    app.quit()
                except:
                    pass


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Translate Excel files JA↔VI')
    parser.add_argument('input', help='Input Excel file path')
    parser.add_argument('--to', choices=['ja', 'vi'], default='ja',
                        help='Target language (default: ja)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--glossary', '-g', help='Glossary JSON file path')

    args = parser.parse_args()

    # Load glossary if provided
    glossary = {}
    if args.glossary:
        glossary_path = Path(args.glossary)
        if glossary_path.exists():
            import json
            glossary = json.loads(glossary_path.read_text(encoding='utf-8'))
            print(f"📖 Loaded {len(glossary)} glossary terms")

    # Translate
    translator = ExcelTranslator(glossary=glossary)
    result = translator.translate_file(args.input, args.output, args.to)

    if result:
        print(f"\n✅ Translation complete: {result}")
    else:
        print("\n❌ Translation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
