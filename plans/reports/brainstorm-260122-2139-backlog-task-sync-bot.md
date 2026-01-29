# Brainstorm: Backlog Task Sync Bot

## Problem Statement
Cần bot tự động sync task từ Backlog KH sang Backlog nội bộ với:
- Dịch nội dung JP↔VI
- Assign người phù hợp theo mapping
- Tạo subtasks cho task phát triển

## Solution Overview

### Architecture: CLI Script (Node.js/TypeScript)
```
node sync-task.js HB21373-123
```

**Lý do chọn CLI:**
- Đơn giản, dễ maintain
- Chạy local, không cần hosting
- Dễ debug và extend
- Tích hợp tốt với Claude Code workflow

### Flow Diagram
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Backlog KH     │────▶│   CLI Script     │────▶│ Backlog Internal│
│  (HB21373)      │     │                  │     │                 │
└─────────────────┘     │ 1. Fetch task    │     └─────────────────┘
                        │ 2. Translate     │
                        │ 3. Apply template│
                        │ 4. Create task   │
                        │ 5. Assign user   │
                        │ 6. Add subtasks? │
                        └──────────────────┘
```

## Configuration

### Task Type → Assignee Mapping
| Task Type | Assignee | Create Subtasks |
|-----------|----------|-----------------|
| Bug | CuongNN | ❌ No |
| Feature Request | Duongnh | ✅ Yes |
| Scenario Upload | Duongnh | ❌ No |
| Investigation | CuongNN | ❌ No |

### Subtasks (cho Feature Request)
1. Hearing
2. Create spec file
3. Review spec file
4. Design
5. Coding
6. Create test case
7. Do the test case
8. UAT
9. Create manual file
10. Release

### Template Structure
```markdown
## 📄 Original (JP)
{original_content}

---

## 🇻🇳 Translation (VI)
{translated_content}

---

## 📝 Internal Notes
- Source: {backlog_kh_url}
- Synced: {datetime}
- Original Assignee: {kh_assignee}
```

## Technical Design

### Project Structure
```
experiments/backlog-sync-bot/
├── src/
│   ├── index.ts           # CLI entry point
│   ├── backlog-client.ts  # Backlog API wrapper
│   ├── translator.ts      # Claude translation
│   ├── task-mapper.ts     # Type → Assignee mapping
│   └── template.ts        # Task template builder
├── config/
│   ├── mapping.json       # Configurable mappings
│   └── subtasks.json      # Subtask definitions
├── .env                   # API keys
└── package.json
```

### Dependencies
- `@anthropic-ai/sdk` - Claude translation
- `node-fetch` - Backlog API calls
- `commander` - CLI parsing
- `dotenv` - Environment config

### Environment Variables
```env
# Backlog KH
BACKLOG_KH_SPACE=hblab
BACKLOG_KH_API_KEY=xxx

# Backlog Internal
BACKLOG_INTERNAL_SPACE=hblab-internal
BACKLOG_INTERNAL_API_KEY=xxx
BACKLOG_INTERNAL_PROJECT_KEY=INTERNAL

# Claude
ANTHROPIC_API_KEY=xxx
```

## Usage Examples

### Basic sync (no subtasks)
```bash
# Sync bug/investigation/scenario
node dist/index.js HB21373-456
```

### Sync with subtasks (auto-detect Feature Request)
```bash
# Auto creates 10 subtasks for Feature Request type
node dist/index.js HB21373-789
```

### Force subtasks
```bash
node dist/index.js HB21373-456 --with-subtasks
```

### Skip translation
```bash
node dist/index.js HB21373-456 --no-translate
```

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limit | Medium | Add retry với exponential backoff |
| Translation quality | Low | Human review sau khi sync |
| Duplicate tasks | Medium | Check existing by source URL trước khi tạo |
| API key exposure | High | Store in .env, add to .gitignore |

## Success Criteria
- [ ] Fetch task từ Backlog KH thành công
- [ ] Translate JP↔VI với Claude
- [ ] Create task đúng template
- [ ] Assign đúng người theo mapping
- [ ] Tạo 10 subtasks cho Feature Request
- [ ] Link back to original task

## Open Questions
1. Internal Backlog project key là gì? (cần confirm)
2. Có cần sync attachments không?
3. Có cần sync comments không?
4. Subtasks có cần estimate mặc định không?

## Next Steps
1. Confirm open questions
2. Setup project structure
3. Implement Backlog API client
4. Implement Claude translator
5. Test with real tickets
