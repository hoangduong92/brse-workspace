# Phase 3: Seed Initial Lessons

## Overview
- **Priority**: High
- **Status**: Pending
- **Depends on**: Phase 1, Phase 2

## Requirements

Populate knowledge files with lessons from today's Facebook content analysis:
- Hooks in Skills post (draft vs production comparison)

## Source Analysis Summary

| Metric | Draft | Production | Lesson |
|--------|-------|------------|--------|
| Lines | 288 | 90 | -69% is good |
| Code blocks | 6+ | 1 | Concept > implementation |
| Images | 0 | 2 | Visual content essential |
| Discussion CTA | No | No | Missing opportunity |

## Implementation Steps

### Step 1: Add Facebook Lessons

Add to `knowledge/facebook-lessons.md`:

**Pattern 1**: Concise Over Complete
**Pattern 2**: Visual Content Essential
**Anti-Pattern 1**: Missing Discussion CTA
**Anti-Pattern 2**: Technical Hook Length

### Step 2: Add General Patterns

Add to `knowledge/general-patterns.md`:

**Pattern**: Draft-to-Production Reduction
- Technical content → social format = 60-70% reduction expected

## Lessons to Add

### Facebook Lessons

```markdown
## ✅ Pattern: Concise Over Complete
- **Source**: 2026-01-24 | Technical tutorial (Hooks in Skills)
- **Context**: Draft had 288 lines, 6+ code blocks
- **Lesson**: Reduce to <100 lines. Keep concept diagrams, remove code implementation.
- **Apply when**: Converting technical content to Facebook

## ✅ Pattern: Visual Content Essential
- **Source**: 2026-01-24 | Technical tutorial
- **Context**: Production added 2 images, draft had none
- **Lesson**: Always include relevant images/diagrams for Facebook posts
- **Apply when**: Any Facebook post with technical content

## ❌ Anti-Pattern: Missing Discussion CTA
- **Source**: 2026-01-24 | Technical tutorial
- **Issue**: No question prompting comments at end
- **Fix**: Add "Bạn có [relevant question]? Comment bên dưới!"
- **Why matters**: Facebook algorithm heavily favors comments over likes

## ❌ Anti-Pattern: Long Technical Hook
- **Source**: 2026-01-24 | Technical tutorial
- **Issue**: Title "Hooks Trong Skills: Cách Tạo..." gets truncated
- **Fix**: Keep hook under 125 chars, use story/curiosity format
- **Why matters**: Facebook truncates after ~125 chars in preview
```

## Todo List

- [ ] Add 4 lessons to facebook-lessons.md
- [ ] Add 1 pattern to general-patterns.md
- [ ] Verify format consistency

## Success Criteria

- Facebook lessons file has 4 entries from today's analysis
- General patterns file has 1 cross-platform insight
- All entries follow standard format

## Next Steps

→ Phase 4 (Optional): Hook auto-append for future automation
