---
title: "bk-translate & bk-tester Parallel Implementation"
description: "Implement two BrseKit skills in parallel - translation and test documentation"
status: in_progress
priority: P1
branch: main
tags: [brsekit, bk-translate, bk-tester, tdd, parallel]
created: 2026-01-29
---

# bk-translate & bk-tester Parallel Implementation

## Overview

Implement two independent BrseKit skills in parallel:
1. **bk-translate** (Phase 5) - JA↔VI translation with glossary
2. **bk-tester** (Phase 9) - Test documentation generator

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                      PARALLEL EXECUTION                      │
├─────────────────────────┬───────────────────────────────────┤
│   Phase 1: bk-translate │   Phase 2: bk-tester              │
│   - translator.py       │   - viewpoint_extractor.py        │
│   - glossary_manager.py │   - test_case_generator.py        │
│   - SKILL.md            │   - test_plan_generator.py        │
│   - tests               │   - report_generator.py           │
│                         │   - templates                     │
│                         │   - tests                         │
└─────────────────────────┴───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      SEQUENTIAL                              │
│   Phase 3: Integration testing & code review                 │
└─────────────────────────────────────────────────────────────┘
```

## File Ownership Matrix

| Phase | Owner Agent | Files |
|-------|-------------|-------|
| 1 | fullstack-developer-1 | `.claude/skills/bk-translate/**` |
| 2 | fullstack-developer-2 | `.claude/skills/bk-tester/**` |
| 3 | tester + code-reviewer | Both skill directories |

## Execution Strategy

### Parallel Phases (1-2)
- Launch 2 fullstack-developer agents simultaneously
- No file conflicts - separate directories
- Each follows TDD approach

### Sequential Phase (3)
- Run after both parallel phases complete
- Integration testing
- Code review

## Phase Summary

| Phase | Skill | Status |
|-------|-------|--------|
| [Phase 1](./phase-01-bk-translate.md) | bk-translate | pending |
| [Phase 2](./phase-02-bk-tester.md) | bk-tester | pending |
| Phase 3 | Integration & Review | pending |

## Shared Dependencies

Both skills use:
- `.claude/skills/common/backlog/` - BacklogClient (read-only)
- `.claude/skills/backlog/scripts/language_detector.py` - LanguageDetector (read-only)
- `.claude/skills/backlog/scripts/models.py` - Language enum (read-only)

## Success Criteria

| Skill | Criteria |
|-------|----------|
| bk-translate | Auto-detect JA/VI, translate with glossary preservation |
| bk-tester | Generate test plan, viewpoint, cases, report in Japanese |
