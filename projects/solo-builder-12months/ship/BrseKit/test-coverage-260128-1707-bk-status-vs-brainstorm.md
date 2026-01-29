# bk-status Test Coverage Analysis

**Date:** 2026-01-28
**Reference:** [Brainstorm Report](./brainstorm-260128-1658-brsekit-test-cases.md)
**Status:** ✅ Tests Updated

---

## Summary

| Category | Brainstorm | Implemented | Coverage |
|----------|------------|-------------|----------|
| Progress Calculation | 5 | 5 | 100% ✅ |
| Deadline Risk | 5 | 4 | 80% |
| Member Workload | 5 | 4 | 80% |
| Task Scheduling | 5 | 0 | 0% (bk-risk) |
| Dependencies | 3 | 0 | 0% (bk-risk) |
| **Total** | **23** | **13** | **57%** |

**Test Suite Status:** 61 tests passing ✅

---

## Detailed Coverage

### Progress Calculation (TC-S01 to TC-S05)

| ID | Test Case | Status | Notes |
|----|-----------|--------|-------|
| TC-S01 | Normal progress (est=16h, act=4h → 25%) | ✅ Covered | `test_tc_s01_normal_progress` |
| TC-S02 | Overtime (est=8h, act=12h → 150%) | ✅ Covered | `test_tc_s02_overtime_progress` |
| TC-S03 | No estimate (est=null → returns None) | ✅ Covered | `test_tc_s03_no_estimate_returns_none` |
| TC-S04 | No actual (est=16h, act=0h → 0%) | ✅ Covered | `test_tc_s04_no_actual_zero_progress` |
| TC-S05 | Closed task → counts as done | ✅ Covered | `test_tc_s05_closed_task_counts_as_done` |

### Deadline Risk (TC-S06 to TC-S10)

| ID | Test Case | Status | Notes |
|----|-----------|--------|-------|
| TC-S06 | On track (remain=12h, 3d, 6h/d cap) | ✅ Covered | `test_tc_s06_on_track_scenario` |
| TC-S07 | At risk (velocity > capacity) | ✅ Covered | `test_tc_s07_at_risk_scenario` |
| TC-S08 | Late (past due, not closed) | ✅ Covered | `test_tc_s08_late_scenario` |
| TC-S09 | Weekend skip (Fri→Mon = 1 day) | ❌ Missing | Uses calendar days, not workdays |
| TC-S10 | Overdue X days calculation | ✅ Covered | `test_tc_s10_overdue_days_calculation` |

### Member Workload (TC-S11 to TC-S15)

| ID | Test Case | Status | Notes |
|----|-----------|--------|-------|
| TC-S11 | Normal load (hours %) | ✅ Covered | `test_member_progress_by_hours` |
| TC-S12 | Threshold hit (overloaded) | ✅ Covered | `test_tc_s12_threshold_overloaded` |
| TC-S13 | Severe overload (%) | ⚠️ Partial | Hours progress shows %, no severity flag |
| TC-S14 | Part-time effort (0.5 → 3h/day) | ❌ Missing | No effort/capacity model |
| TC-S15 | Multiple tasks aggregate | ✅ Covered | `test_tc_s15_multiple_tasks_aggregate` |

### Task Scheduling & Overlap (TC-S20 to TC-S24)

| ID | Test Case | Status | Notes |
|----|-----------|--------|-------|
| TC-S20 | Sequential fit (EDF order) | ❌ Not Impl | No scheduling logic |
| TC-S21 | Overlap conflict detection | ❌ Not Impl | No overlap detection |
| TC-S22 | Scheduling suggestions | ❌ Not Impl | No recommendations |
| TC-S23 | Buffer analysis | ❌ Not Impl | No buffer calc |
| TC-S24 | No slack warning | ❌ Not Impl | No slack detection |

### Dependencies (TC-S16 to TC-S18)

| ID | Test Case | Status | Notes |
|----|-----------|--------|-------|
| TC-S16 | Blocked task detection | ❌ Not Impl | Planned for bk-risk |
| TC-S17 | Unblocked detection | ❌ Not Impl | Planned for bk-risk |
| TC-S18 | Chain dependencies | ❌ Not Impl | Planned for bk-risk |

---

## What's Actually Tested (61 tests)

### test_models.py (13 tests)
- User.from_dict parsing
- Status.from_dict parsing
- Project.from_dict parsing
- Issue.from_dict (with/without assignee, due date, hours)
- RiskLevel enum values

### test_status_analyzer.py (33 tests)
- **TestLateTasks** (4): Detection, exclusion, days_overdue
- **TestWorkload** (3): Count per assignee, overloaded, unassigned
- **TestProjectSummary** (3): Status counts, progress %, empty project
- **TestMarkdownReport** (1): Report generation structure
- **TestHoursProgress** (2): Hours-based progress, null hours
- **TestRiskDetection** (5): ON_TRACK, AT_RISK, LATE, closed, no due
- **TestGetAtRiskTasks** (2): Filtering, sorting by velocity
- **TestProgressCalculation** (5): TC-S01 to TC-S05 from brainstorm ✅
- **TestDeadlineRisk** (4): TC-S06 to TC-S10 from brainstorm ✅
- **TestMemberWorkloadAdvanced** (2): TC-S12, TC-S15 from brainstorm ✅
- **TestMemberProgress** (2): Hours-based member progress ✅

### test_backlog_client.py (10 tests)
- Client initialization, validation
- Rate limiting
- API method mocking (project, statuses, users, issues)

### test_main.py (5 tests)
- Environment loading
- Output path generation

---

## Gap Analysis

### High Priority (MVP Requirements)

1. **Weekend Skip Logic (TC-S09)**
   - Current: Uses calendar days
   - Required: Skip Sat/Sun in days_remaining calculation
   - Impact: Risk assessment accuracy

2. **Overtime Warning (TC-S02)**
   - Current: Returns > 100% silently
   - Required: Flag with ⚠️ warning
   - Impact: Report visibility

### Medium Priority (Phase 2)

3. **Hours-Based Workload (TC-S11, TC-S13)**
   - Current: Count-based only
   - Required: `assigned_hours / (effort × capacity × days)`
   - Dependency: Needs effort/capacity model

4. **Part-Time Effort (TC-S14)**
   - Current: No effort tracking
   - Required: Member effort field (0.5 = half-time)
   - Impact: Accurate capacity calculation

### Deferred (bk-risk Skill)

5. **Dependencies (TC-S16-18)**
   - Planned for separate bk-risk skill
   - Uses custom field or text parsing

6. **Scheduling & Overlap (TC-S20-24)**
   - Complex scheduling logic
   - Requires EDF algorithm
   - May integrate with bk-risk

---

## Recommendations

### Immediate Actions

1. Add test for **TC-S02**: Overtime detection with warning
2. Add test for **TC-S09**: Weekend skip (requires implementation)
3. Ensure **TC-S03** returns warning, not just None

### Implementation Order

```
Phase 1: Core improvements
├── Add workdays calculation (skip weekends)
├── Add overtime flag (> 100% warning)
└── Improve no-estimate handling

Phase 2: Capacity model
├── Add member effort field
├── Hours-based workload calculation
└── Capacity utilization %

Phase 3: bk-risk integration
├── Dependencies
├── Scheduling
└── Overlap detection
```

---

## Unresolved Questions

1. **Holiday handling**: Skip holidays in addition to weekends?
2. **Effort source**: Where to store member effort (Backlog custom field? local config?)
3. **Overlap threshold**: What % overlap triggers warning?
