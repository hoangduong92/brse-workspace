#!/usr/bin/env python3
"""Extract YouTube video transcripts via youtube-transcript-api"""
import sys
import json
import re
from youtube_transcript_api import YouTubeTranscriptApi

# Video ID validation pattern (11 alphanumeric chars + underscore + hyphen)
VIDEO_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{11}$')

def validate_video_id(video_id):
    """Validate YouTube video ID format for security"""
    if not VIDEO_ID_PATTERN.match(video_id):
        return False
    return True

def extract(video_id, languages=['en', 'ja', 'vi']):
    """
    Extract transcript for a YouTube video

    Args:
        video_id: YouTube video ID (11 alphanumeric characters)
        languages: Priority-ordered list of language codes

    Returns:
        dict with success status, text, language, and video_id
    """
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=languages)

        # transcript.snippets is the list of segments
        text = ' '.join([s.text for s in transcript.snippets])

        return {
            "success": True,
            "text": text,
            "language": transcript.language,
            "video_id": video_id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "video_id": video_id
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Missing video_id"}))
        sys.exit(1)

    video_id = sys.argv[1]

    # Validate video ID before processing (defense-in-depth)
    if not validate_video_id(video_id):
        print(json.dumps({
            "success": False,
            "error": "Invalid video ID format",
            "video_id": video_id[:20]  # Truncate to avoid log injection
        }))
        sys.exit(1)

    languages = sys.argv[2].split(',') if len(sys.argv) > 2 else ['en', 'ja', 'vi']
    result = extract(video_id, languages)
    print(json.dumps(result))
