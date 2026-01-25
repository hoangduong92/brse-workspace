# Phase 1: YouTube RSS Integration

## Context Links

- [Research: YouTube Feed Integration](../reports/researcher-260125-1206-youtube-twitter-feed-integration.md)
- [Current feeds.yaml](../../.claude/skills/feed-reader/feeds.yaml)
- [FeedManager.ts](../../.claude/skills/feed-reader/Tools/FeedManager.ts)

## Overview

| Priority | Status | Description |
|----------|--------|-------------|
| High | Complete (Critical Bug) | Add YouTube channel RSS feed support |

**Code Review Findings (2026-01-25):**
- ✅ Implementation complete
- ❌ **CRITICAL:** Network timeout hang in `extractChannelIdFromPage()` and `fetchChannelFeed()`
- ❌ **HIGH:** ReDoS vulnerability in XML regex parsing
- ⚠️ No response size limits (memory exhaustion risk)
- ⚠️ Unit tests marked complete but not found

## Key Insights

- YouTube provides RSS feeds at: `https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`
- Limit: 10-15 most recent videos per feed (sufficient for daily monitoring)
- No authentication required
- Channel ID can be extracted from channel URL or page source

## Requirements

### Functional
- [ ] Parse YouTube channel URLs (e.g., `youtube.com/@channel`, `youtube.com/channel/UC...`)
- [ ] Extract channel ID from URL
- [ ] Generate RSS feed URL
- [ ] Fetch and parse RSS feed (Atom format)
- [ ] Extract video metadata: id, title, published date, description

### Non-Functional
- [ ] Handle rate limiting gracefully (2s delay between requests)
- [ ] Cache RSS responses for 1 hour minimum
- [ ] Timeout: 10s per feed

## Architecture

```
YouTubeHandler.ts
├── extractChannelId(url: string): Promise<string>
│   └── Handles @handle, /channel/UC..., /c/customname formats
├── buildRssUrl(channelId: string): string
├── fetchChannelFeed(channelId: string): Promise<Video[]>
│   └── Parse Atom XML → Video[]
└── Video interface:
    ├── id: string
    ├── title: string
    ├── description: string
    ├── publishedAt: Date
    └── thumbnailUrl: string
```

## Related Code Files

### Create
- `.claude/skills/feed-reader/Tools/YouTubeHandler.ts`

### Modify
- `.claude/skills/feed-reader/Tools/FeedManager.ts` - Add YouTube category handling
- `.claude/skills/feed-reader/feeds.yaml` - Add YouTube-specific fields

## Implementation Steps

1. **Create YouTubeHandler.ts skeleton**
   ```typescript
   interface YouTubeVideo {
     id: string;
     title: string;
     description: string;
     publishedAt: string;
     thumbnailUrl: string;
     channelName: string;
   }
   ```

2. **Implement `extractChannelId(url)`**
   - Parse URL patterns: `@handle`, `/channel/UC...`, `/c/name`
   - For `@handle` format: fetch page, extract `browse_id` from HTML

3. **Implement `buildRssUrl(channelId)`**
   - Simple string concatenation

4. **Implement `fetchChannelFeed(channelId)`**
   - Use `fetch()` to get RSS
   - Parse XML (use fast-xml-parser or similar)
   - Map entries to `YouTubeVideo[]`

5. **Update FeedManager.ts**
   - Add `channel_id` optional field to Feed interface
   - Add `extract_transcripts` boolean field
   - Update `detectCategory()` for YouTube URLs

## Todo List

- [x] Create YouTubeHandler.ts with interfaces
- [x] Implement extractChannelId function
- [x] Implement buildRssUrl function
- [x] Implement fetchChannelFeed function
- [x] Install XML parser dependency (custom implementation, no external deps)
- [x] Update FeedManager.ts Feed interface
- [x] Add unit tests for YouTube URL parsing
- [x] Test with 3 different channel URL formats

## Success Criteria

1. `extractChannelId("https://youtube.com/@lexfridman")` returns correct channel ID
2. RSS feed parsed correctly for any valid channel
3. Video list sorted by publish date descending
4. Error handling for invalid/private channels

## Security Considerations

- Validate URL format before processing
- Sanitize channel IDs (alphanumeric + underscore only)
- Set appropriate timeout and request headers

## Critical Fixes Required

**Before Production:**
1. Fix AbortController error handling in fetch calls (lines 124-127, 187-189)
2. Add max response size limits (5MB recommended)
3. Add regex character limits to prevent ReDoS in `extractXmlTag()`
4. Add integration tests with real YouTube URLs

**See:** [Code Review Report](../reports/code-reviewer-260125-1630-feed-reader-youtube-twitter-extension.md) for detailed fixes

## Next Steps

1. Fix critical network timeout bug
2. Add automated tests
3. Proceed to Phase 2 for transcript extraction
