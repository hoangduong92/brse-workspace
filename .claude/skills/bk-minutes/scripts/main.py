"""Entry point for bk-minutes skill.

Parse meeting transcript into structured meeting minutes.
Supports text input directly or video/audio via ai-multimodal transcription.
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Fix Windows console encoding for Japanese characters
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mm_parser import MeetingParser
from mm_generator import MMGenerator


def load_dotenv_file():
    """Load .env file from skill directory."""
    skill_dir = Path(__file__).parent.parent
    env_file = skill_dir / ".env"

    if env_file.exists():
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def get_input_text(args) -> str:
    """Get input text from file, stdin, or direct argument."""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)

        # Check if media file - need transcription
        ext = file_path.suffix.lower()
        media_extensions = {'.mp4', '.webm', '.mov', '.mp3', '.wav', '.m4a'}

        if ext in media_extensions:
            return transcribe_media(file_path)
        else:
            return file_path.read_text(encoding="utf-8")

    elif args.text:
        return args.text

    elif not sys.stdin.isatty():
        return sys.stdin.read()

    return ""


def transcribe_media(file_path: Path) -> str:
    """Transcribe media file using ai-multimodal skill."""
    print(f"Transcribing {file_path}...")

    # Find ai-multimodal script
    skills_dir = Path(__file__).parent.parent.parent
    transcribe_script = skills_dir / "ai-multimodal" / "scripts" / "gemini_batch_process.py"

    if not transcribe_script.exists():
        print("Error: ai-multimodal skill not found")
        print("Please install ai-multimodal skill for video/audio transcription")
        sys.exit(1)

    import subprocess

    # Get venv python
    venv_python = skills_dir / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = skills_dir / ".venv" / "bin" / "python3"

    # Prompt designed for meeting transcription with speaker detection
    transcribe_prompt = """Transcribe the audio exactly as spoken.

Rules:
- Use original language (Japanese/Vietnamese/English)
- Label speakers as "Speaker 1:", "Speaker 2:" etc. (use names only if clearly stated in audio)
- Add timestamps in [MM:SS] format at start of each speaker turn
- One line per speaker turn
- Keep filler words (えーっと, あの, ừm, etc.)

Example format:
[00:00] Speaker 1: こんにちは。今日は進捗について話します。
[00:15] Speaker 2: はい、お願いします。
"""
    result = subprocess.run(
        [
            str(venv_python),
            str(transcribe_script),
            "--files", str(file_path),
            "--task", "transcribe",
            "--model", "gemini-2.5-pro",
            "--prompt", transcribe_prompt,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    if result.returncode != 0:
        print(f"Transcription failed: {result.stderr}")
        sys.exit(1)

    # Extract transcript from output
    output = result.stdout
    # Find the Result section
    if "Result:" in output:
        transcript = output.split("Result:")[-1].strip()
        return transcript

    return output


def main():
    """Run meeting minutes generation."""
    parser = argparse.ArgumentParser(
        description="Generate meeting minutes from transcript"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Input file (transcript .txt, video .mp4, audio .mp3)"
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        help="Direct text input"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Custom meeting title"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview mode - show summary only"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    args = parser.parse_args()

    # Load env
    load_dotenv_file()

    # Get input
    text = get_input_text(args)

    if not text or not text.strip():
        print("Error: No input provided")
        print("\nUsage:")
        print("  bk-minutes --file transcript.txt")
        print("  bk-minutes --file meeting.mp4  # requires ai-multimodal")
        print("  echo 'transcript' | bk-minutes")
        sys.exit(1)

    # Parse transcript
    meeting_parser = MeetingParser()
    minutes = meeting_parser.parse(text)

    # Generate output
    generator = MMGenerator()

    if args.dry_run:
        # Preview only
        preview = generator.generate_preview(minutes)
        print(preview)

        counts = minutes.item_count()
        print(f"Parse completed: {sum(counts.values())} items found")
        return

    if args.json:
        # JSON output
        output = json.dumps(minutes.to_dict(), ensure_ascii=False, indent=2)
    else:
        # Markdown output
        output = generator.generate(minutes, args.title)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
        print(f"Meeting minutes saved to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
