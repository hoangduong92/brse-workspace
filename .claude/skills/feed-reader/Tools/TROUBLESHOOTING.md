# FeedReader Troubleshooting Guide

Common issues and solutions for feed-reader skill.

## YouTube Handler Issues

### "Could not extract channel ID"

**Symptoms:**
- Error when adding YouTube URL
- Message: "Failed to extract channel ID"

**Causes:**
- Invalid URL format
- YouTube blocking the request (rate limit)
- Network connectivity issue
- Invalid handle/custom name (doesn't exist)

**Solutions:**

1. **Verify URL format:**
   ```
   Valid:   https://youtube.com/@channelname
   Valid:   https://youtube.com/channel/UC...
   Valid:   https://youtube.com/c/customname
   Invalid: https://youtu.be/... (video link, not channel)
   Invalid: /channel/UC... (missing domain)
   ```

2. **Check if channel is public:**
   - Visit the URL in browser first
   - Ensure channel exists and is not private

3. **Try alternative format:**
   - @handle not working? Try /channel/ format
   - /c/customname not working? Look up the channel ID and use /channel/ format

4. **Check network connectivity:**
   - Test: `ping youtube.com`
   - Ensure no firewall blocking YouTube

### "No transcript available for this video"

**Symptoms:**
- YouTube video fetched but transcript extraction fails
- Message: "Could not retrieve a transcript"

**Causes:**
- Video has no captions/transcripts enabled
- Language requested is not available
- Video is restricted or age-gated
- Channel disabled transcripts

**Solutions:**

1. **Check if video has transcripts:**
   - Open video on YouTube.com
   - Check for "More" → "Show transcript" option
   - If not available, video has no transcripts

2. **Request different language:**
   - Script tries: en, ja, vi (in order)
   - Some videos only have auto-generated captions
   - Auto-generated captions have lower quality

3. **For restricted videos:**
   - Age-gated videos may not have extractable transcripts
   - No technical workaround available

### "Channel fetch returned 404"

**Symptoms:**
- RSS feed fetch fails with 404
- Channel ID is correct but feed won't load

**Causes:**
- Channel has no public videos
- YouTube changed feed format
- Feed was temporarily unavailable

**Solutions:**

1. **Check channel has public videos:**
   - Visit channel URL
   - Ensure videos are not all private

2. **Verify channel ID format:**
   - Channel IDs start with "UC" followed by 22 alphanumeric characters
   - Example: `UCSHZKyawb77ixDdsGog4iWA`

3. **Wait and retry:**
   - YouTube feeds sometimes cache
   - Try again in 5-10 minutes

## Twitter/X Scraper Issues

### "Puppeteer installation failed"

**Symptoms:**
- Error when trying to scrape Twitter
- Message: "Cannot find module 'puppeteer'"

**Causes:**
- Node dependencies not installed
- MSYS environment (Chromium download fails)
- Disk space issues
- Network timeout during install

**Solutions:**

1. **Install dependencies:**
   ```bash
   cd .claude/skills/feed-reader/Tools
   npm install
   ```

2. **For MSYS environment:**
   - Puppeteer requires Chromium binary
   - MSYS doesn't support Chromium easily
   - Workaround: Use Windows native terminal or WSL2

3. **Check disk space:**
   - Chromium binary is ~200MB
   - Ensure 500MB+ free space

4. **Disable Chromium download:**
   - Set: `PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true`
   - Use system Chromium/Chrome instead
   - `npm install PUPPETEER_PRODUCT=chrome`

### "Login wall detected / Rate limit"

**Symptoms:**
- Twitter profile exists but scraper gets login wall
- Message: "Rate limit detected"

**Causes:**
- Twitter blocking automated access
- Request rate too high
- IP address flagged as bot
- Account temporarily suspended

**Solutions:**

1. **Add more delay between requests:**
   - Increase `MIN_REQUEST_INTERVAL` in code
   - Default: 10 seconds between profiles
   - Try: 30-60 seconds for rate-limited scenarios

2. **Use VPN/proxy:**
   - IP may be flagged by Twitter
   - Try from different IP address

3. **Remove and re-add feed:**
   - Delete feed from feeds.yaml
   - Wait 24 hours
   - Add again

4. **Check if account is public:**
   - Private accounts can't be scraped
   - Verify account is public and has tweets

### "No tweets extracted"

**Symptoms:**
- Scraper runs but returns empty tweet list
- No error message

**Causes:**
- Profile is private
- Profile has no tweets
- DOM selectors changed (Twitter/X redesign)
- Login wall shown

**Solutions:**

1. **Verify profile is public:**
   - Visit profile on Twitter/X in browser
   - Check if tweets are visible

2. **Check DOM selectors:**
   - Twitter/X updates DOM structure frequently
   - Selectors may need updating:
     - `[data-testid="tweet"]` - main tweet container
     - `[data-testid="tweetText"]` - tweet content
     - `[data-testid="User-Name"]` - author name
   - Report issue if selectors need updates

3. **Try again later:**
   - Sometimes temporary loading issues
   - Wait 5 minutes and retry

### "Timeout or browser crash"

**Symptoms:**
- "Navigation timeout" error
- "Browser disconnected" error
- Scraper hangs indefinitely

**Causes:**
- Slow network connection
- Twitter slow to load
- Browser resource exhaustion
- Port conflicts with other processes

**Solutions:**

1. **Increase timeout:**
   - Default: 30 seconds
   - For slow connections: try 60 seconds
   - Edit `YouTubeHandler.ts` REQUEST_TIMEOUT value

2. **Check browser process:**
   - Background Chrome/Chromium instances running
   - Kill unused browser processes
   - Restart computer if many processes

3. **Reduce batch size:**
   - Don't scrape too many profiles at once
   - Limit to 5-10 per batch
   - Add delays between batches

## General Issues

### "Cache file corrupted"

**Symptoms:**
- Error loading cache
- Message: "Invalid JSON in cache.json"

**Causes:**
- File truncated during save
- File locked by another process
- Disk write error

**Solutions:**

1. **Clear cache:**
   ```bash
   bun run ContentCache.ts clear
   ```

2. **Reset cache file:**
   ```bash
   rm ~/.claude/skills/feed-reader/cache.json
   ```

3. **Run digest to regenerate:**
   - Next "daily digest" will recreate cache

### "Feeds.yaml not found"

**Symptoms:**
- Error: "No feeds configured"
- Message: "Missing feeds.yaml"

**Causes:**
- Feeds file deleted
- Path misconfiguration
- First time setup

**Solutions:**

1. **Initialize feeds:**
   - Run: `bun run FeedManager.ts list`
   - Will create template if missing

2. **Add first feed:**
   ```
   User: "add feed https://example.com/blog"
   ```

3. **Check file location:**
   - Expected: `~/.claude/skills/feed-reader/feeds.yaml`
   - `~` = user home directory
   - On Windows: `C:\Users\[YourName]\.claude\skills\feed-reader\feeds.yaml`

### "Digest not saving"

**Symptoms:**
- Digest generated but not found in output directory
- Message: "Could not save digest"

**Causes:**
- Directory doesn't exist
- Permission denied on directory
- Disk full

**Solutions:**

1. **Create output directory:**
   ```bash
   mkdir -p ~/.claude/History/digests
   ```

2. **Check permissions:**
   ```bash
   ls -ld ~/.claude/History
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```
   - Ensure at least 100MB free

## Performance Issues

### "Digest takes too long"

**Symptoms:**
- Daily digest takes 30+ minutes
- System slow during digest

**Causes:**
- Too many feeds (100+)
- Network latency
- Large content downloads
- Low system resources

**Solutions:**

1. **Reduce feed count:**
   - Keep high-priority feeds only
   - Remove inactive feeds
   - Use: `"remove feed [url]"`

2. **Set feed priorities:**
   ```yaml
   - url: https://fast-blog.com
     priority: high

   - url: https://slow-blog.com
     priority: low
   ```

3. **Run during off-peak:**
   - Schedule digest for low-traffic hours
   - Improves network response times

4. **Monitor system resources:**
   - CPU/RAM usage
   - Disk I/O
   - Network bandwidth

## Getting Help

If issue persists:

1. **Check logs:**
   - Look for error messages during digest run
   - Note exact error text

2. **Test individual components:**
   - Test YouTube fetch separately
   - Test single feed scraping
   - Isolate which part is failing

3. **Report issue:**
   - Include full error message
   - Note OS/environment
   - List affected feeds
   - Provide reproduction steps
