# Twitter/X Scraper Maintenance Guide

Regular maintenance tasks for keeping the Twitter scraper working reliably.

## Monthly Maintenance Checklist

### 1. DOM Selector Verification (Every 2 weeks)

Twitter/X regularly updates their DOM structure. Test these selectors monthly:

```bash
# Test with 3 popular accounts to verify selectors still work
bun run TwitterScraper.ts scrape twitter 5
bun run TwitterScraper.ts scrape elonmusk 5
bun run TwitterScraper.ts scrape karpathy 5
```

**Selectors to verify in twitter-dom-extractor.ts:**
- `[data-testid="tweet"]` - Main tweet container
- `[data-testid="tweetText"]` - Tweet text content
- `[data-testid="User-Name"]` - Author name/handle
- `[data-testid="login"]` - Login wall detection
- `a[href*="/status/"]` - Tweet URL for ID extraction
- `time` - Timestamp element

**If selectors fail:**
1. Open Twitter in browser
2. Inspect element (F12 Developer Tools)
3. Find current selector in HTML
4. Update selector in twitter-dom-extractor.ts
5. Test again

### 2. Rate Limiting Review

Monitor rate limit performance:

```bash
# Check current rate limit settings in twitter-retry-handler.ts
# Default: 10 seconds between requests (MIN_REQUEST_INTERVAL)
```

**Current settings:**
- Request interval: 10 seconds
- Retry delays: [5s, 15s, 45s]
- Rate limit threshold: HTTP 429

**If you see many rate limit errors:**
1. Increase MIN_REQUEST_INTERVAL to 30-60 seconds
2. Add jitter to avoid synchronized requests
3. Implement backoff multiplier: `5s * (1.5 ^ attempt)`

### 3. Login Wall Handling Test

Verify login wall detection and recovery:

```bash
# Test with account that often triggers login wall
bun run TwitterScraper.ts scrape newaccount 3
```

**Expected behavior:**
1. Detects login wall: `[data-testid="login"]`
2. Clears cookies
3. Reloads page
4. Retries extraction

**If login wall handling fails:**
1. Check `handleLoginWall()` in TwitterScraper.ts
2. Verify cookie clearing: `page.deleteCookie(...)`
3. Test page reload: `page.reload({ waitUntil: 'networkidle2' })`

### 4. Dependency Updates

Check and update packages monthly:

```bash
cd .claude/skills/feed-reader/Tools
npm outdated
npm update
```

**Critical packages to monitor:**
- `puppeteer` - Browser automation (updates frequently)
- `yaml` - Feed YAML parsing
- TypeScript types (`@types/node`, `@types/bun`)

**When to update puppeteer:**
- New Chromium security patches
- Breaking changes to API (check changelog)
- Performance improvements

**Backward compatibility check:**
- After update, test all scrapers
- Verify selectors still work
- Check error handling

### 5. Error Pattern Monitoring

Track error patterns to identify trends:

**Common error types to monitor:**
- `429` (Rate limit) - Increasing? Adjust delays
- `403` (Forbidden) - IP flagged? Use VPN/proxy
- `404` (Not found) - Accounts deleted? Clean feeds.yaml
- Browser crashes - Low memory? Reduce batch size
- Timeout errors - Network issues? Increase timeout

**Quarterly analysis:**
1. Collect error logs from digests
2. Count error frequency by type
3. Identify if specific accounts trigger errors
4. Adjust configuration accordingly

## Performance Optimization

### Batch Size Optimization

Current: 5-10 profiles per batch with 10s delays

**Profile size impact:**
- Small profile (< 5K followers): ~2-3 seconds
- Medium profile (5K-100K): ~5-8 seconds
- Large profile (100K+): ~8-15 seconds

**Recommended batching:**
```
Small:   10 profiles max
Medium:  5-7 profiles max
Large:   3-5 profiles max
```

### Memory Management

Browser memory usage per profile: ~30-50 MB

**Optimization:**
1. Close browser after each profile
2. Don't keep multiple browsers open
3. Monitor memory growth over time
4. Restart if memory > 500MB

### Retry Strategy Fine-tuning

Current exponential backoff: [5s, 15s, 45s]

