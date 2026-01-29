# Brainstorming Report: Nulab Backlog Automation

**Date:** 2026-01-22
**Type:** Brainstorming
**Status:** ✅ AGREED

---

## Problem Statement

**Current Pain Point:**
- Manual copy-paste từ Backlog KH → Backlog nội bộ
- Tốn thời gian, dễ lỗi
- Task template không chuẩn

**Desired Outcome:**
- Automation: Trigger slash command → Bot tự tạo task
- Template động theo loại task
- Dịch thuật 2 chiều (JA ↔ VI)
- Tạo task con cho dev tasks

---

## Requirements

### Functional
- [x] Trigger: `/backlog create-ticket <ticket_id>` slash command
- [x] Source: Nulab Backlog (https://hblab.backlogtool.com/projects/HB21373)
- [x] Destination: Nulab Backlog nội bộ (project ID khác)
- [x] Auth: API Key trong `.env`
- [x] Dịch thuật: AI dịch JA ↔ VI (dùng Claude API)
- [x] Assignee: Default/Unassigned
- [x] Task types:
  - Feature phát triển (cần task con)
  - Upload scenario (KHÔNG cần task con)
  - Điều tra issue (KHÔNG cần task con)
- [x] Template task con: Theo loại task, lưu file config local

### Non-Functional
- [x] Chạy local, dùng Claude Code agentic power
- [x] Maintainable, testable, extensible
- [x] YAGNI - KISS - DRY principles

---

## Evaluated Approaches

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Option 1: Claude Code Skill + Python** | ✅ Agentic AI ✅ Maintainable ✅ Extensible ✅ Integrated | ⚠️ Cài Python deps | **SELECTED** |
| Option 2: N8N/Make | ✅ UI workflow | ❌ No agentic AI ❌ Cần server riêng | REJECTED |
| Option 3: Pure CLI script | ✅ Simple | ❌ No agentic AI ❌ Hard to scale | REJECTED |

---

## Final Solution: Claude Code Skill

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code CLI                           │
│                                                               │
│  /backlog create-ticket HB21373-123                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              .claude/skills/backlog/                         │
│                                                               │
│  skill.json (define slash command)                           │
│  script.py (main logic)                                      │
│  templates/ (task templates)                                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flow Logic                                │
│                                                               │
│  1. Parse ticket ID from command                             │
│  2. Fetch source task from Nulab API                         │
│  3. Detect language (JA/VI)                                  │
│  4. Translate content (Claude API)                           │
│  5. Load template based on task type                         │
│  6. Create destination task with template                    │
│  7. If dev task: Create sub-tasks from template              │
│  8. Return result to user                                    │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Skill | Claude Code Skill | Slash command, agentic context |
| Language | Python 3.10+ | Scripting |
| HTTP | `requests` / `httpx` | Nulab API calls |
| Translate | Claude API (haiku/sonnet) | JA ↔ VI translation |
| Config | JSON/YAML | Task templates |
| Env | `.env` | API keys, project IDs |

### File Structure

```
.claude/skills/backlog/
├── skill.json                 # Skill definition
├── script.py                  # Main logic
├── templates/
│   ├── feature-dev.json       # Template: Feature phát triển
│   ├── upload-scenario.json   # Template: Upload scenario
│   └── investigate-issue.json # Template: Điều tra issue
└── .env.example               # Env template

.env                           # API keys (local, gitignored)
```

### Template Structure (JSON)

```json
{
  "feature-dev": {
    "summary_template": "[KH-{project_id}] {translated_summary}",
    "description_template": "## Original\n{original_description}\n\n## Translation\n{translated_description}",
    "subtasks": [
      {"subject": "Analysis", "estimated_hours": 2},
      {"subject": "Implementation", "estimated_hours": 8},
      {"subject": "Testing", "estimated_hours": 4},
      {"subject": "Code Review", "estimated_hours": 2}
    ],
    "default_assignee": null,
    "default_priority": "normal"
  },
  "upload-scenario": {
    "summary_template": "[Scenario] {translated_summary}",
    "description_template": "{translated_description}",
    "subtasks": [],
    "default_assignee": null,
    "default_priority": "high"
  },
  "investigate-issue": {
    "summary_template": "[Investigate] {translated_summary}",
    "description_template": "## Issue Details\n{translated_description}\n\n## Original\n{original_description}",
    "subtasks": [],
    "default_assignee": null,
    "default_priority": "urgent"
  }
}
```

### Key Implementation Details

**1. Language Detection**
- Simple heuristic: Check for Japanese characters (ひらがな, カタカナ, 漢字)
- Or use Claude API for language detection

**2. Translation Flow**
```python
async def translate_text(text: str, source_lang: str) -> str:
    if source_lang == target_lang:
        return text
    # Use Claude API for translation
    response = await claude_api.translate(text, target=target_lang)
    return response
```

**3. Task Type Detection**
- Rule-based: Keywords in summary/description
- Configurable patterns in template file

**4. Error Handling**
- API rate limiting (Nulab: 100 req/min)
- Network retries with exponential backoff
- Graceful fallback if translation fails

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Nulab API rate limit | Medium | Implement queue + retry |
| Translation accuracy | Medium | Human review option |
| Template mismatch | Low | Config validation on load |
| API key exposure | High | `.env` in `.gitignore` |
| Nulab API changes | Low | Version-specific client |

---

## Success Metrics

- [x] Slash command executes in < 10 seconds
- [x] Translation accuracy > 90% (human review)
- [x] Zero API key leaks
- [x] Template coverage: 100% of task types

---

## Next Steps & Dependencies

### Phase 1: Setup
- [ ] Create skill structure in `.claude/skills/backlog/`
- [ ] Generate Nulab API key
- [ ] Get Claude API key
- [ ] Configure `.env`

### Phase 2: Core Implementation
- [ ] Implement Nulab API client
- [ ] Implement Claude translation
- [ ] Implement template loader
- [ ] Implement main flow

### Phase 3: Testing
- [ ] Test with real tickets
- [ ] Test all task types
- [ ] Test translation quality
- [ ] Test error scenarios

### Phase 4: Polish
- [ ] Add human review mode
- [ ] Add dry-run mode
- [ ] Add logging
- [ ] Documentation

---

## Dependencies

| Item | Type | Status |
|------|------|--------|
| Nulab API Key | External | Pending |
| Claude API Key | External | Pending |
| Source Project ID | Config | Known: HB21373 |
| Destination Project ID | Config | TBD |
| Task Type Rules | Config | To be defined |

---

## Open Questions

1. **Destination Project ID:** Project ID cho backlog nội bộ là gì?
2. **Task Type Detection:** Keywords/patterns để detect task type?
3. **Priority Mapping:** Rules cho mapping priority từ source → destination?
4. **Custom Fields:** Có custom fields nào cần map không?
5. **Attachments:** Cần copy attachments từ source task không?

---

## Appendix: Nulab API Reference

**Base URL:** `https://{space}.backlogtool.com/api/v2/`

**Key Endpoints:**
- `GET /api/v2/issues/{issueId}` - Get issue details
- `POST /api/v2/issues` - Create issue
- `POST /api/v2/issues/{issueId}/comments` - Add comment

**Authentication:** `?apiKey={your_api_key}`

**Rate Limit:** 100 requests/minute, 1000 requests/day

---

*Report generated by brainstorming skill*
*Follows YAGNI - KISS - DRY principles*
