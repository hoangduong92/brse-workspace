# RemoveFeed Workflow

Remove a URL from the feeds list.

## Trigger

- "remove feed [URL]"
- "unfollow [URL]"
- "unsubscribe from [URL]"
- "delete feed [NAME]"

## Input

- **URL or Name** (required): The URL or name to remove

## Workflow Steps

### Step 1: Parse Input

Extract URL or name from user input.

### Step 2: Find Feed

```bash
bun run ~/.claude/skills/FeedReader/Tools/FeedManager.ts find "[INPUT]"
```

Search by:
1. Exact URL match
2. Partial URL match
3. Name match (case-insensitive)

### Step 3: Confirm Match

If single match found:
```
Found feed:
  Name: [NAME]
  URL: [URL]
  Category: [CATEGORY]

Remove this feed? (yes/no)
```

If multiple matches:
```
Found multiple feeds matching "[INPUT]":
1. [NAME] - [URL]
2. [NAME] - [URL]

Which one should I remove? (Enter number or "all")
```

If no match:
```
No feed found matching "[INPUT]".
Use "list feeds" to see all your feeds.
```

### Step 4: Remove from feeds.yaml

```bash
bun run ~/.claude/skills/FeedReader/Tools/FeedManager.ts remove --url "[URL]"
```

### Step 5: Clear Cache Entry

```bash
bun run ~/.claude/skills/FeedReader/Tools/ContentCache.ts remove "[URL]"
```

### Step 6: Confirm

```
Removed feed:
  Name: [NAME]
  URL: [URL]

You now have X feeds remaining.
```

## Examples

### Remove by URL
```
User: remove feed https://old-blog.com
Assistant: Removed feed:
  Name: Old Blog
  URL: https://old-blog.com

You now have 12 feeds remaining.
```

### Remove by name
```
User: unfollow Paul Graham
Assistant: Found feed:
  Name: Paul Graham Essays
  URL: https://www.paulgraham.com/articles.html

Remove this feed? (yes/no)

User: yes
Assistant: Removed feed:
  Name: Paul Graham Essays
  URL: https://www.paulgraham.com/articles.html

You now have 11 feeds remaining.
```

## Error Handling

### Feed not found
```
No feed found matching "[INPUT]".

Your current feeds:
1. [Name] - [URL]
2. [Name] - [URL]
...
```

### Last feed
```
This is your only remaining feed. Remove it anyway?
Note: You'll have no feeds left for daily digest.
```
