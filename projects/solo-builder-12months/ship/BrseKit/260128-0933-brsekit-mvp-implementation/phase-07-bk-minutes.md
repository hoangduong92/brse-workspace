# Phase 7: bk-minutes - Meeting Minutes with PM Mindset

## Overview
- **Priority:** P1
- **Status:** pending
- **Skill:** `bk-minutes`
- **Approach:** TDD
- **Dependencies:** ai-multimodal (transcription), bk-task (task creation)

## Pain Point
> "Meeting minutes tốn thời gian, khó extract action items, không phân biệt được Task/Issue/Risk"

## Input
```
/bk-minutes <video.mp4>           # From video
/bk-minutes <audio.mp3>           # From audio
/bk-minutes <transcript.txt>      # From text
```

## Expected Output
- Full meeting minutes document (Template chuẩn)
- Classified items: Tasks, Issues, Risks, Questions
- Preview before creating Backlog items (Always approval)
- Save MM to Backlog Document

## Key Features

### 1. Input Processing

| Input Type | Processing |
|------------|------------|
| Video (mp4, webm) | ai-multimodal → transcribe → parse |
| Audio (mp3, wav) | ai-multimodal → transcribe → parse |
| Text (txt, md) | Direct parse |

### 2. Language Support
- Japanese + Vietnamese mixed meetings
- Auto-detect language per segment

### 3. Full Meeting Minutes Template

```markdown
# Meeting Minutes - [Date]

## 基本情報 / Thông tin cơ bản
- **Date:** 2026-01-29
- **Participants:** Tanaka (ABC Corp), Nguyen (Dev Team)
- **Duration:** 60 min

## アジェンダ / Agenda
1. Sprint review
2. Next sprint planning
3. CR discussion

## 決定事項 / Decisions
- [ ] Approved: New payment feature scope
- [ ] Rejected: Additional API endpoints (out of budget)

## 📋 TASKS (3)
| # | Description | Assignee | Deadline |
|---|-------------|----------|----------|
| 1 | Implement login API | @Tuan | 2026-02-05 |
| 2 | Design mockup | @Linh | 2026-02-03 |
| 3 | Review specs | @Hiro | 2026-02-01 |

## 🐛 ISSUES (1)
| # | Description | Priority |
|---|-------------|----------|
| 1 | Payment timeout on staging | High |

## ⚠️ RISKS (2)
| # | Description | Impact | Mitigation |
|---|-------------|--------|------------|
| 1 | Deadline tight for Phase 2 | High | Reduce scope |
| 2 | Customer might change scope | Medium | Document CR |

## ❓ NEED CONFIRMATION (1)
| # | Question | Ask to |
|---|----------|--------|
| 1 | Budget for additional server? | Customer |

## Next Steps
- Follow up on NEED CONFIRMATION items
- Create Backlog tasks for approved TASKS
```

### 4. PM Mindset Classification

| Category | Trigger Keywords | Backlog Action |
|----------|------------------|----------------|
| **Task** | "sẽ làm", "implement", "作成する" | Create Task issue |
| **Issue/Bug** | "lỗi", "bug", "問題", "エラー" | Create Bug issue |
| **Risk** | "nếu", "có thể", "リスク", "心配" | Create Issue (Risk type) |
| **Question** | "cần confirm", "確認", "chưa rõ" | Flag for follow-up |

### 5. Context-Aware Classification (PM Mindset)

**Without project-context:**
```
"追加要件" → Task: Handle additional requirements
```

**With project-context (project-based/waterfall):**
```
"追加要件" → ⚠️ RISK: Scope change detected
           → Suggest: Create CR document
           → Remind: Check budget impact
```

### 6. Approval Flow

```
┌─────────────────────────────────────┐
│         Preview Action Items        │
├─────────────────────────────────────┤
│ 📋 TASKS (3)                        │
│   ☑ Implement login API - @Tuan    │
│   ☑ Design mockup - @Linh          │
│   ☐ Review specs - @Hiro (skip)    │
├─────────────────────────────────────┤
│ 🐛 ISSUES (1)                       │
│   ☑ Payment timeout on staging     │
├─────────────────────────────────────┤
│ ⚠️ RISKS (2)                        │
│   ☑ Deadline tight for Phase 2     │
│   ☑ Customer might change scope    │
└─────────────────────────────────────┘
     [Create Selected] [Edit] [Skip]
```

## Architecture

```
brsekit/skills/bk-minutes/
├── SKILL.md
├── scripts/
│   ├── main.py
│   ├── transcriber.py         # Use ai-multimodal
│   ├── mm_parser.py           # Parse transcript
│   ├── item_classifier.py     # Classify Task/Issue/Risk/Question
│   └── mm_generator.py        # Generate MM document
├── templates/
│   └── mm_template.md
└── tests/
    ├── fixtures/
    │   ├── sample_transcript_ja_vi.txt
    │   └── expected_mm_output.md
    ├── test_transcriber.py
    ├── test_mm_parser.py
    └── test_item_classifier.py
```

## Key Test Cases

1. Transcribe video → accurate text (JA+VI)
2. Parse transcript → extract attendees, agenda, decisions
3. Classify items correctly: Task vs Issue vs Risk vs Question
4. Context-aware: detect CR/scope change in waterfall project
5. Generate MM document với full template
6. Approval flow: preview → select → create

## Dependencies

- `ai-multimodal` skill: Video/audio transcription
- `bk-task` skill: Create tasks in Backlog
- `lib/context_loader.py`: Load project context
- `lib/pm_mindset.py`: PM rules for classification
- Nulab Backlog API: Create issues, upload document

## Success Criteria

- [ ] Transcribe video/audio với accuracy >90% (JA+VI mixed)
- [ ] Extract attendees, agenda, decisions correctly
- [ ] Classify Task/Issue/Risk/Question với PM mindset
- [ ] Context-aware classification based on project type
- [ ] Preview approval flow working
- [ ] Save MM to Backlog Document

## Detailed plan: TBD after Phase 3 (bk-task) complete
