# PAI FeedReader Skill

Daily content aggregation from blogs, Twitter/X, newsletters, and more.

## Features

- **URL Management**: Add, remove, and organize feeds in YAML format
- **Smart Scraping**: Uses BrightData 4-tier fallback for reliable content retrieval
- **Change Detection**: Hash-based comparison to identify new content only
- **AI Synthesis**: Leverages Research skill to extract key insights
- **Daily Digest**: Generates organized markdown summaries

## Workflow

```
feeds.yaml → BrightData Scrape → Change Detection → Research Synthesis → Digest.md
```

## Quick Start

1. Install the skill (see [INSTALL.md](INSTALL.md))
2. Add your feeds: `"add feed https://example.com/blog"`
3. Run digest: `"daily digest"` or `"check feeds"`

## Commands

| Command | Description |
|---------|-------------|
| `daily digest` | Run full aggregation workflow |
| `check feeds` | Same as daily digest |
| `what's new` | Same as daily digest |
| `add feed [URL]` | Add new URL to follow |
| `remove feed [URL]` | Stop following a URL |
| `list feeds` | Show all followed URLs |

## Output

Digests are saved to: `~/.claude/History/digests/YYYY-MM-DD_digest.md`

## Dependencies

- `pai-brightdata-skill` - For reliable URL scraping
- `pai-research-skill` - For content synthesis

## Configuration

User feeds are stored in: `~/.claude/skills/FeedReader/feeds.yaml`

See [Data/feeds.yaml](src/skills/FeedReader/Data/feeds.yaml) for template format.
