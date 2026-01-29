# ListFeeds Workflow

Display all followed URLs.

## Trigger

- "list feeds"
- "show feeds"
- "my feeds"
- "show my subscriptions"

## Workflow Steps

### Step 1: Load Feeds

```bash
bun run ~/.claude/skills/FeedReader/Tools/FeedManager.ts list --format table
```

### Step 2: Load Cache Stats

```bash
bun run ~/.claude/skills/FeedReader/Tools/ContentCache.ts stats
```

Get last check time and update status for each feed.

### Step 3: Display

Format output as organized table:

```
# Your Feeds (15 total)

## By Category

### Blogs (8)
| Name | URL | Priority | Last Checked |
|------|-----|----------|--------------|
| Simon Willison | simonwillison.net | high | 2 hours ago |
| Paul Graham | paulgraham.com | high | 2 hours ago |
| ... | ... | ... | ... |

### Twitter/X (4)
| Name | URL | Priority | Last Checked |
|------|-----|----------|--------------|
| @karpathy | twitter.com/karpathy | high | 2 hours ago |
| ... | ... | ... | ... |

### Newsletters (2)
| Name | URL | Priority | Last Checked |
|------|-----|----------|--------------|
| Pragmatic Engineer | newsletter.pragmaticengineer.com | medium | 2 hours ago |
| ... | ... | ... | ... |

### YouTube (1)
| Name | URL | Priority | Last Checked |
|------|-----|----------|--------------|
| Lex Fridman | youtube.com/@lexfridman | low | 2 hours ago |

---

## Summary

- Total feeds: 15
- High priority: 6
- Medium priority: 7
- Low priority: 2
- Last digest: 2026-01-25 08:30
- Next suggested: Run "daily digest" now

## Quick Actions

- Add new: "add feed [URL]"
- Remove: "remove feed [URL or name]"
- Run digest: "daily digest"
```

## Output Variations

### Compact mode

If user asks for "list feeds briefly" or "quick feed list":

```
Your 15 feeds:
1. simonwillison.net (blog, high)
2. paulgraham.com (blog, high)
3. @karpathy (twitter, high)
...
```

### By priority

If user asks for "list high priority feeds":

```
High Priority Feeds (6):
1. Simon Willison - simonwillison.net
2. Paul Graham - paulgraham.com
3. @karpathy - twitter.com/karpathy
...
```

### With stats

If user asks for "list feeds with stats":

```
| Name | Category | Checked | New Content | Avg Updates |
|------|----------|---------|-------------|-------------|
| Simon Willison | blog | 2h ago | Yes | 3/week |
| Paul Graham | blog | 2h ago | No | 1/month |
...
```

## Error Handling

### No feeds configured

```
No feeds configured yet.

Get started:
1. "add feed https://example.com/blog"
2. "add feed https://twitter.com/username"
3. "daily digest"
```

### feeds.yaml corrupted

```
Error reading feeds file. The file may be corrupted.

Would you like to:
1. View raw file content
2. Reset to template
3. Try to repair
```
