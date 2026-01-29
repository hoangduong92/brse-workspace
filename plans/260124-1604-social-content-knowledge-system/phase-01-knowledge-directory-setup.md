# Phase 1: Knowledge Directory Setup

## Overview
- **Priority**: High
- **Status**: Pending
- **Estimate**: Quick (~10 min)

## Requirements

Create knowledge directory structure with:
1. `README.md` - Index and usage guide
2. Platform-specific lesson files (initially empty templates)
3. `general-patterns.md` - Cross-platform patterns

## Implementation Steps

### Step 1: Create Directory
```bash
mkdir -p .claude/skills/social-content/knowledge
```

### Step 2: Create README.md
Content:
- Purpose of knowledge directory
- How to add new lessons
- Lesson format specification
- Quick reference to lesson files

### Step 3: Create Lesson File Templates
Files to create:
- `facebook-lessons.md`
- `linkedin-lessons.md`
- `twitter-lessons.md`
- `instagram-lessons.md`
- `general-patterns.md`

Each file starts with:
- Header with platform name
- Empty sections ready for lessons
- Format example commented

## Lesson Format Specification

```markdown
## ✅ Pattern: [Short Descriptive Name]
- **Source**: [YYYY-MM-DD] | [Content Type/Topic]
- **Context**: [Brief situation description]
- **Lesson**: [What to do]
- **Apply when**: [Trigger conditions]

## ❌ Anti-Pattern: [Short Descriptive Name]
- **Source**: [YYYY-MM-DD] | [Content Type/Topic]
- **Issue**: [What went wrong]
- **Fix**: [How to correct]
- **Why matters**: [Impact explanation]
```

## Todo List

- [ ] Create knowledge directory
- [ ] Create README.md with usage guide
- [ ] Create facebook-lessons.md template
- [ ] Create linkedin-lessons.md template
- [ ] Create twitter-lessons.md template
- [ ] Create instagram-lessons.md template
- [ ] Create general-patterns.md template

## Success Criteria

- Directory structure exists
- All template files have consistent format
- README clearly explains usage

## Next Steps

→ Phase 2: Update SKILL.md to reference knowledge directory
