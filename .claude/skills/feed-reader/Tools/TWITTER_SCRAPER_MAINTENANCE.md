# Twitter Scraper Maintenance Guide

## Overview
DIY Twitter scraper using Puppeteer for $0 budget.
Target uptime: ~80% (accept occasional failures).
Expected maintenance: ~15 hours/month.

## DOM Selectors (as of Jan 2025)

### Tweet Container
```typescript
document.querySelectorAll('[data-testid="tweet"]')
```

### Tweet Components
| Element | Selector | What it extracts |
|---------|----------|------------------|
| Text | `[data-testid="tweetText"]` | Tweet content |
| ID | `a[href*="/status/"]` → extract from href | Tweet ID |
| Timestamp | `time` element → `datetime` attribute | ISO timestamp |
| Author | `[data-testid="User-Name"] a` → href | Username |
| Metrics | `[role="group"] button` → `aria-label` | Likes, retweets, replies |
| Media | `img[src*="media"]` | Image/video URLs |
| Thread indicator | `[data-testid="tweet-text-show-more-link"]` | Is thread? |

### Login Wall Detection
```typescript
page.$('[data-testid="login"]')
```

## When Scraping Breaks

### Symptoms
- Empty tweet arrays returned
- Error: "Timeout waiting for [data-testid='tweet']"
- Missing fields in extracted tweets
- All metrics = 0

### Diagnosis Steps

1. **Check if Twitter updated UI**
   ```bash
   # Open browser and navigate to any profile
   # Right-click → Inspect → Elements tab
   https://twitter.com/elonmusk
   ```

2. **Inspect tweet elements**
   - Look for tweet containers (usually `<article>` tags)
   - Find data-testid attributes
   - Check if selectors changed

3. **Update selectors in code**
   Edit: `.claude/skills/feed-reader/Tools/twitter-dom-extractor.ts`

   ```typescript
   // OLD (if broken):
   const tweetElements = document.querySelectorAll('[data-testid="tweet"]');

   // NEW (example if changed to "post"):
   const tweetElements = document.querySelectorAll('[data-testid="post"]');
   ```

4. **Test with 3 profiles**
   ```bash
   cd .claude/skills/feed-reader/scripts
   bun run twitter-scraper-test.ts
   ```

5. **Deploy fix**
   - Commit changes
   - Update this maintenance guide with new selectors
   - Document changes in changelog

## Selector Update Checklist

When updating selectors:

- [ ] Update `twitter-dom-extractor.ts`
- [ ] Test with 3 different accounts
- [ ] Verify all fields extract correctly:
  - [ ] Tweet ID
  - [ ] Text content
  - [ ] Timestamp
  - [ ] Author
  - [ ] Likes count
  - [ ] Retweets count
  - [ ] Replies count
  - [ ] Media URLs
  - [ ] Thread detection
- [ ] Update this guide with new selectors
- [ ] Add entry to changelog with date and changes

## Common Issues

### Issue: Login Wall Appears
**Solution**: Already handled in code. Clears cookies and retries.
**File**: `TwitterScraper.ts` → `handleLoginWall()`

### Issue: Rate Limiting (429)
**Solution**: Already handled. Waits 60s and retries.
**File**: `twitter-retry-handler.ts` → `handleRateLimit()`

### Issue: Memory Leaks
**Symptoms**: Process memory grows over time
**Solution**:
1. Check browser.close() in finally blocks
2. Restart scraper process after 100 profiles
3. Monitor with: `process.memoryUsage()`

### Issue: Timeout Errors
**Symptoms**: "Navigation timeout exceeded"
**Solutions**:
1. Increase timeout in TwitterScraper.ts:
   ```typescript
   await page.goto(url, { timeout: 60000 }); // 60s instead of 30s
   ```
2. Check internet connection
3. Check if Twitter is down

## Monthly Maintenance Tasks

### Week 1-2: Monitor
- Run test script daily
- Check success rate (target: 80%+)
- Monitor error logs for patterns

### Week 2-3: Update if Needed
- If success rate drops below 80%, investigate
- Update selectors if Twitter changed UI
- Test fixes

### Week 4: Verify
- Run comprehensive tests
- Validate data quality
- Document any changes

## Performance Benchmarks

Target metrics:
- Memory usage: < 500MB per run
- Scrape time: < 30s per profile
- Success rate: > 80%
- Rate limit: 1 request per 10s
- Max batch size: 5 profiles

## Files to Monitor

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `twitter-dom-extractor.ts` | DOM selectors | When Twitter updates UI |
| `TwitterScraper.ts` | Browser config | When Puppeteer updates |
| `twitter-retry-handler.ts` | Rate limits | If rate limits change |

## Testing Accounts

Recommended test accounts (public figures with active profiles):
1. @elonmusk - High volume
2. @OpenAI - Medium volume
3. @github - Tech focus
4. @TwitterDev - Twitter official
5. @vercel - Medium volume

## Emergency Rollback

If update breaks scraping:

1. Revert to previous commit:
   ```bash
   git log --oneline -10  # Find last working commit
   git checkout <commit-hash> -- Tools/twitter-dom-extractor.ts
   ```

2. Test immediately:
   ```bash
   bun run scripts/twitter-scraper-test.ts
   ```

3. Investigate issue offline before re-deploying fix

## Contact

For questions or issues:
- Check implementation report: `plans/reports/fullstack-developer-260125-1229-twitter-scraper.md`
- Review phase plan: `plans/260125-1216-feed-reader-youtube-twitter-extension/phase-03-twitter-diy-scraper.md`
