---
title: "BrseKit MVP Implementation"
description: "Standalone AI Kit for BrSE - TDD approach, separate skills with PM mindset"
status: pending
priority: P1
effort: 3w
branch: main
tags: [brsekit, bk, backlog, tdd, skills, pm-mindset]
created: 2026-01-28
validated: 2026-01-28
updated: 2026-01-29
---

# BrseKit (BK) Implementation Plan

## Validated Decisions

| Decision | Choice |
|----------|--------|
| Architecture | **Separate skills** (not grouped) |
| Approach | **TDD** - Test first |
| Test project | Backlog project có sẵn |
| Validation order | init → status → report → task → minutes → analyze |
| Report language default | Japanese (JA) |
| Glossary scope | Per-project |
| Human approval | Only external actions |
| Rate limit handling | Fail fast |
| **Workspace** | **Build in brse-workspace first**, migrate later |
| **Report format (MVP)** | **Markdown only**, add Excel/PPTX later |
| **bk-write vs bk-translate** | **Keep separate** - different use cases, share glossary lib |
| **Project context setup** | **First run (/bk-init)** - dedicated skill |
| **PM templates** | **Customizable** - base templates + user override |

### bk-write vs bk-translate Clarification

| Aspect | bk-write | bk-translate |
|--------|----------|--------------|
| Purpose | **CREATE** Japanese content | **CONVERT** content JA↔VI |
| Input | Ideas/outline (VI/EN) | Existing text to translate |
| Output | Japanese business docs | Translated text |
| Key feature | Templates, keigo level | Preserve technical terms |

### bk-minutes vs bk-task Clarification

| Aspect | bk-minutes | bk-task |
|--------|------------|---------|
| Purpose | **Meeting → Structured output** | **Unstructured text → Tasks** |
| Input | Video/audio/text transcript | Customer email, chat, notes |
| Output | MM doc + Tasks/Issues/Risks | Backlog tasks only |
| Key feature | PM mindset classification | Task parsing |

### bk-analyze → bk-tester Pipeline

| Aspect | bk-analyze | bk-tester |
|--------|------------|-----------|
| Purpose | **Analyze requirements** | **Create test documentation** |
| Input | Requirements, specs, email | Requirements + bk-analyze output |
| Output | Questions, user stories, specs | Test plan, viewpoint, cases, report |
| Key feature | BA mindset, gap analysis | テスト観点抽出, traceability |

**Typical workflow:**
```
Requirements → bk-analyze → Refined specs → bk-tester → Test docs
```

### bk-tester Output Structure (MVP = Markdown)

| Document | Japanese | Description |
|----------|----------|-------------|
| Test Plan | テスト計画書 | Scope, schedule, resources, environments |
| Test Viewpoint | テスト観点表 | Viewpoint matrix từ requirements |
| Test Cases | テストケース一覧 | Test cases với expected results |
| Test Report | テスト報告書 | Execution summary, pass/fail stats |

**Note:** MVP outputs Markdown tables. Excel export (3 sheets) deferred to post-MVP.

---

## Overview

**BrseKit (BK)** - Standalone AI toolkit for BrSE in Japan-Vietnam offshore teams.

**MVP Target:** BrSE role (expandable to Tester/BA later)

**Pain Points Addressed:**
1. Check tiến độ - late tasks, overloaded members
2. Weekly report tốn thời gian
3. Create task từ unstructured customer input
4. Japanese writing consistency
5. **Meeting minutes tốn thời gian** (NEW)
6. **BrSE kiêm BA, skill BA yếu** (NEW)
7. **Test documentation tốn thời gian** (NEW)

---

## Phase Summary (By Validation Priority)

