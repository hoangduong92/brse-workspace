# Phase 01: Create Reference Files

## Overview

- **Priority:** High
- **Status:** pending
- **Description:** Extract content from SKILL.md into modular reference files

## Key Insights

- Current SKILL.md: 868 lines, needs splitting into 15 files
- Each ref file should be < 100 lines
- Follow copywriting skill pattern for structure

## Requirements

### Functional
- Extract all platform-specific content into separate files
- Create template files grouped by platform
- Split strategy content into logical modules

### Non-functional
- Each file < 100 lines
- Clear, actionable instructions (not documentation)
- Sacrifice grammar for concision

## Related Code Files

**Create:**
- `.claude/skills/social-content/refs/platform-linkedin.md`
- `.claude/skills/social-content/refs/platform-twitter.md`
- `.claude/skills/social-content/refs/platform-instagram.md`
- `.claude/skills/social-content/refs/platform-tiktok.md`
- `.claude/skills/social-content/refs/platform-facebook.md`
- `.claude/skills/social-content/refs/templates-linkedin.md`
- `.claude/skills/social-content/refs/templates-twitter.md`
- `.claude/skills/social-content/refs/templates-instagram.md`
- `.claude/skills/social-content/refs/hook-formulas.md`
- `.claude/skills/social-content/refs/content-pillars.md`
- `.claude/skills/social-content/refs/content-repurposing.md`
- `.claude/skills/social-content/refs/content-calendar.md`
- `.claude/skills/social-content/refs/engagement-strategy.md`
- `.claude/skills/social-content/refs/analytics-optimization.md`
- `.claude/skills/social-content/refs/reverse-engineering.md`

## Implementation Steps

1. Create `refs/` directory
2. Extract LinkedIn content (lines 44-74) → `refs/platform-linkedin.md`
3. Extract Twitter content (lines 75-103) → `refs/platform-twitter.md`
4. Extract Instagram content (lines 105-133) → `refs/platform-instagram.md`
5. Extract TikTok content (lines 135-165) → `refs/platform-tiktok.md`
6. Extract Facebook content (lines 166-187) → `refs/platform-facebook.md`
7. Extract LinkedIn templates (lines 219-289) → `refs/templates-linkedin.md`
8. Extract Twitter templates (lines 291-333) → `refs/templates-twitter.md`
9. Extract Instagram templates (lines 335-354) → `refs/templates-instagram.md`
10. Extract hook formulas (lines 358-395) → `refs/hook-formulas.md`
11. Extract content pillars (lines 190-214) → `refs/content-pillars.md`
12. Extract repurposing system (lines 398-430) → `refs/content-repurposing.md`
13. Extract calendar structure (lines 433-464) → `refs/content-calendar.md`
14. Extract engagement strategy (lines 467-501) → `refs/engagement-strategy.md`
15. Extract analytics (lines 504-554) → `refs/analytics-optimization.md`
16. Extract reverse engineering (lines 641-848) → `refs/reverse-engineering.md`

## Todo List

- [ ] Create refs/ directory
- [ ] Create platform-linkedin.md
- [ ] Create platform-twitter.md
- [ ] Create platform-instagram.md
- [ ] Create platform-tiktok.md
- [ ] Create platform-facebook.md
- [ ] Create templates-linkedin.md
- [ ] Create templates-twitter.md
- [ ] Create templates-instagram.md
- [ ] Create hook-formulas.md
- [ ] Create content-pillars.md
- [ ] Create content-repurposing.md
- [ ] Create content-calendar.md
- [ ] Create engagement-strategy.md
- [ ] Create analytics-optimization.md
- [ ] Create reverse-engineering.md

## Success Criteria

- All 15 reference files created
- Each file < 100 lines
- Content preserved from original SKILL.md

## Risk Assessment

- **Low:** Content extraction is straightforward
- **Mitigation:** Verify line counts after each file

## Next Steps

Proceed to Phase 02 to rewrite SKILL.md with references to new files
