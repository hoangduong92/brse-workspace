# Phase 4: Hook Auto-Append (Optional Enhancement)

## Overview
- **Priority**: Low (Future enhancement)
- **Status**: Future
- **Depends on**: Phase 1-3 complete and proven

## Requirements

Create a Stop hook that:
1. Detects when skill is used for content analysis
2. Prompts Claude to save lessons
3. Auto-appends to appropriate knowledge file

## Architecture

```
SKILL.md frontmatter:
---
hooks:
  Stop:
    - hooks:
        - type: command
          command: node ".claude/skills/social-content/scripts/save-lesson.cjs"
      once: true
---
```

## Implementation Approach

### Detection Logic
```javascript
// Detect content analysis activity
const analysisPatterns = [
  'draft vs production',
  'phân tích',
  'compare',
  'rút kinh nghiệm',
  'lessons learned'
];
```

### Output Format
Hook outputs JSON for Claude to process:
```json
{
  "detected": true,
  "platform": "facebook",
  "suggestedLessons": [...]
}
```

## Why Future/Optional

1. **Manual first**: Validate format and usefulness before automating
2. **Low frequency**: Content analysis happens occasionally, not every session
3. **Quality control**: Manual review ensures high-quality lessons
4. **Complexity**: Hook development adds maintenance overhead

## Implementation Steps (When Ready)

1. Create `scripts/` directory in skill
2. Implement `save-lesson.cjs` script
3. Add hook to SKILL.md frontmatter
4. Test with sample content analysis sessions
5. Refine detection logic based on false positives/negatives

## Prerequisites Before Starting

- [ ] Phase 1-3 complete
- [ ] 10+ manual lessons added successfully
- [ ] Format proven useful in practice
- [ ] User confirms automation value

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| False positive detection | Conservative pattern matching |
| Low quality auto-lessons | Always prompt user confirmation |
| Hook performance impact | once: true limits to 1x per session |

## Success Criteria

- Hook correctly detects content analysis sessions
- Lessons auto-appended maintain quality
- No false positives disrupting normal skill usage