| Phase | Skill | Use Case | Priority | Status |
|-------|-------|----------|----------|--------|
| [Phase 0](./phase-00-bk-init.md) | `bk-init` | Project setup, PM mindset | P0 | pending |
| [Phase 1](./phase-01-bk-status.md) | `bk-status` | Check tiến độ, workload | P0 | pending |
| [Phase 2](./phase-02-bk-report.md) | `bk-report` | Weekly report (Markdown MVP) | P0 | pending |
| [Phase 3](./phase-03-bk-task.md) | `bk-task` | Create task từ unstructured | P1 | pending |
| [Phase 4](./phase-04-bk-write.md) | `bk-write` | Japanese business writing | P2 | pending |
| [Phase 5](./phase-05-bk-translate.md) | `bk-translate` | JA↔VI translation | P2 | pending |
| [Phase 6](./phase-06-kit-structure.md) | Kit finalize | CLAUDE.md, hooks, install | P1 | pending |
| [Phase 7](./phase-07-bk-minutes.md) | `bk-minutes` | Meeting → Tasks/Issues/Risks | P1 | pending |
| [Phase 8](./phase-08-bk-analyze.md) | `bk-analyze` | BA assistant, feature analysis | P1 | pending |
| [Phase 9](./phase-09-bk-tester.md) | `bk-tester` | Test docs (plan, viewpoint, cases, report) | P1 | pending |

---

## Project Context & PM Mindset

### Project Types

| Project Type | Methodology | Key Focus Areas |
|-------------|-------------|-----------------|
| **Project-based (請負)** | Waterfall | CR tracking, Budget, Schedule, Milestones |
| **Labor (派遣/SES)** | Agile | Quality, Priority, Communication, Sprint goals |
| **Hybrid** | Mix | Both: CR + Quality, Schedule + Sprint |

### project-context.yaml Structure

```yaml
project:
  name: "Project Name"
  backlog_key: "PROJ"
  type: "project-based"  # or "labor", "hybrid"
  methodology: "waterfall"

customer:
  name: "Customer Corp"
  industry: "Finance"
  timezone: "JST"
  communication_style: "formal"

focus_areas:
  primary: [change_request_tracking, budget_monitoring]
  secondary: [documentation_quality]

warning_triggers:
  high: ["scope change", "追加要件", "budget", "delay"]
  medium: ["clarification", "確認"]

pm_checklist:
  weekly: ["Review CR status", "Check budget burn rate"]
  meeting: ["Confirm scope alignment", "Track action items"]
```

---

## Architecture (Updated)

```
brsekit/
├── CLAUDE.md                      # Kit overview, skill index
├── README.md                      # Installation guide
├── install.sh / install.ps1      # Setup scripts
├── .env.example
│
├── skills/                        # Each skill independent
│   ├── bk-init/                   # P0: Project setup
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── tests/
│   │
│   ├── bk-status/                 # P0: Check tiến độ
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── references/
│   │   └── tests/
│   │
│   ├── bk-report/                 # P0: Weekly report
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── templates/
│   │   └── tests/
│   │
│   ├── bk-task/                   # P1: Create task
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── tests/
│   │
│   ├── bk-minutes/                # P1: Meeting minutes (NEW)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── templates/
│   │   └── tests/
│   │
│   ├── bk-analyze/                # P1: BA assistant (NEW)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── tests/
│   │
│   ├── bk-tester/                 # P1: Test documentation (NEW)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── templates/             # Test doc templates
│   │   └── tests/
│   │
│   ├── bk-write/                  # P2: Japanese writing
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── templates/
│   │   └── tests/
│   │
│   └── bk-translate/              # P2: Translation
│       ├── SKILL.md
│       ├── scripts/
│       ├── glossaries/
│       └── tests/
│
├── lib/                           # Shared utilities
│   ├── backlog_client.py
│   ├── context_loader.py          # NEW: Load project-context.yaml
│   ├── pm_mindset.py              # NEW: PM rules engine
│   ├── language_detector.py
│   └── models.py
│
├── pm-templates/                  # NEW: Base PM templates
│   ├── waterfall.yaml
│   ├── agile.yaml
│   └── hybrid.yaml
│
├── project-context.yaml           # Generated per project by bk-init
│
└── tests/                         # Integration & E2E tests
    ├── integration/
    └── evals/
```

