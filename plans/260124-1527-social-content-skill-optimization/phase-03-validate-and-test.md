# Phase 03: Validate & Test

## Overview

- **Priority:** High
- **Status:** pending
- **Depends on:** Phase 02
- **Description:** Validate skill structure and test functionality

## Key Insights

- Must verify all line counts
- Test skill activation with sample prompts
- Ensure progressive disclosure works

## Requirements

### Functional
- SKILL.md < 100 lines
- All ref files < 100 lines
- Description < 200 characters
- All file references valid

### Non-functional
- Skill activates on relevant prompts
- Correct ref files load when needed

## Implementation Steps

1. Count lines in SKILL.md
2. Count lines in each ref file
3. Verify description length
4. Test skill with sample prompts:
   - "Help me write a LinkedIn post"
   - "Create a Twitter thread"
   - "What hooks work best?"
   - "How do I schedule content?"
5. Verify correct refs are loaded

## Todo List

- [ ] Verify SKILL.md < 100 lines
- [ ] Verify all ref files < 100 lines
- [ ] Verify description < 200 chars
- [ ] Test skill activation
- [ ] Fix any issues found

## Success Criteria

- All line count requirements met
- Skill activates correctly
- Progressive disclosure functioning

## Risk Assessment

- **Low:** Validation is straightforward
- **Mitigation:** Use wc -l for line counts

## Next Steps

Mark optimization complete if all validations pass
