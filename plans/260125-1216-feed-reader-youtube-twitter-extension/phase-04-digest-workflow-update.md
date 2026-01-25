# Phase 4: Digest Workflow Update

## Context Links

- [Current Digest Workflow](../../.claude/skills/feed-reader/Workflows/Digest.md)
- [Phase 1: YouTube RSS](phase-01-youtube-rss-integration.md)
- [Phase 2: YouTube Transcripts](phase-02-youtube-transcript-extraction.md)
- [Phase 3: Twitter Scraper](phase-03-twitter-diy-scraper.md)

## Overview

| Priority | Status | Description |
|----------|--------|-------------|
| High | Completed | Update Digest workflow to use YouTube/Twitter handlers |

## Key Insights

- Current workflow uses BrightData for all scraping
- Need to route YouTube/Twitter to specialized handlers
- Maintain backward compatibility with existing feeds

## Requirements

### Functional
- [ ] Route YouTube feeds to YouTubeHandler
- [ ] Route Twitter feeds to TwitterScraper
- [ ] Fallback to BrightData for other categories
- [ ] Merge all content into unified digest format

### Non-Functional
- [ ] Process YouTube first (fastest)
- [ ] Process Twitter with delays (avoid detection)
- [ ] Total runtime target: <5 minutes for 20 feeds

## Architecture

```
Digest Workflow (updated)
┌─────────────────────────────────────────────────────┐
│ Step 3: Scrape Each URL (MODIFIED)                  │
│                                                     │
│ if (feed.category === "youtube"):                   │
│   → YouTubeHandler.fetchChannelFeed(channelId)      │
│   → if (extract_transcripts):                       │
│       → YouTubeHandler.extractTranscript(videoId)   │
│                                                     │
│ elif (feed.category === "twitter"):                 │
│   → TwitterScraper.scrapeTweets(handle)             │
│                                                     │
│ else:                                               │
│   → BrightData.FourTierScrape(url)                  │
└─────────────────────────────────────────────────────┘
```

## Related Code Files

### Modify
- `.claude/skills/feed-reader/Workflows/Digest.md` - Add routing logic

## Implementation Steps

1. **Update Step 3 in Digest.md**
   - Add category-based routing
   - Document YouTube-specific handling
   - Document Twitter-specific handling

2. **Update Step 7 (Digest Generation)**
   - Add YouTube section with video titles + transcript summaries
   - Add Twitter section with tweet highlights
   - Keep existing sections for blogs/newsletters

3. **Add error handling per category**
   - YouTube failure: Log, skip to next feed
   - Twitter failure: Log, note in digest
   - Don't block entire digest on single failure

4. **Update digest markdown template**
   ```markdown
   ## YouTube (N new videos)

   ### [Channel Name]
   **New video:** [Title]
   > Transcript summary (first 200 words)...

   [Watch on YouTube](link)

   ---

   ## Twitter/X (N new)

   ### @username
   > Latest tweet content...

   📊 12 likes · 3 retweets
   [View on Twitter](link)
   ```

## Todo List

- [x] Update Digest.md Step 3 with routing logic
- [x] Update Digest.md Step 7 with new sections
- [x] Add YouTube section template
- [x] Add Twitter section template
- [x] Add category-specific error handling
- [ ] Test full workflow with mixed feeds
- [ ] Verify error handling doesn't break digest

## Success Criteria

1. YouTube feeds processed via YouTubeHandler
2. Twitter feeds processed via TwitterScraper
3. Failed feeds don't block entire digest
4. Digest includes all content types in proper sections

## Security Considerations

- Sanitize all scraped content before including in digest
- Don't expose internal error details in digest output

## Next Steps

Proceed to Phase 5 for testing and documentation.
