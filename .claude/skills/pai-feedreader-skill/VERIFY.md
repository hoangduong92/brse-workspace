# FeedReader Skill - Verification Checklist

## Required Checks

Complete ALL of these before using the skill:

### 1. File Structure

- [ ] `~/.claude/skills/FeedReader/SKILL.md` exists
- [ ] `~/.claude/skills/FeedReader/Workflows/Digest.md` exists
- [ ] `~/.claude/skills/FeedReader/Workflows/AddFeed.md` exists
- [ ] `~/.claude/skills/FeedReader/Workflows/RemoveFeed.md` exists
- [ ] `~/.claude/skills/FeedReader/Workflows/ListFeeds.md` exists
- [ ] `~/.claude/skills/FeedReader/Tools/ContentCache.ts` exists
- [ ] `~/.claude/skills/FeedReader/Tools/FeedManager.ts` exists

### 2. User Configuration

- [ ] `~/.claude/skills/FeedReader/feeds.yaml` exists
- [ ] feeds.yaml contains at least one valid URL

### 3. Dependencies

- [ ] pai-brightdata-skill is installed
- [ ] pai-research-skill is installed
- [ ] Bun is installed (`bun --version`)
- [ ] Tool dependencies installed (`cd Tools && bun install`)

### 4. Output Directory

- [ ] `~/.claude/History/digests/` directory exists

## Quick Verification Commands

```bash
# Check skill files
ls -la ~/.claude/skills/FeedReader/

# Check feeds file
cat ~/.claude/skills/FeedReader/feeds.yaml

# Check dependencies
bun --version

# Check output directory
ls -la ~/.claude/History/digests/
```

## Functional Tests

### Test 1: List Feeds

Say: `"list my feeds"`

Expected: Shows contents of feeds.yaml with all URLs listed.

### Test 2: Add Feed

Say: `"add feed https://example.com/test"`

Expected: URL added to feeds.yaml, confirmation message shown.

### Test 3: Remove Feed

Say: `"remove feed https://example.com/test"`

Expected: URL removed from feeds.yaml, confirmation message shown.

### Test 4: Daily Digest (Full Test)

Say: `"daily digest"`

Expected:
1. Reads all feeds from feeds.yaml
2. Scrapes each URL using BrightData
3. Detects new content
4. Synthesizes insights
5. Saves digest to `~/.claude/History/digests/YYYY-MM-DD_digest.md`

## Verification Status

| Check | Status |
|-------|--------|
| File structure | |
| User configuration | |
| Dependencies | |
| Output directory | |
| List feeds test | |
| Add feed test | |
| Remove feed test | |
| Daily digest test | |

## Common Issues

### Issue: "feeds.yaml not found"

**Solution**: Copy template to user location:
```bash
cp ~/.claude/skills/FeedReader/Data/feeds.yaml ~/.claude/skills/FeedReader/feeds.yaml
```

### Issue: "Tool dependencies not installed"

**Solution**: Install Bun dependencies:
```bash
cd ~/.claude/skills/FeedReader/Tools && bun install
```

### Issue: "Digest file not created"

**Solution**: Create output directory:
```bash
mkdir -p ~/.claude/History/digests
```
