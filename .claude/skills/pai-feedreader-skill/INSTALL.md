# FeedReader Skill - Installation Guide

## Prerequisites

Before installing, ensure you have:

1. **pai-brightdata-skill** installed and verified
2. **pai-research-skill** installed and verified
3. **Bun** runtime installed (`bun --version`)

## Installation Steps

### Step 1: Copy Skill Files

Copy the skill directory to your Claude skills folder:

```bash
# Create destination if not exists
mkdir -p ~/.claude/skills/FeedReader

# Copy skill files
cp -r src/skills/FeedReader/* ~/.claude/skills/FeedReader/
```

### Step 2: Install Tool Dependencies

```bash
cd ~/.claude/skills/FeedReader/Tools
bun install
```

### Step 3: Create User Feeds File

Create your personal feeds file:

```bash
mkdir -p ~/.claude/skills/FeedReader
cp ~/.claude/skills/FeedReader/Data/feeds.yaml ~/.claude/skills/FeedReader/feeds.yaml
```

Edit `~/.claude/skills/FeedReader/feeds.yaml` to add your URLs.

### Step 4: Create Output Directory

```bash
mkdir -p ~/.claude/History/digests
```

### Step 5: Verify Installation

Run the verification checklist in [VERIFY.md](VERIFY.md).

## Configuration

### feeds.yaml Format

```yaml
feeds:
  - url: "https://example.com/blog"
    name: "Example Blog"
    category: blog        # blog, twitter, newsletter, youtube
    priority: high        # high, medium, low
    notes: "Optional notes"
```

### Categories

| Category | Description |
|----------|-------------|
| `blog` | Personal/company blogs |
| `twitter` | Twitter/X profiles |
| `newsletter` | Email newsletters with web archives |
| `youtube` | YouTube channels |

### Priority

- `high`: Always include in digest, process first
- `medium`: Include if time permits
- `low`: Include only in extensive digests

## Troubleshooting

### "Cannot find feeds.yaml"

Ensure the file exists at `~/.claude/skills/FeedReader/feeds.yaml`

### "BrightData skill not found"

Install pai-brightdata-skill first.

### "Scraping failed for Twitter URLs"

Twitter/X requires Tier 3 (Browser) or Tier 4 (Bright Data API). Ensure pai-browser-skill is installed or Bright Data MCP is configured.

## Uninstallation

```bash
rm -rf ~/.claude/skills/FeedReader
```

Note: This will remove your feeds.yaml. Back it up first if needed.
