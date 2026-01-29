# Social Content Skill Optimization

## Overview

Optimize the social-content skill from 868 lines to < 100 lines using progressive disclosure pattern.

## Phases

| Phase | Name | Status | Lines |
|-------|------|--------|-------|
| 01 | [Create reference files](phase-01-create-reference-files.md) | completed | 593 |
| 02 | [Rewrite SKILL.md](phase-02-rewrite-skill-md.md) | completed | 77 |
| 03 | [Validate & test](phase-03-validate-and-test.md) | completed | - |

## Key Metrics

| Metric | Before | After |
|--------|--------|-------|
| SKILL.md lines | 868 | 77 |
| Reference files | 0 | 15 |
| Token efficiency | Poor | Optimized |
| Description chars | 342 | 193 |

## Dependencies

- Phase 02 depends on Phase 01 (refs must exist before referencing)
- Phase 03 depends on Phase 02 (skill must be complete before validation)

## File Structure (Target)

```
social-content/
├── SKILL.md (~90 lines)
└── refs/
    ├── platform-linkedin.md
    ├── platform-twitter.md
    ├── platform-instagram.md
    ├── platform-tiktok.md
    ├── platform-facebook.md
    ├── templates-linkedin.md
    ├── templates-twitter.md
    ├── templates-instagram.md
    ├── hook-formulas.md
    ├── content-pillars.md
    ├── content-repurposing.md
    ├── content-calendar.md
    ├── engagement-strategy.md
    ├── analytics-optimization.md
    └── reverse-engineering.md
```