---

## Commands

| Command | Skill | Description |
|---------|-------|-------------|
| `/bk-init` | bk-init | Setup project context, PM mindset |
| `/bk-status` | bk-status | Check tiến độ, late tasks, workload |
| `/bk-report` | bk-report | Generate weekly report |
| `/bk-task` | bk-task | Create task từ unstructured input |
| `/bk-minutes <input>` | bk-minutes | Meeting → MM doc + Tasks/Issues/Risks |
| `/bk-analyze <input>` | bk-analyze | Analyze requirements, generate questions/stories |
| `/bk-analyze feature "<desc>"` | bk-analyze | Feature-specific analysis |
| `/bk-tester <input>` | bk-tester | Generate test docs từ requirements |
| `/bk-tester plan` | bk-tester | Generate test plan |
| `/bk-tester viewpoint` | bk-tester | Generate test viewpoint matrix |
| `/bk-tester cases` | bk-tester | Generate test cases |
| `/bk-tester report` | bk-tester | Generate test report |
| `/bk-write` | bk-write | Japanese business writing |
| `/bk-translate` | bk-translate | JA↔VI translation |
| `/bk-glossary` | bk-translate | Manage glossary |

---

## TDD Workflow (Per Skill)

```
1. Define test cases (input, expected output)
2. Create test fixtures (sample Backlog data)
3. Write tests → all FAIL
4. Implement skill code
5. Run tests → all PASS
6. Integration test với real Backlog
7. Refactor if needed
```

---

## Test Fixtures

| Fixture | Description |
|---------|-------------|
| `sample_project.json` | Project với tasks (late, on-time, mixed) |
| `sample_members.json` | 3+ members với different workload |
| `sample_unstructured_input.txt` | Customer messages in Japanese |
| `sample_meeting_transcript.txt` | Meeting transcript JA+VI |
| `sample_customer_email.txt` | Customer email for analysis |
| `sample_requirements.md` | Requirements for bk-analyze/bk-tester |
| `expected_report.md` | Expected report output |
| `expected_test_plan.md` | Expected test plan output |
| `expected_test_viewpoint.md` | Expected viewpoint matrix |
| `expected_test_cases.md` | Expected test cases |

---

## Success Criteria

| Skill | Criteria |
|-------|----------|
| `bk-init` | Generate valid project-context.yaml với user input |
| `bk-status` | Show late tasks, overloaded members chính xác |
| `bk-report` | Generate weekly report đúng template |
| `bk-task` | Create structured task từ unstructured JP input |
| `bk-minutes` | Classify Task/Issue/Risk/Question với PM mindset |
| `bk-analyze` | Generate questions, user stories, requirements |
| `bk-tester` | Generate test plan, viewpoint, cases, report từ requirements |
| `bk-write` | Consistent Japanese output với same template |
| `bk-translate` | Preserve technical terms, glossary working |

---

## Key Dependencies

- Existing `backlog` skill: `nulab_client.py`, `language_detector.py`
- `ai-multimodal` skill: Video/audio transcription for bk-minutes
- Nulab Backlog API v2
- Test Backlog project (có sẵn)

---

## Skills to Migrate (Post-MVP)

When migrating to standalone workspace, bring:

| Category | Skills |
|----------|--------|
| **Essential** | `backlog`, `skill-creator`, `planning`, `brainstorming`, `code-review`, `debugging`, `fixing`, `git`, `docs-seeker`, `sequential-thinking` |
| **Nice to have** | `mcp-builder`, `ai-multimodal` |

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Backlog API limitations | Medium | Extend client, manual fallback |
| Template complexity (PPTX) | Low (MVP) | **MVP = Markdown only**, Excel/PPTX deferred |
| Scope creep | High | Strict P0 first |
| TDD overhead | Low | Pay upfront, save debugging time |
| Video transcription accuracy | Medium | Use ai-multimodal (Gemini), allow text input fallback |
| PM mindset complexity | Medium | Start with 3 base templates, iterate |
