---
title: "bk-status Skill Implementation"
description: "Check project progress: late tasks, overloaded members, health summary"
status: in_progress
priority: P0
effort: 4h
branch: main
tags: [bk-status, backlog, tdd, progress-tracking]
created: 2026-01-28
parent: plans/260128-0933-brsekit-mvp-implementation/plan.md
---

# bk-status Skill Implementation Plan

## Overview

**Purpose:** Check project progress - identify late tasks, overloaded members, project health summary.

**Approach:** TDD - Write tests first, then implement.

**Parent Plan:** [BrseKit MVP](../260128-0933-brsekit-mvp-implementation/plan.md)

---

## Phase Summary

| Phase | Description | Effort | Status |
|-------|-------------|--------|--------|
| [Phase 1](./phase-01-extend-backlog-client.md) | Create bk-status/client.py with list_issues, get_users, get_statuses | 1h | ✅ DONE |
| [Phase 2](./phase-02-tdd-test-fixtures.md) | Create test fixtures & TDD test cases | 1h | ✅ DONE |
| [Phase 3](./phase-03-status-analyzer.md) | Implement core analysis logic | 1.5h | ✅ DONE |
| [Phase 4](./phase-04-skill-structure.md) | Create SKILL.md, command integration | 0.5h | pending |

---

## Key Insights (From Research)

1. **BacklogAPI gaps:** Missing `list_issues()`, `get_users()`, `get_statuses()` - must extend
2. **API pagination:** Max 100 per request, need pagination loop
3. **Rate limiting:** 1s between requests (existing), 429 auto-retry (existing)
4. **Late task logic:** `dueDate < today` AND status is active (not closed)
5. **Workload calc:** Count open issues per assignee

---

## Architecture

```
.claude/skills/bk-status/
├── SKILL.md                    # Workflow instructions
├── scripts/
│   └── status_analyzer.py      # Core analysis logic
├── tests/
│   ├── test_status_analyzer.py # Unit tests
│   └── fixtures/               # Sample data
│       ├── sample_issues.json
│       ├── sample_users.json
│       └── sample_statuses.json
└── references/
    └── api-endpoints.md        # Quick reference
```

**Independent Client (validated):**
- `.claude/skills/bk-status/scripts/backlog_client.py` - Own API client (copy needed code from backlog)
- `.claude/skills/bk-status/scripts/models.py` - Own models (Issue, User, Status with dueDate)

---

## Success Criteria

- [x] `list_issues()` fetches all issues with pagination
- [x] Late tasks identified correctly (due < today, status active)
- [x] Workload calculated per assignee
- [x] Markdown report generated with tables
- [x] All TDD tests pass (29/29)

---

## Dependencies

- Existing `nulab_client.py` with rate limiting, error handling
- Existing `models.py` dataclasses
- Test Backlog project access

---

## Skill Best Practices (from skill-creator)

Reference: [skill-creator SKILL.md](../../.claude/skills/skill-creator/SKILL.md)

### Requirements Checklist

| Requirement | Target | Current Status |
|-------------|--------|----------------|
| SKILL.md size | <100 lines | ✅ 85 lines |
| Description | <200 chars | ✅ ~95 chars |
| Scripts have tests | Required | ✅ tests/ exists |
| .env hierarchy | Required | ✅ Implemented |
| Python over Bash | Preferred | ✅ All Python |
| Progressive disclosure | Principle | ✅ Modular scripts |

### .env Hierarchy (MUST follow)

Order: `process.env` > `.claude/skills/bk-status/.env` > `.claude/skills/.env` > `.claude/.env`

### Writing Style

- Use **imperative/infinitive form** (verb-first)
- Objective, instructional language
- Example: "To fetch issues, run..." NOT "You should run..."

### File Organization

- **scripts/**: Executable code with tests
- **references/**: Reference docs (<100 lines each)
- **assets/**: Files for output (templates, etc.)

### Compliance Actions

- [x] SKILL.md under 100 lines
- [x] Description under 200 chars
- [x] Python scripts (not bash)
- [x] Tests for scripts (test_backlog_client.py, test_models.py)
- [x] .env.example created
- [x] Add test_status_analyzer.py (Phase 2)
- [ ] Verify .env hierarchy in all scripts

---

## Validation Summary

**Validated:** 2026-01-28
**Questions:** 5

### Confirmed Decisions

| Decision | User Choice |
|----------|-------------|
| Overloaded threshold | **>5 issues** (default) |
| Closed status names | **Chỉ "Closed"** (simple, final status only) |
| dueDate handling | **Use Backlog's Due Date field** directly |
| Client architecture | **Tạo bk-status/client.py riêng** (independent, copy needed code) |
| Report output | **Save to file**: `/project-status/yyyymmdd-hhmmss_{projectName}-status.md` |

### Action Items (Plan Revisions Completed)

- [x] **Phase 1:** Changed to "create bk-status/client.py" (independent client)
- [x] **Phase 4:** Updated output to save to `./project-status/yyyymmdd-hhmmss_{projectName}-status.md`
- [x] **Phase 3:** Default closed_status_names is already `["Closed"]`
- [x] **All phases:** dueDate field added to Issue model
