---
name: social-content
description: "Create social media content for LinkedIn, Twitter/X, Instagram, TikTok, Facebook. Use for posts, threads, carousels, reels, content calendars, engagement strategies, and viral content analysis."
hooks:
  Stop:
    - hooks:
        - type: command
          command: node "scripts/content-analysis-detector.cjs"
      once: true
---

# Social Content

Expert social media strategist for creating engaging content that builds audience and drives engagement.

## When to Use

- Creating posts, threads, carousels, reels for any platform
- Building content calendars and scheduling strategies
- Repurposing content across platforms
- Analyzing viral content patterns
- Optimizing engagement and reach

## Workflow

1. Gather context (goals, audience, brand voice, resources)
2. Select platform strategy from refs
3. **Check knowledge base for platform-specific lessons**
4. Choose appropriate templates
5. Apply hook formulas
6. Schedule using content calendar

## Platforms

| Platform | Best For | Frequency | Ref |
|----------|----------|-----------|-----|
| LinkedIn | B2B, thought leadership | 3-5x/week | `refs/platform-linkedin.md` |
| Twitter/X | Tech, real-time, community | 3-10x/day | `refs/platform-twitter.md` |
| Instagram | Visual, lifestyle, e-commerce | 1-2 feed + stories | `refs/platform-instagram.md` |
| TikTok | Brand awareness, viral | 1-4x/day | `refs/platform-tiktok.md` |
| Facebook | Communities, local, groups | 1-2x/day | `refs/platform-facebook.md` |

## Templates

| Type | Platform | Ref |
|------|----------|-----|
| Story, Contrarian, List, How-To | LinkedIn | `refs/templates-linkedin.md` |
| Tutorial, Story, Breakdown threads | Twitter/X | `refs/templates-twitter.md` |
| Carousel, Reel scripts | Instagram | `refs/templates-instagram.md` |

## Strategy Modules

| Topic | Ref |
|-------|-----|
| Hook formulas (curiosity, story, value, contrarian) | `refs/hook-formulas.md` |
| Content pillars framework | `refs/content-pillars.md` |
| Repurposing blog/podcast → social | `refs/content-repurposing.md` |
| Weekly/monthly calendar structure | `refs/content-calendar.md` |
| Daily engagement routine | `refs/engagement-strategy.md` |
| Metrics and optimization | `refs/analytics-optimization.md` |
| Reverse engineering viral content | `refs/reverse-engineering.md` |

## Knowledge Base

Lessons from real content analysis. Check before creating/reviewing content.

| Platform | Ref |
|----------|-----|
| Facebook | `knowledge/facebook-lessons.md` |
| LinkedIn | `knowledge/linkedin-lessons.md` |
| Twitter/X | `knowledge/twitter-lessons.md` |
| Instagram | `knowledge/instagram-lessons.md` |
| General | `knowledge/general-patterns.md` |

## References

| File | Purpose |
|------|---------|
| `refs/platform-*.md` | Platform-specific strategies and algorithm tips |
| `refs/templates-*.md` | Post templates by platform |
| `refs/hook-formulas.md` | First-line hook patterns |
| `refs/content-pillars.md` | Content strategy framework |
| `refs/content-repurposing.md` | Multi-platform content system |
| `refs/content-calendar.md` | Scheduling and batching |
| `refs/engagement-strategy.md` | Daily engagement routine |
| `refs/analytics-optimization.md` | Metrics tracking and optimization |
| `refs/reverse-engineering.md` | Viral content analysis framework |

## Best Practices

1. First line is everything—hook before "see more"
2. No external links in post body (kills reach)
3. Comments > likes for algorithm
4. Platform-native content > cross-posting
5. Consistency > perfection
6. Engage with others' content daily

## Post-Analysis Workflow

When analyzing draft vs production or content performance:

1. Identify changes and rationale
2. Extract patterns (✅) and anti-patterns (❌)
3. Append to `knowledge/{platform}-lessons.md`
4. Use format from `knowledge/README.md`
