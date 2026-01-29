# BrseKit Test Cases Brainstorm Report

**Date:** 2026-01-28
**Status:** Draft
**Context:** [BrseKit MVP Plan](../260128-0933-brsekit-mvp-implementation/plan.md)

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Progress calculation | actual_hours / estimate_hours | Real-world progress, not binary |
| No estimate handling | Warning + require input | Force proper estimation |
| Daily capacity | effort × standard_capacity × 8h | VD: 1.0 × 75% × 8h = 6h/day |
| Work days | Weekdays only (Mon-Fri) | Skip weekends |
| Overload threshold | Configurable | Default 100%, user can adjust |
| Dependencies | Custom field + text parse fallback | Flexibility |
| bk-risk | Separate skill | Invoke bk-status, add risk layer |

---

## Skill: bk-status

### Progress Calculation

| ID | Test Case | Input | Expected |
|----|-----------|-------|----------|
| TC-S01 | Normal progress | est=16h, actual=4h | 25% |
| TC-S02 | Overtime | est=8h, actual=12h | 150% + warning |
| TC-S03 | No estimate | est=null | ⚠️ Warning |
| TC-S04 | No actual | est=16h, actual=0h | 0% |
| TC-S05 | Closed task | status=Closed | 100% |

### Deadline Risk

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-S06 | On track | remain=12h, days=3, cap=6h/day | ✅ On track |
| TC-S07 | At risk | remain=12h, days=2, cap=6h/day | ⚠️ At risk |
| TC-S08 | Late | remain=12h, days=1, cap=6h/day | 🔴 Late |
| TC-S09 | Weekend skip | Fri→Mon, remain=8h | days_left=1 |
| TC-S10 | Overdue | due < today | 🔴 Overdue X days |

### Member Workload

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-S11 | Normal load | 20h/30h available | 67% ✅ |
| TC-S12 | Threshold hit | 30h/30h, threshold=100% | ⚠️ Overloaded |
| TC-S13 | Severe overload | 50h/30h available | 🔴 167% |
| TC-S14 | Part-time | effort=0.5 → 3h/day | Calculate correctly |
| TC-S15 | Multiple tasks | 5 tasks, diff deadlines | Aggregate workload |

### Task Scheduling & Overlap

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-S20 | Sequential fit | 3 tasks, 60h, cap 60h | ✅ EDF order |
| TC-S21 | Overlap conflict | 2 tasks same due, total > cap | ⚠️ Overlap detected |
| TC-S22 | Scheduling suggestion | Overload detected | 💡 Move task X |
| TC-S23 | Buffer analysis | 60h work, 70h available | ✅ 10h buffer |
| TC-S24 | No slack | Back-to-back | ⚠️ No slack |

### Dependencies

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-S16 | Blocked task | B depends on A (Open) | 🔴 B blocked |
| TC-S17 | Unblocked | A=Closed → B | ✅ B can start |
| TC-S18 | Chain | A→B→C, A not done | B,C blocked |

---

## Skill: bk-risk (NEW)

### Dependency Analysis

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-R01 | Custom field | "Blocked By"="BKT-10" | Parse OK |
| TC-R02 | Text fallback | Desc: "Wait for BKT-10" | Detect dependency |
| TC-R03 | Chain | A→B→C | Show critical path |
| TC-R04 | Circular | A→B→A | 🔴 Error |
| TC-R05 | Bottleneck | BKT-10 blocks 3 tasks | 🔴 High risk |

### Workload Risk

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-R06 | SPOF | 1 member has 80% critical | 🔴 SPOF warning |
| TC-R07 | Balanced | Even distribution | ✅ Low risk |
| TC-R08 | Knowledge silo | Only Tanaka knows X | ⚠️ Share knowledge |

### Schedule Risk

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-R09 | Multiple late | 3+ overdue | 🔴 Schedule at risk |
| TC-R10 | Cascade delay | Blocker late | Calculate impact |

### Recommendations

| ID | Test Case | Scenario | Expected Output |
|----|-----------|----------|-----------------|
| TC-R11 | No custom field | Field missing | "Add 'Blocked By' field" |
| TC-R12 | Reassignment | Overload | "Move Task X to Y" |
| TC-R13 | Priority adjust | Blocker low priority | "Raise priority" |

---

## Skill: bk-report

### Data Aggregation

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-RP01 | Progress summary | From bk-status | "65% complete" |
| TC-RP02 | Risk integration | From bk-risk | "3 high-risk items" |
| TC-RP03 | Week-over-week | Compare last week | "+15% vs last week" |
| TC-RP04 | Milestone | Goal 80%, actual 65% | ⚠️ "Behind 15%" |

### Content Generation

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-RP05 | Accomplishments | Tasks closed | Bullet list |
| TC-RP06 | Blockers | From bk-risk | List blockers |
| TC-RP07 | Next week | Tasks due | Prioritized list |
| TC-RP08 | Empty week | No closes | Explanation |

