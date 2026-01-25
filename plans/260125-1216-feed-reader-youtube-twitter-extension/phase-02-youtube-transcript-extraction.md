# Phase 2: YouTube Transcript Extraction

## Context Links

- [Research: YouTube Transcript Methods](../reports/researcher-260125-1206-youtube-transcript-methods.md)
- [Research: Fabric CLI](../reports/researcher-260125-1206-fabric-youtube-extraction.md)
- [Phase 1: YouTube RSS](phase-01-youtube-rss-integration.md)

## Overview

| Priority | Status | Description |
|----------|--------|-------------|
| High | ✅ Completed | Extract transcripts from YouTube videos using `youtube-transcript-api` |

## Key Insights

- `youtube-transcript-api` works without authentication (tested ✅)
- Uses YouTube's internal API - free but undocumented
- Returns timestamped segments
- Falls back gracefully when transcripts unavailable
- API changed: now uses `YouTubeTranscriptApi().fetch(video_id)`

## Requirements

### Functional
- [x] Extract transcript for given video ID
- [x] Support multiple languages (priority: en, ja, vi)
- [x] Convert transcript segments to plain text
- [x] Handle videos without transcripts gracefully

### Non-Functional
- [x] Timeout: 30s per video
- [ ] Rate limit: 2s delay between requests (deferred to integration phase)
- [ ] Cache transcripts for 24 hours (deferred to integration phase)

## Architecture

```
YouTubeHandler.ts (extend from Phase 1)
├── ... (existing from Phase 1)
└── extractTranscript(videoId: string, options?: TranscriptOptions): Promise<Transcript>

TranscriptOptions:
├── languages: string[]  (default: ['en', 'ja', 'vi'])
└── includeTimestamps: boolean (default: false)

Transcript:
├── videoId: string
├── language: string
├── text: string
├── segments?: TranscriptSegment[]
└── error?: string
```

## Related Code Files

### Modify
- `.claude/skills/feed-reader/Tools/YouTubeHandler.ts` - Add transcript extraction

### Create
- `.claude/skills/feed-reader/scripts/extract-transcript.py` - Python script wrapper

## Implementation Steps

1. **Create Python wrapper script**
   ```python
   # extract-transcript.py
   import sys
   import json
   from youtube_transcript_api import YouTubeTranscriptApi

   def extract(video_id, languages=['en', 'ja', 'vi']):
       try:
           ytt = YouTubeTranscriptApi()
           transcript = ytt.fetch(video_id, languages=languages)
           text = ' '.join([s.text for s in transcript.snippets])
           return {"success": True, "text": text, "language": transcript.language}
       except Exception as e:
           return {"success": False, "error": str(e)}

   if __name__ == "__main__":
       result = extract(sys.argv[1])
       print(json.dumps(result))
   ```

2. **Add TypeScript wrapper in YouTubeHandler.ts**
   ```typescript
   async function extractTranscript(videoId: string): Promise<Transcript> {
     const proc = Bun.spawn(["python", "scripts/extract-transcript.py", videoId]);
     const output = await new Response(proc.stdout).text();
     return JSON.parse(output);
   }
   ```

3. **Integrate with fetchChannelFeed**
   - For each new video, optionally extract transcript
   - Controlled by `extract_transcripts` flag in feeds.yaml

4. **Add caching layer**
   - Store transcripts in ContentCache with video ID as key
   - TTL: 24 hours (transcripts rarely change)

## Todo List

- [x] Create extract-transcript.py script
- [x] Test script with various video types
- [x] Add extractTranscript to YouTubeHandler.ts
- [ ] Add transcript caching (deferred to integration phase)
- [x] Handle edge cases (no transcript, private video, age-restricted)
- [x] Add language fallback logic
- [x] Integration test with real channels

## Success Criteria

1. Transcript extracted for 90%+ of public videos with captions
2. Graceful error handling for videos without transcripts
3. Cache prevents duplicate API calls
4. Performance: <5s per video transcript

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| API breaking changes | Pin youtube-transcript-api version, monitor releases |
| IP blocking | Add delays, use sparingly (only for new videos) |
| Large transcripts | Truncate to first 5000 words for digest |

## Security Considerations

- Validate video ID format (11 alphanumeric characters)
- Sanitize transcript output (remove HTML entities)

## Next Steps

Proceed to Phase 3 for Twitter scraper implementation.
