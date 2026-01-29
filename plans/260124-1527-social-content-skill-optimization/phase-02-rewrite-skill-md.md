# Phase 02: Rewrite SKILL.md

## Overview

- **Priority:** High
- **Status:** pending
- **Depends on:** Phase 01
- **Description:** Rewrite SKILL.md to < 100 lines with references to new files

## Key Insights

- Follow copywriting skill pattern (94 lines)
- Use tables for compact reference listings
- Keep workflow instructions brief

## Requirements

### Functional
- YAML frontmatter with name, description (< 200 chars)
- "When to Use" section
- Platform quick reference table
- References table with all 15 files
- Best practices (condensed)

### Non-functional
- < 100 lines total
- Clear, scannable format
- Progressive disclosure via refs

## Architecture

**New SKILL.md structure:**
```
---
YAML frontmatter (name, description)
---
# Social Content

[1-2 sentence purpose]

## When to Use
[Bullet list of triggers]

## Workflow
[Context gathering checklist - condensed]

## Platforms Quick Reference
[Table: Platform | Best For | Frequency | Ref File]

## Templates
[Table: Type | Platform | Ref File]

## Strategy Modules
[Table: Topic | Ref File]

## References
[Full table of all ref files]

## Best Practices
[6 condensed best practices]
```

## Related Code Files

**Modify:**
- `.claude/skills/social-content/SKILL.md`

## Implementation Steps

1. Backup current SKILL.md
2. Write new YAML frontmatter (description < 200 chars)
3. Write condensed "When to Use" section
4. Write condensed "Workflow" section
5. Create platform quick reference table
6. Create templates reference table
7. Create strategy modules table
8. Create full references table
9. Write condensed best practices
10. Verify line count < 100

## Todo List

- [ ] Backup current SKILL.md
- [ ] Write new SKILL.md
- [ ] Verify < 100 lines

## Success Criteria

- SKILL.md < 100 lines
- Description < 200 characters
- All 15 ref files properly linked
- Core workflow preserved

## Risk Assessment

- **Medium:** May need to iterate on condensing
- **Mitigation:** Use tables aggressively, remove redundancy

## Next Steps

Proceed to Phase 03 for validation and testing
