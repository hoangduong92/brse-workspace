# YouTube Transcript Extraction Usage

## Overview

Extract transcripts from YouTube videos using the `extractTranscript()` function or CLI command.

## TypeScript/JavaScript Usage

```typescript
import { extractTranscript } from './YouTubeHandler';

// Basic usage (default languages: en, ja, vi)
const transcript = await extractTranscript('dQw4w9WgXcQ');
console.log(transcript.text); // Full transcript
console.log(transcript.language); // "English"

// Custom languages
const transcript2 = await extractTranscript('9bZkp7q19f0', {
  languages: ['ko', 'en']
});

// Truncate to first 100 words for digest
const transcript3 = await extractTranscript('dQw4w9WgXcQ', {
  languages: ['en'],
  maxWords: 100
});

// Error handling
if (!transcript.success) {
  console.error('Failed:', transcript.error);
}
```

## CLI Usage

```bash
# Basic usage
bun run YouTubeHandler.ts transcript dQw4w9WgXcQ

# Specify languages
bun run YouTubeHandler.ts transcript dQw4w9WgXcQ en,ja,vi

# Multiple languages fallback
bun run YouTubeHandler.ts transcript 9bZkp7q19f0 ko,en
```

## Python Script Direct Usage

```bash
# Direct execution
python scripts/extract-transcript.py dQw4w9WgXcQ en

# Multiple languages
python scripts/extract-transcript.py 9bZkp7q19f0 ko,en,ja

# Default languages (en,ja,vi)
python scripts/extract-transcript.py jNQXAC9IVRw
```

## Response Format

```typescript
interface Transcript {
  success: boolean;
  text?: string;           // Full transcript as plain text
  language?: string;       // Language code (e.g., "English", "Korean (auto-generated)")
  video_id: string;        // Video ID
  error?: string;          // Error message if success=false
}
```

## Examples

### Success Response
```json
{
  "success": true,
  "text": "All right, so here we are, in front of the elephants...",
  "language": "English",
  "video_id": "jNQXAC9IVRw"
}
```

### Error Response (No Transcript)
```json
{
  "success": false,
  "error": "No transcripts were found for any of the requested language codes: ['en']...",
  "video_id": "aaaaaaaaaaa"
}
```

## Features

- **Multi-language support**: Specify priority-ordered language list
- **Automatic fallback**: Tries languages in order until one succeeds
- **Error handling**: Graceful failures with descriptive messages
- **Truncation**: Optional maxWords parameter for digest creation
- **Validation**: Video ID format check (11 alphanumeric chars)
- **Performance**: ~3s average, 30s timeout

## Integration with Feed Reader

```typescript
import { fetchChannelFeed, extractTranscript } from './YouTubeHandler';

// Fetch videos and extract transcripts
const videos = await fetchChannelFeed('UCBJycsmduvYEL83R_U4JriQ');

for (const video of videos.slice(0, 5)) {
  const transcript = await extractTranscript(video.id, {
    languages: ['en', 'ja'],
    maxWords: 500  // Limit for digest
  });

  if (transcript.success) {
    console.log(`${video.title}: ${transcript.text?.substring(0, 100)}...`);
  }

  // Rate limiting (recommended)
  await new Promise(resolve => setTimeout(resolve, 2000));
}
```

## Error Cases

1. **Invalid video ID**: Returns error before API call
2. **Video not found**: API error with description
3. **No transcript available**: Lists available languages
4. **Language mismatch**: Suggests alternatives
5. **Private/restricted video**: API error message

## Performance Tips

1. **Cache transcripts**: Store results to avoid repeated API calls
2. **Rate limiting**: Add 2s delay between requests
3. **Truncation**: Use maxWords for digest creation
4. **Language priority**: Put most common language first
5. **Batch processing**: Process videos sequentially, not parallel

## Testing

```bash
# Test with Rick Astley (487 words)
bun run YouTubeHandler.ts transcript dQw4w9WgXcQ

# Test with first YouTube video (short)
bun run YouTubeHandler.ts transcript jNQXAC9IVRw

# Test with Korean video
bun run YouTubeHandler.ts transcript 9bZkp7q19f0 ko

# Test error handling
bun run YouTubeHandler.ts transcript invalid
```

## Dependencies

- **Python**: 3.11+
- **youtube-transcript-api**: Installed globally or in venv
- **Bun/Node**: For TypeScript execution

## Limitations

- Requires video to have captions (auto-generated or manual)
- Uses YouTube's internal API (undocumented, may change)
- No authentication required (good for simple use cases)
- Rate limits unknown (recommend 2s delay between requests)
