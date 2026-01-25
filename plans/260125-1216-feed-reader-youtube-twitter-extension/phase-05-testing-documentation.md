# Phase 5: Testing & Documentation

## Context Links

- [plan.md](plan.md)
- [All phase files](.)

## Overview

| Priority | Status | Description |
|----------|--------|-------------|
| Medium | Pending | Test all components, update documentation |

## Requirements

### Testing
- [ ] Unit tests for YouTubeHandler
- [ ] Unit tests for TwitterScraper
- [ ] Integration test for full Digest workflow
- [ ] Edge case testing (invalid URLs, rate limits, etc.)

### Documentation
- [ ] Update skill.md with new capabilities
- [ ] Add troubleshooting guide
- [ ] Document maintenance procedures for Twitter scraper

## Test Cases

### YouTubeHandler

| Test | Input | Expected |
|------|-------|----------|
| extractChannelId - @handle | `youtube.com/@lexfridman` | `UCxxxxxx` |
| extractChannelId - channel URL | `youtube.com/channel/UCxxxxxx` | `UCxxxxxx` |
| fetchChannelFeed | Valid channel ID | Array of 10-15 videos |
| fetchChannelFeed - invalid | `invalid123` | Empty array + error |
| extractTranscript | `dQw4w9WgXcQ` | Transcript object |
| extractTranscript - no captions | Video without captions | `{ success: false, error: "..." }` |

### TwitterScraper

| Test | Input | Expected |
|------|-------|----------|
| scrapeTweets | `@karpathy` | Array of tweets |
| scrapeTweets - suspended | `@suspended_user` | Empty array + error |
| scrapeTweets - rate limited | Many requests | Retry logic triggered |

### Integration

| Test | Feeds | Expected |
|------|-------|----------|
| Mixed digest | 2 blogs, 1 YouTube, 1 Twitter | Complete digest with all sections |
| YouTube-only | 3 YouTube channels | YouTube section only |
| Failure recovery | 1 valid, 1 invalid | Digest generated with partial content |

## Implementation Steps

1. **Create test file structure**
   ```
   Tools/
   ├── __tests__/
   │   ├── YouTubeHandler.test.ts
   │   ├── TwitterScraper.test.ts
   │   └── integration.test.ts
   ```

2. **Write YouTubeHandler tests**
   - Mock HTTP responses for RSS
   - Mock Python subprocess for transcript

3. **Write TwitterScraper tests**
   - Mock Puppeteer responses
   - Test DOM extraction logic

4. **Update skill documentation**
   - Add YouTube usage examples
   - Add Twitter usage examples
   - Add troubleshooting section

## Todo List

- [ ] Create test directory structure
- [ ] Write YouTubeHandler unit tests
- [ ] Write TwitterScraper unit tests
- [ ] Write integration tests
- [ ] Run all tests, fix failures
- [ ] Update skill.md
- [ ] Add TROUBLESHOOTING.md
- [ ] Add MAINTENANCE.md for Twitter scraper

## Documentation Updates

### skill.md additions

```markdown
## YouTube Support

Add YouTube channels to your feeds:
```
add feed https://youtube.com/@lexfridman
```

Enable transcript extraction:
```yaml
- url: "https://youtube.com/@lexfridman"
  extract_transcripts: true
```

## Twitter Support

Add Twitter accounts:
```
add feed https://twitter.com/karpathy
```

**Note:** Twitter scraping requires maintenance. See MAINTENANCE.md.
```

### TROUBLESHOOTING.md

```markdown
# Troubleshooting

## YouTube

### "Could not extract channel ID"
- Ensure URL is valid YouTube channel
- Try channel URL format: youtube.com/channel/UCxxxxxx

### "No transcript available"
- Video may not have captions
- Check if video is age-restricted

## Twitter

### "Scraping failed - login wall"
- Clear browser cache
- Wait 1 hour, try again

### "Rate limited"
- Reduce number of Twitter feeds
- Increase delay between requests
```

## Success Criteria

1. All unit tests passing
2. Integration test with real feeds succeeds
3. Documentation covers all new features
4. Troubleshooting guide addresses common issues

## Next Steps

After Phase 5 completion:
- Deploy to production
- Monitor for first week
- Adjust Twitter scraper as needed
