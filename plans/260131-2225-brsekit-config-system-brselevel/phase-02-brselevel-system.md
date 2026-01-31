# Phase 2: brseLevel System

## Overview

- **Priority:** P1
- **Status:** pending
- **Effort:** 1h
- **Depends on:** Phase 1 (config loader)

Define brseLevel L0-L4 system with verbosity guidelines and workflow behavior.

## Context Links

- [Brainstorm Summary](../reports/brainstorm-260131-2214-brsekit-config-system-brselevel.md)
- [ClaudeKit codingLevel reference](../../.claude/hooks/lib/ck-config-utils.cjs)

## brseLevel Definitions

| Level | Name | Verbosity | Guidance | Workflow Suggestions |
|-------|------|-----------|----------|---------------------|
| L0 | Intern | Very detailed | Step-by-step instructions | Proactive |
| L1 | Junior | Detailed | Tips + warnings | Proactive |
| L2 | Mid | Balanced | When relevant | Ask before |
| L3 | Senior | Concise | Minimal | On-demand |
| L4 | Lead | Raw/compact | None | On-demand |

## Requirements

### Functional
- Get brseLevel from config (default: 2)
- Provide guidelines text for each level
- Skills read BK_BRSE_LEVEL env var for formatting

### Output Examples

**L0-L1 (Detailed):**
```markdown
## Morning Brief - HB21373

### Overnight Updates (3 items)
Đây là các updates từ team JP. Review và respond trong buổi sáng.

1. **ABC-123**: Customer reported bug
   - Severity: High
   - Tip: High = respond within 2h
   - Action: Acknowledge → Investigate → Update
```

**L3-L4 (Compact):**
```markdown
## Brief - HB21373
- 3 updates (1 high)
- 1 blocker: API auth
```

## Implementation

### Add to `bk-config-loader.cjs`

```javascript
const BRSE_LEVEL_NAMES = ['Intern', 'Junior', 'Mid', 'Senior', 'Lead'];

const BRSE_LEVEL_GUIDELINES = {
  0: `## BrSE Level: Intern (L0)
- Output: Very detailed with step-by-step instructions
- Include tips, warnings, action items
- Proactively suggest workflows`,
  1: `## BrSE Level: Junior (L1)
- Output: Detailed with tips and warnings
- Include context for decisions
- Proactively suggest workflows`,
  2: `## BrSE Level: Mid (L2)
- Output: Balanced detail
- Include guidance when relevant
- Ask before suggesting workflows`,
  3: `## BrSE Level: Senior (L3)
- Output: Concise, minimal guidance
- Only include critical information
- Workflows on-demand only`,
  4: `## BrSE Level: Lead (L4)
- Output: Raw/compact data
- No guidance or tips
- Workflows on-demand only`
};

function getBrseLevelName(level) {
  return BRSE_LEVEL_NAMES[level] || 'Unknown';
}

function getBrseLevelGuidelines(level) {
  if (level < 0 || level > 4) return null;
  return BRSE_LEVEL_GUIDELINES[level];
}
```

## Todo List

- [ ] Define BRSE_LEVEL_NAMES array
- [ ] Define BRSE_LEVEL_GUIDELINES object
- [ ] Implement `getBrseLevelName(level)` function
- [ ] Implement `getBrseLevelGuidelines(level)` function
- [ ] Export functions from bk-config-loader.cjs
- [ ] Test all 5 levels return correct guidelines
- [ ] Test out-of-range levels return null

## Success Criteria

1. `getBrseLevelName(2)` returns "Mid"
2. `getBrseLevelGuidelines(0)` returns intern guidelines
3. Invalid levels (< 0 or > 4) return null
4. Guidelines text matches specification

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Level out of range | Return null, let caller handle |
| Config missing brseLevel | Default to 2 (Mid) |

## Next Steps

After completion:
- Phase 3 writes BK_BRSE_LEVEL to env file
- Phase 5 injects guidelines via session-init hook
