# AddFeed Workflow

Add a new URL to the feeds list.

## Trigger

- "add feed [URL]"
- "follow [URL]"
- "subscribe to [URL]"

## Input

- **URL** (required): The URL to add
- **name** (optional): Display name for the feed
- **category** (optional): blog, twitter, newsletter, youtube
- **priority** (optional): high, medium, low

## Workflow Steps

### Step 1: Parse Input

Extract URL from user input. If URL not provided, ask:
```
Please provide the URL you want to add:
```

### Step 2: Validate URL

Check URL format:
```bash
# Basic URL validation
curl -s -o /dev/null -w "%{http_code}" -L "[URL]"
```

If returns 000 (unreachable) or 404:
```
Cannot reach [URL]. Please check:
1. URL is correct
2. Site is accessible
Continue anyway? (The URL may work with browser automation)
```

### Step 3: Detect Category

Auto-detect category from URL:

| URL Pattern | Category |
|-------------|----------|
| `twitter.com`, `x.com` | twitter |
| `youtube.com`, `youtu.be` | youtube |
| `substack.com`, `newsletter` | newsletter |
| Default | blog |

### Step 4: Get Feed Details

If name not provided, try to extract from page title using WebFetch:
```
Use WebFetch to get the page title from [URL]
```

If extraction fails, ask user:
```
What name should I use for this feed?
```

### Step 5: Add to feeds.yaml

```bash
bun run ~/.claude/skills/FeedReader/Tools/FeedManager.ts add \
  --url "[URL]" \
  --name "[NAME]" \
  --category "[CATEGORY]" \
  --priority "medium"
```

### Step 6: Confirm

```
Added feed:
  URL: [URL]
  Name: [NAME]
  Category: [CATEGORY]
  Priority: medium

You now have X feeds total.
Run "daily digest" to check for new content.
```

## Examples

### Simple add
```
User: add feed https://simonwillison.net/
Assistant: Added feed:
  URL: https://simonwillison.net/
  Name: Simon Willison
  Category: blog
  Priority: medium
```

### With details
```
User: add feed https://twitter.com/karpathy as "Andrej Karpathy" with high priority
Assistant: Added feed:
  URL: https://twitter.com/karpathy
  Name: Andrej Karpathy
  Category: twitter
  Priority: high
```

## Error Handling

### Duplicate URL
```
This URL is already in your feeds list as "[NAME]".
```

### Invalid URL format
```
"[INPUT]" doesn't look like a valid URL.
Please provide a full URL starting with http:// or https://
```

### feeds.yaml not found
```
Creating new feeds file at ~/.claude/skills/FeedReader/feeds.yaml
```
