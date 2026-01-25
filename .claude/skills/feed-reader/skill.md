---
name: feed-reader
version: 1.0.0
description: Daily content aggregation from blogs and social media. USE WHEN user wants to check feeds, aggregate content, get daily digest, run feed reader, or manage followed URLs.
---

# feed-reader

Aggregates content from your followed URLs (blogs, Twitter/X, newsletters) and generates daily digests with key insights.

## Workflow Routing

| Trigger | Workflow | Description |
|---------|----------|-------------|
| "daily digest", "check feeds", "what's new", "run feed reader" | [Digest](Workflows/Digest.md) | Full aggregation: scrape → detect changes → synthesize → save |
| "add feed [URL]", "follow [URL]" | [AddFeed](Workflows/AddFeed.md) | Add new URL to feeds.yaml |
| "remove feed [URL]", "unfollow [URL]" | [RemoveFeed](Workflows/RemoveFeed.md) | Remove URL from feeds.yaml |
| "list feeds", "show feeds", "my feeds" | [ListFeeds](Workflows/ListFeeds.md) | Display all followed URLs |

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| User feeds | `~/.claude/skills/feed-reader/feeds.yaml` | Your URL list |
| Content cache | `~/.claude/skills/feed-reader/cache.json` | Change detection data |
| Digest output | `~/.claude/History/digests/YYYY-MM-DD_digest.md` | Generated summaries |

## Integration

This skill delegates to:

- **bright-data skill** → `FourTierScrape` workflow for reliable URL content retrieval
- **research skill** → `ExtractKnowledge` workflow for insight synthesis

## Supported Feed Sources

### YouTube Channels
Extract RSS feeds and transcripts from YouTube channels using multiple URL formats.

**Supported URL Formats:**
- Direct channel ID: `https://youtube.com/channel/UCSHZKyawb77ixDdsGog4iWA`
- Handle (@username): `https://youtube.com/@lexfridman`
- Custom name: `https://youtube.com/c/mkbhd`
- Legacy user format: `https://youtube.com/user/username`

**Features:**
- Automatic RSS feed extraction
- Video transcript extraction (en, ja, vi, and other languages)
- New video notifications in daily digest
- Transcript summaries in digest

**Example Commands:**
```
User: "add feed https://youtube.com/@lexfridman"
User: "add feed https://youtube.com/channel/UCSHZKyawb77ixDdsGog4iWA"
```

### Twitter/X Accounts
Scrape latest tweets and threads from Twitter/X accounts.

**Supported URL Formats:**
- Profile URL: `https://twitter.com/karpathy`
- X.com: `https://x.com/elonmusk`

**Features:**
- Latest tweet extraction with engagement metrics
- Thread reconstruction
- Rate limiting (10s between requests)
- Automatic retry with exponential backoff
- Login wall detection and recovery

**Limitations:**
- Browser automation required (Chromium/Puppeteer)
- May fail on heavily rate-limited requests
- Requires valid URL format

**Example Commands:**
```
User: "add feed https://twitter.com/karpathy"
User: "follow https://x.com/elonmusk"
```

### Blog & Newsletter Feeds
Scrape general web content from blogs and newsletters.

**Features:**
- HTML content extraction
- Multi-tier scraping (WebFetch → Curl → Browser → BrightData)
- Change detection for efficiency

## Examples

### Check for new content
```
User: "daily digest"
User: "check my feeds"
User: "what's new from my feeds?"
```

### Manage feeds
```
User: "add feed https://simonwillison.net/"
User: "follow https://twitter.com/karpathy"
User: "add feed https://youtube.com/@lexfridman"
User: "remove feed https://old-blog.com"
User: "list my feeds"
```

## Quick Start

1. Add feeds: `"add feed https://example.com/blog"`
2. Add YouTube channels: `"add feed https://youtube.com/@channel-name"`
3. Add Twitter accounts: `"follow https://twitter.com/username"`
4. Run: `"daily digest"`
5. Check output in `~/.claude/History/digests/`

## Troubleshooting

For common issues and solutions, see [TROUBLESHOOTING.md](Tools/TROUBLESHOOTING.md).

For Twitter scraper maintenance tasks, see [TWITTER_SCRAPER_MAINTENANCE.md](Tools/TWITTER_SCRAPER_MAINTENANCE.md).
