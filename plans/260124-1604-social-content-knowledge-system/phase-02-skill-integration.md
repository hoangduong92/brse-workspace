# Phase 2: SKILL.md Integration

## Overview
- **Priority**: High
- **Status**: Pending
- **Depends on**: Phase 1

## Requirements

Update SKILL.md to:
1. Reference knowledge directory in workflow
2. Add section for knowledge-based recommendations
3. Keep token-efficient (progressive disclosure)

## Related Code Files

- `.claude/skills/social-content/SKILL.md`

## Implementation Steps

### Step 1: Add Knowledge Section to SKILL.md

Add after "Strategy Modules" section:

```markdown
## Knowledge Base

Lessons learned from real content analysis. Reference when creating or reviewing content.

| Platform | Lessons | Ref |
|----------|---------|-----|
| Facebook | Draft vs Production patterns | `knowledge/facebook-lessons.md` |
| LinkedIn | B2B content optimization | `knowledge/linkedin-lessons.md` |
| Twitter/X | Thread performance | `knowledge/twitter-lessons.md` |
| Instagram | Visual content patterns | `knowledge/instagram-lessons.md` |
| General | Cross-platform patterns | `knowledge/general-patterns.md` |
```

### Step 2: Update Workflow Section

Add step 6 to existing workflow:

```markdown
## Workflow

1. Gather context (goals, audience, brand voice, resources)
2. Select platform strategy from refs
3. Choose appropriate templates
4. Apply hook formulas
5. Schedule using content calendar
6. **Check knowledge base for platform-specific lessons**
```

### Step 3: Add Post-Analysis Workflow

Add new section:

```markdown
## Post-Analysis Workflow

When analyzing content performance or comparing draft vs production:

1. Identify what changed and why
2. Extract patterns (what worked) and anti-patterns (what didn't)
3. Append to relevant `knowledge/*.md` file
4. Use standard lesson format from `knowledge/README.md`
```

## Todo List

- [ ] Add Knowledge Base section to SKILL.md
- [ ] Update Workflow with step 6
- [ ] Add Post-Analysis Workflow section
- [ ] Verify progressive disclosure maintained

## Success Criteria

- SKILL.md references knowledge directory
- Workflow includes knowledge check step
- Post-analysis workflow documented
- Token count increase minimal (<20 lines)

## Next Steps

→ Phase 3: Seed initial lessons from today's analysis
