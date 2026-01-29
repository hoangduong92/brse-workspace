# X Profile Scraping Report: Andrej Karpathy (@karpathy)
**Date:** January 25, 2026
**Target:** https://x.com/karpathy
**Objective:** Extract recent tweets from January 24-25, 2026

---

## Execution Summary

Attempted progressive four-tier scraping strategy per bright-data skill workflow:

| Tier | Method | Status | Reason |
|------|--------|--------|--------|
| **1** | WebFetch (built-in) | ❌ Failed | X requires JavaScript rendering; returned shell HTML |
| **2** | Curl + Chrome Headers | ❌ Failed | Static shell HTML without actual tweet content |
| **3** | Browser Automation (chrome-devtools) | ❌ Failed | Page requires user authentication to display tweets |
| **4** | Bright Data MCP | ⏸️ Unavailable | Not configured in current environment |

---

## Detailed Findings

### Tier 1: WebFetch
**Result:** Error page - "JavaScript is not available"
- WebFetch receives empty DOM shell
- X returns generic error message when JavaScript disabled
- No tweet data accessible

### Tier 2: Curl with Browser Headers
**Result:** Static HTML shell without content
- Successfully fetches page structure
- Contains CSS framework classes and meta tags
- Missing dynamic JavaScript-rendered tweet content
- No actual tweets, engagement metrics, or user info

### Tier 3: Chrome DevTools (Puppeteer)
**Result:** Authentication wall
- Browser successfully loads X.com domain
- Page title: "Andrej Karpathy (@karpathy) / X" ✓
- 190 DOM elements detected
- **Critical finding:** Only login/signup buttons visible
- Requires X account login to access profile tweets
- Personal tweets not publicly accessible without authentication

### Tier 4: Bright Data MCP
**Status:** Not configured

**Current MCP Configuration:**
```json
{
  "mcpServers": {
    "context7": "Upstash Context7 MCP",
    "human-mcp": "Human interaction MCP",
    "chrome-devtools": "Browser automation (already in use)",
    "sequential-thinking": "Reasoning MCP"
  }
}
```

**Missing:** Bright Data MCP server not in `.claude/.mcp.json`

---

## Access Requirements

X.com enforces **authentication-required profile viewing**:
- All public profiles require login on X.com (as of 2026)
- Bot detection prevents scrapers
- Residential IP needed for reliable access
- CAPTCHA/challenge possible on scrapers

---

## Recommendations

### Option 1: Configure Bright Data MCP (Recommended)
**Cost:** Bright Data credits (~$1-5 per scrape)
**Setup Time:** 10-15 minutes

1. Create Bright Data account & get API key
2. Update `.claude/.mcp.json`:
```json
{
  "mcpServers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@bright-data/mcp-server"],
      "env": {
        "BRIGHT_DATA_API_KEY": "your_api_key_here"
      }
    }
  }
}
```
3. Call `mcp__Brightdata__scrape_as_markdown` tool with URL
4. Returns markdown-formatted tweets with metadata

**Success Rate:** ~99% (handles CAPTCHA, bot detection, residential IPs)

### Option 2: Use X API (Official)
**Cost:** Free (with rate limits) to paid tiers
**Complexity:** Medium

Use official X API endpoints:
```
GET /2/users/by/username/{username}
GET /2/users/{id}/tweets
```

Requires:
- X Developer Account
- API key & bearer token
- Elevated access (might need approval for free tier)

**Success Rate:** 100% for public tweets (if user allows)

### Option 3: Browser Extension / Manual Access
**Cost:** Free (time investment)
**Reliability:** 100%

Access directly via web browser at https://x.com/karpathy while logged in, then manually extract or screenshot relevant tweets from January 24-25, 2026.

### Option 4: Web Archive / Alternative Sources
**Cost:** Free
**Limitation:** May have delayed indexing

Check:
- archive.org/web/ (Wayback Machine)
- Alternative Twitter archives
- News aggregators covering Andrej Karpathy's recent statements

---

## Technical Blockers

**Why standard scraping fails on X:**

1. **JavaScript-Rendered Content:** X uses React SPAs; static scrapers get empty shells
2. **Authentication Gate:** Most profiles need login
3. **Bot Detection:** IP reputation, header analysis, fingerprinting
4. **Rate Limiting:** Datacenter IPs blocked; need residential proxies
5. **Terms of Service:** Scraping X violates ToS without permission

**Why Bright Data succeeds:**
- Residential proxy network (real user IPs)
- Automatic CAPTCHA solving
- JavaScript rendering + DOM extraction
- Anti-detection bypass
- Automatic retries

---

## Files & Configuration

**Work Context:** c:\Users\duongbibo\brse-workspace
**Bright-data Skill:** `.claude/skills/bright-data/`
**Chrome-devtools:** `.claude/skills/chrome-devtools/` (verified working)
**MCP Config:** `.claude/.mcp.json` (missing Bright Data)
**MCP Config Example:** `.claude/.mcp.json.example`

---

## Unresolved Questions

1. Do you have Bright Data API credentials?
2. Should I configure Bright Data MCP with your API key?
3. Do you prefer X API approach instead?
4. Is authentication available (can you log in manually)?
5. Can this data be sourced from public archives instead?

---

**Report Generated:** 2026-01-25 12:13 UTC
**Subagent:** mcp-manager
