---
title: "Backlog Task Sync Bot"
description: "CLI tool to sync tasks from KH Backlog to Internal with JP-VI translation"
status: pending
priority: P2
effort: 6h
branch: main
tags: [cli, backlog, translation, automation]
created: 2026-01-22
---

# Backlog Task Sync Bot

## Overview
CLI tool (Node.js/TypeScript) to sync tasks from Backlog KH to Internal Backlog with:
- Japanese-Vietnamese translation via Claude Sonnet 4.5
- Auto-assignment based on task type mapping
- Subtask generation for Feature Requests
- Attachment synchronization

## Architecture
```
User → CLI (commander) → Backlog Client (fetch KH task)
                      → Translator (Claude API)
                      → Task Mapper (type → assignee)
                      → Backlog Client (create internal task + subtasks)
```

## Phases

| Phase | Description | Effort | Status |
|-------|-------------|--------|--------|
| [Phase 01](phase-01-project-setup.md) | Project init, deps, env config | 0.5h | pending |
| [Phase 02](phase-02-backlog-api-client.md) | Backlog API client implementation | 1.5h | pending |
| [Phase 03](phase-03-claude-translator.md) | Claude translation service | 1h | pending |
| [Phase 04](phase-04-task-mapper-template.md) | Task mapper & template builder | 1h | pending |
| [Phase 05](phase-05-cli-integration.md) | CLI integration & testing | 2h | pending |

## Key Dependencies
- `@anthropic-ai/sdk` - Claude translation
- `commander` - CLI framework
- `dotenv` - Environment config

## Configuration
- Task mapping: Bug/Investigation → CuongNN; Feature Request/Scenario Upload → Duongnh
- Subtasks: Only for Feature Request (10 items)
- Location: `experiments/backlog-sync-bot/`

## Success Criteria
- [ ] Fetch task from Backlog KH
- [ ] Translate JP↔VI accurately
- [ ] Create task with correct template
- [ ] Assign based on type mapping
- [ ] Generate subtasks for Feature Requests
- [ ] Sync attachments

## Validation Summary

**Validated:** 2026-01-22
**Questions asked:** 6

### Confirmed Decisions
- **Test Setup:** Use HB21373 for both KH and Internal during testing; configure separate spaces later
- **User Mapping:** Hardcode user IDs in config file (get IDs once from Backlog)
- **Translation:** JP→VI only (KH sends Japanese, internal uses Vietnamese)
- **Duplicate Handling:** Check existing by source URL, skip if already synced
- **Attachments:** Sync all attachments (images, docs, files)
- **Error Handling:** Continue on partial failure, report errors at end

### Action Items
- [ ] Add duplicate check logic in Phase 05 (search by source URL in description)
- [ ] Simplify translator to JP→VI only
- [ ] Get actual user IDs for CuongNN, Duongnh before implementation

## Resolved Questions
1. ~~Internal Backlog project key?~~ → HB21373 (same as KH for testing)
2. ~~User IDs for CuongNN/Duongnh?~~ → Hardcode in config after lookup