### Japanese Format

| ID | Test Case | Context | Expected |
|----|-----------|---------|----------|
| TC-RP09 | Greeting | Weekly | 今週の進捗をご報告いたします |
| TC-RP10 | Problem | Has blockers | 謙譲語: 遅延しております |
| TC-RP11 | Request | Need action | ご確認いただけますでしょうか |

---

## Skill: bk-task

### Japanese Parsing

| ID | Test Case | Input | Expected |
|----|-----------|-------|----------|
| TC-TK01 | Full structure | 明日までにログイン画面を田中さんが作成。8時間 | All fields parsed |
| TC-TK02 | Implicit deadline | 今週中に | due = Friday |
| TC-TK03 | ASAP | 至急対応 | priority=High, due=today |
| TC-TK04 | Vague | できれば早めに | ⚠️ Unclear deadline |
| TC-TK05 | Multiple items | 5 bullets | 5 tasks |

### Source Types

| ID | Test Case | Source | Challenge |
|----|-----------|--------|-----------|
| TC-TK06 | Comment | Backlog comment | Extract actions |
| TC-TK07 | Email | Forwarded email | Parse quotes |
| TC-TK08 | Chat | Teams/Slack | Informal JP |
| TC-TK09 | Minutes | 議事録 | Extract 宿題 |
| TC-TK10 | Mixed | JA/EN code-switch | Handle both |

### Validation

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-TK11 | Ambiguous assignee | 2 Yamada in team | Ask user |
| TC-TK12 | No project | Task without context | Use default/ask |
| TC-TK13 | Duplicate | Similar exists | ⚠️ Confirm |

---

## Skill: bk-write

### Keigo Levels

| ID | Level | Context | Expected |
|----|-------|---------|----------|
| TC-WR01 | 丁寧語 | Internal email | 〜します |
| TC-WR02 | 謙譲語 | Customer report | 〜いたします |
| TC-WR03 | 尊敬語 | Customer action | ご確認いただき |
| TC-WR04 | Mixed | Customer CC | Appropriate switch |

### Templates

| ID | Template | Key Sections |
|----|----------|--------------|
| TC-WR05 | 週報 | 成果、課題、予定 |
| TC-WR06 | 議事録 | 参加者、議題、決定、宿題 |
| TC-WR07 | 障害報告 | 日時、影響、原因、対策 |
| TC-WR08 | 見積書 | 項目、工数、前提 |

### Consistency

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-WR09 | Same input 3x | Identical request | Consistent structure |
| TC-WR10 | Term consistency | "bug" 5 times | Same translation |

---

## Skill: bk-translate

### Glossary

| ID | Test Case | Scenario | Expected |
|----|-----------|----------|----------|
| TC-TR01 | Exact match | API→API | Unchanged |
| TC-TR02 | Case insensitive | "api"/"API" | Both work |
| TC-TR03 | Phrase | pull request→プルリクエスト | Full match |
| TC-TR04 | Project-specific | A: bug→不具合, B: bug→バグ | Correct glossary |
| TC-TR05 | Conflict | Same term, diff meanings | ⚠️ Ask context |

### Content Types

| ID | Test Case | Content | Expected |
|----|-----------|---------|----------|
| TC-TR06 | Code block | ```python``` | Keep code |
| TC-TR07 | URL | https://... | Unchanged |
| TC-TR08 | Table | MD table | Keep structure |
| TC-TR09 | Bullet list | - Items | Keep format |
| TC-TR10 | Mixed | Text + `code` | Selective |

### Quality

| ID | Test Case | Direction | Verification |
|----|-----------|-----------|--------------|
| TC-TR11 | JA→VI | Technical spec | Meaning OK |
| TC-TR12 | VI→JA | Email | Natural JP |
| TC-TR13 | Round-trip | JA→VI→JA | Meaning preserved |
| TC-TR14 | Formality | Formal→Formal | Tone preserved |

---

## Updated Architecture

```
brsekit/skills/
├── bk-status/          # P0: Progress, workload, scheduling
├── bk-risk/            # P0.5: Risk analysis (NEW)
│   ├── SKILL.md
│   ├── scripts/
│   │   ├── risk_aggregator.py
│   │   ├── dependency_parser.py
│   │   ├── risk_scorer.py
│   │   └── recommendation_engine.py
│   └── tests/
├── bk-report/          # P0
├── bk-task/            # P1
├── bk-write/           # P2
└── bk-translate/       # P2
```

---

## Next Steps

1. Update bk-status tests with scheduling logic
2. Create bk-risk skill structure
3. Implement TDD for each skill
4. Integration tests between skills

---

## Unresolved Questions

1. **Rate limit handling:** How to handle Backlog API rate limits during bulk operations?
2. **Offline mode:** Cache data for offline analysis?
3. **Multi-project:** How to aggregate across projects for bk-risk?
