#!/bin/bash
# Integration test for transcript extraction

VIDEO_ID="${1:-dQw4w9WgXcQ}"
LANGUAGES="${2:-en,ja,vi}"

echo "Testing transcript extraction for video: $VIDEO_ID"
echo "Languages: $LANGUAGES"
echo "---"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/extract-transcript.py"

python "$PYTHON_SCRIPT" "$VIDEO_ID" "$LANGUAGES"
