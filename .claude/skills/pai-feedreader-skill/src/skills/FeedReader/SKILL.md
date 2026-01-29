---
name: FeedReader
version: 1.0.0
description: Daily content aggregation from blogs and social media. USE WHEN user wants to check feeds, aggregate content, get daily digest, run feed reader, or manage followed URLs.
---

# FeedReader

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
| User feeds | `~/.claude/skills/FeedReader/feeds.yaml` | Your URL list |
| Content cache | `~/.claude/skills/FeedReader/cache.json` | Change detection data |
| Digest output | `~/.claude/History/digests/YYYY-MM-DD_digest.md` | Generated summaries |

## Integration

This skill delegates to:

- **BrightData Skill** → `FourTierScrape` workflow for reliable URL content retrieval
- **Research Skill** → `ExtractKnowledge` workflow for insight synthesis

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
User: "remove feed https://old-blog.com"
User: "list my feeds"
```

## Quick Start

1. Add feeds: `"add feed https://example.com/blog"`
2. Add more feeds as needed
3. Run: `"daily digest"`
4. Check output in `~/.claude/History/digests/`
