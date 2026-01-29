# Social Content Knowledge System

## Overview
Add `knowledge/` directory to `social-content` skill for continuous learning from real content analysis sessions.

**Goal**: Transform skill from static templates → accumulative learning system

## Phases

| Phase | Description | Status | Link |
|-------|-------------|--------|------|
| 1 | Knowledge Directory Setup | ✅ Complete | [phase-01](phase-01-knowledge-directory-setup.md) |
| 2 | SKILL.md Integration | ✅ Complete | [phase-02](phase-02-skill-integration.md) |
| 3 | Seed Initial Lessons | ✅ Complete | [phase-03](phase-03-seed-initial-lessons.md) |
| 4 | Hook Auto-Append | ✅ Complete | [phase-04](phase-04-hook-auto-append.md) |

## Architecture

```
social-content/
├── SKILL.md (+ knowledge workflow + Stop hook)
├── refs/ (existing - unchanged)
├── scripts/
│   └── content-analysis-detector.cjs
└── knowledge/
    ├── README.md (index + usage guide)
    ├── facebook-lessons.md (4 lessons seeded)
    ├── linkedin-lessons.md
    ├── twitter-lessons.md
    ├── instagram-lessons.md
    └── general-patterns.md (1 pattern seeded)
```

## Key Decisions

1. **Platform-specific files**: Grouped by platform for targeted advice
2. **Pattern format**: Concise, actionable, with source attribution
3. **Progressive disclosure**: SKILL.md references, Claude loads only when needed
4. **Append-only**: New lessons appended, no modification to existing entries

## Success Criteria

- [x] Knowledge files created with proper format
- [x] SKILL.md updated with knowledge workflow
- [x] Initial lessons seeded from today's analysis
- [x] Stop hook detects content analysis and logs reminder
- [x] Claude can reference lessons when creating content
