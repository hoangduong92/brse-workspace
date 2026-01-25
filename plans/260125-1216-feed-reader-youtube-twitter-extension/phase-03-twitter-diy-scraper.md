# Phase 3: Twitter DIY Scraper

## Context Links

- [Research: Twitter Integration](../reports/researcher-260125-1206-youtube-twitter-feed-integration.md)
- [Current FeedManager](../../.claude/skills/feed-reader/Tools/FeedManager.ts)

## Overview

| Priority | Status | Description |
|----------|--------|-------------|
| High | Complete (Untested) | DIY Twitter scraper using Puppeteer (budget: $0) |

**Code Review Findings (2026-01-25):**
- ✅ Implementation complete with Puppeteer v23.11.1
- ❌ **CRITICAL:** Browser resource leak if `handleRateLimit()` throws in catch block
- ❌ **HIGH:** Rate limit race condition (global state not thread-safe)
- ❌ **HIGH:** XSS risk if scraped content rendered in web UI (needs sanitization)
- ⚠️ No real-world testing with Twitter accounts
- ⚠️ Hardcoded Chrome UA will become outdated

## Key Insights

- Official Twitter API: $100-42k/month - too expensive
- Nitter: Broken since Jan 2024
- DIY approach: Puppeteer + guest tokens
- Expected maintenance: ~15 hrs/month
- Success rate target: ~80% (accept occasional failures)

## Requirements

### Functional
- [ ] Scrape latest N tweets from a user profile (default: 10)
- [ ] Extract: text, timestamp, media URLs, engagement metrics
- [ ] Handle threads (optional: expand "Show more" replies)
- [ ] Support rate limiting and retries

### Non-Functional
- [ ] Headless browser mode
- [ ] Memory cleanup after each session
- [ ] Timeout: 30s per profile
- [ ] Max 5 profiles per run (avoid detection)

## Architecture

```
TwitterScraper.ts
├── scrapeTweets(handle: string, count?: number): Promise<Tweet[]>
├── scrapeThread(tweetUrl: string): Promise<Tweet[]>
└── internal:
    ├── launchBrowser(): Browser
    ├── extractTweets(page: Page): Tweet[]
    └── handleRateLimit(error: Error): void

Tweet:
├── id: string
├── text: string
├── createdAt: string
├── author: string
├── likes: number
├── retweets: number
├── replies: number
├── mediaUrls: string[]
└── isThread: boolean
```

## Related Code Files

### Create
- `.claude/skills/feed-reader/Tools/TwitterScraper.ts`
- `.claude/skills/feed-reader/scripts/twitter-scraper.ts` (alternative: standalone script)

### Modify
- `.claude/skills/feed-reader/Tools/package.json` - Add puppeteer dependency

## Implementation Steps

1. **Install dependencies**
   ```bash
   cd .claude/skills/feed-reader/Tools
   bun add puppeteer
   ```

2. **Create TwitterScraper.ts**
   ```typescript
   import puppeteer from 'puppeteer';

   interface Tweet {
     id: string;
     text: string;
     createdAt: string;
     author: string;
     likes: number;
     retweets: number;
     replies: number;
     mediaUrls: string[];
   }

   export async function scrapeTweets(handle: string, count = 10): Promise<Tweet[]> {
     const browser = await puppeteer.launch({ headless: true });
     try {
       const page = await browser.newPage();
       await page.setViewport({ width: 1280, height: 800 });

       // Set user agent to avoid bot detection
       await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64)...');

       // Navigate to profile
       await page.goto(`https://twitter.com/${handle}`, {
         waitUntil: 'networkidle2',
         timeout: 30000
       });

       // Wait for tweets to load
       await page.waitForSelector('[data-testid="tweet"]', { timeout: 10000 });

       // Extract tweets
       const tweets = await page.evaluate(() => {
         // DOM extraction logic
       });

       return tweets.slice(0, count);
     } finally {
       await browser.close();
     }
   }
   ```

3. **Add retry logic with exponential backoff**
   - Retry 3 times on failure
   - Wait 5s, 15s, 45s between retries

4. **Add rate limiting**
   - Max 1 request per 10 seconds
   - Max 5 profiles per batch

5. **Handle common failure modes**
   - Login wall: Clear cookies, try guest mode
   - Rate limit (429): Wait 60s, retry once
   - Timeout: Log error, continue with other profiles

## Todo List

- [x] Install puppeteer
- [x] Create TwitterScraper.ts skeleton
- [x] Implement scrapeTweets function
- [x] Add tweet extraction logic (DOM selectors)
- [x] Implement retry logic
- [x] Add rate limiting
- [ ] Test with 5 different accounts (requires puppeteer runtime)
- [x] Document known failure modes
- [x] Add error logging

## Success Criteria

1. Successfully scrape 80%+ of attempts
2. Extract text, timestamp, engagement for each tweet
3. Handle login walls gracefully
4. Memory usage stays under 500MB per run

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Twitter changes DOM | High | Document selectors, easy to update |
| Account suspension | N/A | Using guest mode, no login |
| Chromium memory leaks | Medium | Proper cleanup, restart browser |
| Rate limiting | Medium | Delays, batch limits |

## Maintenance Notes

**Expected monthly tasks:**
- Week 1-2: Monitor for DOM changes
- Week 2-3: Update selectors if needed
- Week 4: Test and verify scraping works

**When scraping breaks:**
1. Check if Twitter updated UI
2. Inspect elements in browser
3. Update selectors in `extractTweets()`
4. Test with 3 profiles
5. Deploy fix

## Security Considerations

- No credential storage (guest mode only)
- Sanitize scraped content
- Don't store cookies between sessions
- Respect robots.txt (informational)

## Critical Fixes Required

**Before Production:**
1. Fix browser cleanup in catch block (move `handleRateLimit` out of try/catch)
2. Fix rate limit race condition with promise-based locking
3. Add text sanitization to prevent XSS
4. Test with 5+ real Twitter accounts to validate scraping works
5. Update user agent strategy to use Puppeteer's dynamic UA

**See:** [Code Review Report](../reports/code-reviewer-260125-1630-feed-reader-youtube-twitter-extension.md) sections 3, 5, 6, 9

## Next Steps

1. Fix critical browser resource leak
2. Test with real Twitter accounts
3. Document success rate baseline
4. Proceed to Phase 4 for Digest workflow integration
