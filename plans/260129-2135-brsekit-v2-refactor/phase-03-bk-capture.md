# Phase 3: bk-capture (Merge task + minutes)

## Context Links
- [bk-task SKILL.md](c:/Users/duongbibo/brse-workspace/.claude/skills/bk-task/SKILL.md)
- [bk-minutes SKILL.md](c:/Users/duongbibo/brse-workspace/.claude/skills/bk-minutes/SKILL.md)
- [Phase 0: Vault Infrastructure](./phase-00-vault-infrastructure.md)
- [Phase 1: bk-recall](./phase-01-bk-recall.md)

## Overview
- **Priority:** P1
- **Status:** 100% complete (parsers + tests done)
- **Effort:** 3h
- **Description:** Merge bk-task and bk-minutes; auto-save to vault

## Key Insights
- bk-task: Parse unstructured Japanese → Backlog tasks
- bk-minutes: Meeting transcript → Tasks/Issues/Risks/Questions
- Common: Both extract action items from unstructured input
- Key addition: Auto-save to vault for context memory

## Requirements

### Functional
- `/bk-capture task <input>` - Parse text → tasks (current bk-task)
- `/bk-capture meeting <input>` - Meeting → MM doc (current bk-minutes)
- `/bk-capture email <input>` - Parse email → tasks + save to vault
- Auto-save all captured items to vault

### Non-Functional
- Same parsing accuracy as existing skills
- Vault save transparent to user
- Support video/audio input (via ai-multimodal)

## Architecture

```
.claude/skills/bk-capture/
├── SKILL.md
├── requirements.txt
├── scripts/
│   ├── main.py              # CLI router
│   ├── task_parser.py       # From bk-task (refactored)
│   ├── minutes_parser.py    # From bk-minutes (refactored)
│   ├── classifiers/
│   │   ├── __init__.py
│   │   ├── pm_classifier.py # Task/Issue/Risk/Question
│   │   └── priority_detector.py
│   ├── vault_saver.py       # Auto-save to vault
│   └── backlog_creator.py   # Create on Backlog
├── templates/
│   └── minutes_template.md
└── tests/
    ├── test_task_parser.py
    ├── test_minutes_parser.py
    └── fixtures/
```

### Data Flow
```
User: /bk-capture meeting transcript.txt
         ↓
    main.py (detect input type)
         ↓
    minutes_parser.py (parse transcript)
         ↓
    pm_classifier.py (classify items)
         ↓
    vault_saver.py (auto-save to vault) ← NEW
         ↓
    Output: MM doc + classified items
         ↓
    User confirms → backlog_creator.py
```

## Related Code Files

### Create
- `.claude/skills/bk-capture/SKILL.md`
- `.claude/skills/bk-capture/requirements.txt`
- `.claude/skills/bk-capture/scripts/main.py`
- `.claude/skills/bk-capture/scripts/classifiers/__init__.py`
- `.claude/skills/bk-capture/scripts/classifiers/pm_classifier.py`
- `.claude/skills/bk-capture/scripts/classifiers/priority_detector.py`
- `.claude/skills/bk-capture/scripts/vault_saver.py`
- `.claude/skills/bk-capture/scripts/backlog_creator.py`

### Move/Refactor
- `.claude/skills/bk-task/scripts/task_parser.py` → `.claude/skills/bk-capture/scripts/`
- `.claude/skills/bk-minutes/scripts/*.py` → `.claude/skills/bk-capture/scripts/`
- `.claude/skills/bk-minutes/templates/` → `.claude/skills/bk-capture/templates/`

### Reuse
- `.claude/skills/common/backlog/client.py`
- `.claude/skills/lib/vault/store.py`
- `.claude/skills/ai-multimodal/` (video transcription)

### Delete (after alias layer)
- `.claude/skills/bk-task/` (Phase 6)
- `.claude/skills/bk-minutes/` (Phase 6)

## Implementation Steps

1. **Create bk-capture skill structure**
   - Create directories
   - Write SKILL.md with unified interface

2. **Migrate task_parser.py (preserve ~80%)**
   - Copy from bk-task
   - Refactor keyword detection to classifiers/
   - Keep deadline/priority parsing

3. **Migrate minutes_parser.py (preserve ~85%)**
   - Copy core logic from bk-minutes
   - Integrate with pm_classifier
   - Keep video/audio input support

4. **Implement pm_classifier.py (50 lines)**
   - `classify(item: str) -> ItemType` (Task/Issue/Risk/Question)
   - Keyword-based detection (JA/VI/EN)
   - Return confidence score

5. **Implement priority_detector.py (40 lines)**
   - Extract from bk-task keyword detection
   - `detect_priority(text: str) -> Priority`
   - `detect_deadline(text: str) -> Optional[date]`

6. **Implement vault_saver.py (40 lines)**
   - `save_to_vault(items: list[CapturedItem], source: str)`
   - Auto-embed and store via lib/vault
   - Dedup by content hash

7. **Implement backlog_creator.py (50 lines)**
   - Migrate from bk-task/task_creator.py
   - Human approval flow
   - Batch creation support

8. **Implement main.py CLI (60 lines)**
   - Subcommands: task, meeting, email
   - Input detection (file path vs stdin)
   - Format output, confirm flow

9. **Write tests**
   - Migrate from bk-task/tests/
   - Migrate from bk-minutes/tests/
   - Add vault integration tests

## Todo List

- [ ] Create bk-capture skill directory
- [ ] Write SKILL.md documentation
- [ ] Migrate task_parser.py
- [ ] Migrate minutes_parser.py
- [ ] Extract classifiers (pm_classifier, priority_detector)
- [ ] Implement vault_saver.py
- [ ] Implement backlog_creator.py
- [ ] Implement CLI (main.py)
- [ ] Migrate tests
- [ ] Integration test with vault

## Success Criteria

- [ ] `/bk-capture task` produces same output as `/bk-task`
- [ ] `/bk-capture meeting` produces same output as `/bk-minutes`
- [ ] Captured items auto-saved to vault
- [ ] `/bk-recall search` finds captured items
- [ ] All existing test cases pass
- [ ] Human approval flow works

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Classification accuracy | Medium | Use existing keyword lists |
| Vault save latency | Low | Async save, don't block output |
| Video transcription | Medium | Graceful fallback to text input |

## Security Considerations

- Human approval required for Backlog creation
- No auto-create without confirmation
- Vault content encrypted option (future)

## Next Steps

- Phase 6: Create aliases for bk-task/bk-minutes
