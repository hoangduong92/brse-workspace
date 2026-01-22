---
title: "Nulab Backlog Automation"
description: "Automate ticket creation from customer backlog to internal backlog with AI translation"
status: pending
priority: P1
effort: 14h
branch: main
tags: [automation, backlog, translation, claude-code-skill]
created: 2026-01-22
---

## Overview

Automate manual copy-paste workflow from customer Backlog (HB21373) to internal Backlog using Claude Code slash command with AI translation (JA ↔ VI) and dynamic task templates.

## Status Summary

| Phase | Status | Progress |
|-------|--------|----------|
| Phase 01: Project Setup | pending | 0% |
| Phase 02: Nulab API Client | pending | 0% |
| Phase 03: Claude Translation | pending | 0% |
| Phase 04: Template System | pending | 0% |
| Phase 05: Main Skill Logic | pending | 0% |
| Phase 06: Testing & Validation | pending | 0% |

## Architecture

```
/backlog create-ticket HB21373-123
         ↓
┌─────────────────────────────────────┐
│  Claude Code Skill (backlog/)       │
│  ├─ Parse ticket ID                 │
│  ├─ Fetch source task (Nulab API)   │
│  ├─ Detect language (JA/VI)         │
│  ├─ Translate (Claude API)          │
│  ├─ Load template (by task type)    │
│  ├─ Create destination task         │
│  └─ Create subtasks (if dev task)   │
└─────────────────────────────────────┘
```

## Key Features

- **Slash Command**: `/backlog create-ticket <ticket_id>`
- **AI Translation**: Claude API (Haiku/Sonnet) JA ↔ VI
- **Dynamic Templates**: Feature dev, Upload scenario, Investigate issue
- **Auto Subtasks**: Only for feature development tasks
- **Local Execution**: Claude Code agentic power

## Phase Files

- [Phase 01: Project Setup](phase-01-project-setup.md) - 2h
- [Phase 02: Nulab API Client](phase-02-nulab-api-client.md) - 3h
- [Phase 03: Claude Translation Service](phase-03-claude-translation.md) - 2h
- [Phase 04: Template System](phase-04-template-system.md) - 2h
- [Phase 05: Main Skill Logic](phase-05-main-skill-logic.md) - 3h
- [Phase 06: Testing & Validation](phase-06-testing-validation.md) - 2h

## Validation Summary

**Validated:** 2026-01-22
**Questions asked:** 7

### Confirmed Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Task Type Detection** | Hybrid (keyword + --type flag) | Flexibility with override option |
| **Attachments** | Yes, copy from source | User wants complete ticket copy |
| **Priority Mapping** | Copy from source | Preserve original priority |
| **Error Rollback** | No, manual cleanup | Safer, partial review |
| **Project Scope** | Same project (HB21373) for MVP | Test workflow first, customer URL later |
| **Assignee** | Auto-assign by type | User wants auto-routing |

### Updated Scope

**MVP Configuration:**
- Source = Destination = HB21373 (same project, same API key)
- Later: Customer will provide separate project ID
- Auto-assign by task type (configurable in templates)

### Action Items

- [ ] Update phase files to reflect same-project workflow
- [ ] Add `--type` flag for manual task type override
- [ ] Add attachment copying to Phase 02 (Nulab API Client)
- [ ] Update priority handling to copy from source
- [ ] Add assignee mapping in templates
- [ ] Remove rollback logic (manual cleanup only)

## Dependencies

- Nulab API Key (HB21373 project)
- Claude API Key (translation)
- Project ID: HB21373 (MVP - same project for source/destination)
- Assignee mapping by task type (TBD in templates)

## Remaining Open Questions

1. Exact assignee IDs for each task type?
2. Custom fields requirements (defer - user doesn't know yet)?

## Success Criteria

- [ ] Slash command executes < 10 seconds
- [ ] Translation accuracy > 90% (human review)
- [ ] Zero API key leaks (.env in .gitignore)
- [ ] 100% template coverage for all task types
- [ ] All tests passing

---

**Next**: Start with [Phase 01: Project Setup](phase-01-project-setup.md)