**Adjust for different failure types:**
- Rate limit (429): Use backoff [10s, 30s, 60s]
- Network error (timeout): Use backoff [5s, 15s, 45s]
- Server error (500+): Use backoff [5s, 15s, 45s]

## Quarterly Deep Dive

Every 3 months, conduct detailed review:

### 1. DOM Selector Audit

Test ALL selectors with multiple accounts:

```javascript
// Log all extracted selectors to verify accuracy
const tweets = await extractTweetsFromPage(page);
tweets.forEach(tweet => {
  console.log('Tweet:', {
    id: tweet.id.length === 19 ? 'VALID' : 'INVALID',
    text: tweet.text.length > 0 ? 'VALID' : 'INVALID',
    author: tweet.author.length > 0 ? 'VALID' : 'INVALID',
    metrics: tweet.likes + tweet.retweets + tweet.replies > 0 ? 'VALID' : 'NO_ENGAGEMENT',
  });
});
```

### 2. Network Performance Analysis

Profile network requests:

```bash
# Monitor network timing in browser DevTools
# Check:
# - Page load time (should be < 10s)
# - JavaScript parsing time
# - Rendering time
```

**Optimize if:**
- Load time > 15 seconds: Increase timeout
- Memory leaks: Check page.close() calls
- Too many requests: Reduce wait strategies

### 3. Security Review

Check for security issues:

**Areas to review:**
- User-Agent string (current, not blocklisted)
- Headers and fingerprinting
- Cookie handling
- Authentication bypass attempts
- Login detection accuracy

**Keep User-Agent current:**
```
Current: Chrome 120.0.0.0 (as of 2025-01)
Check:   https://www.useragentstring.com/
Update:  When Chrome version changes significantly
```

### 4. Documentation Update

Review and update:
- This maintenance guide
- TROUBLESHOOTING.md
- Error messages and solutions
- Known limitations

## Emergency Response

### Twitter/X API Changes

If scraper stops working:

1. **Check if X changed DOM:**
   ```bash
   # Open Twitter in browser, inspect element
   # Check if [data-testid="tweet"] still exists
   # Compare with github issues/discussions
   ```

2. **Verify using different approach:**
   - Try accessing via x.com vs twitter.com
   - Check if private browsing works
   - Test with VPN

3. **Fallback to official API:**
   - Twitter API (paid, limited free tier)
   - Alternative: Use browser extension or tool
   - Migrate away from Twitter feeds if needed

### Performance Degradation

If scraper becomes very slow:

1. **Check Twitter service status:**
   - Is Twitter.com slow for everyone?
   - Check status page

2. **Verify network:**
   - Test: `curl https://twitter.com`
   - Check latency: `ping twitter.com`

3. **Reduce concurrency:**
   - Decrease batch size
   - Increase delays between requests
   - Serialize requests instead of parallel

4. **Monitor system resources:**
   - CPU/Memory usage
   - Disk I/O
   - Network bandwidth

## Deployment Checklist

Before deploying scraper updates:

- [ ] All DOM selectors tested with 3+ accounts
- [ ] Error handling verified
- [ ] Rate limits tested
- [ ] Login wall recovery tested
- [ ] Memory leaks checked
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] Backward compatibility verified
- [ ] No breaking changes to API

## Reporting Issues

When reporting maintenance issues:

**Include:**
1. Error message (full text)
2. Account that triggered error
3. Timestamp of occurrence
4. Environment (OS, Node version, Puppeteer version)
5. Recent DOM/configuration changes
6. Network conditions at time

**Example report:**
```
Twitter Scraper Issue:
- Account: @username
- Error: "Browser disconnected"
- Time: 2026-01-25 07:30:00 UTC
- Environment: MSYS, Node 22, Puppeteer 23.11
- Pattern: Happens after 20+ consecutive scrapes
- Last update: Check Puppeteer changelog for crash fixes
```

## Resources

- Twitter/X: https://twitter.com/
- Puppeteer docs: https://pptr.dev/
- DOM selector guide: https://developer.mozilla.org/en-US/docs/Web/CSS/Selectors
- Chrome DevTools: https://developer.chrome.com/docs/devtools/
