# Project Status Report

**Date:** 2026-01-30
**Project:** brsekit-test
**Sprint End:** 2026-02-17

## ⚡ Action Required

Issues requiring immediate attention:

| Issue | Summary | Type | Detail | Assignee |
|-------|---------|------|--------|----------|
| BKT-3 | [BUG-INT] Nút đăng nhập không  | 🔴 Overdue | 1 days overdue | Unassigned |
| BKT-7 | [ISSUE] Performance degradatio | 🔴 Impossible schedule | Need 16h but only 1 day (start=due) | bibonihongo |
| BKT-1 | [TASK] Triển khai chức năng ph | ⚠️ Needs overtime | Need 12.0h/day, capacity 6h/day | Unassigned |
| BKT-2 | [SUBTASK] Thiết kế UI phòng ch | ⚠️ Needs overtime | Need 8.0h/day, capacity 6h/day | Unassigned |
| BKT-2 | [SUBTASK] Thiết kế UI phòng ch | 📅 Will miss deadline | Due 02/03 → Complete 02/04 | bibonihongo |
| BKT-5 | [BUG-PROD] API timeout khi loa | 📅 Will miss deadline | Due 02/06 → Complete 02/09 | bibonihongo |
| BKT-3 | [BUG-INT] Nút đăng nhập không  | 📅 Will miss deadline | Due 01/29 → Complete 01/30 | Nguyen Hoang Duong |
| BKT-1 | [TASK] Triển khai chức năng ph | 📅 Will miss deadline | Due 01/30 → Complete 02/02 | Nguyen Hoang Duong |
| BKT-4 | [BUG-UAT] Hiển thị sai số tiền | 📅 Will miss deadline | Due 02/03 → Complete 02/04 | Nguyen Hoang Duong |
| BKT-6 | [RISK] Dependency outdated có  | 📅 Will miss deadline | Due 02/04 → Complete 02/06 | Nguyen Hoang Duong |

## Summary

| Metric | Value |
|--------|-------|
| Estimated Hours | 172.0 |
| Actual Hours | 68.0 |
| Progress | 39.5% |

### By Status

| Status | Count |
|--------|-------|
| Open | 4 |
| In Progress | 5 |
## BrSE Insights - Member Capacity

**Analysis Date:** 2026-01-30 | **Capacity:** 6h/day | **Sprint End:** 2026-02-17

**Note:** Gap = Available Capacity - Workload. Positive = surplus, Negative = deficit (needs reschedule).

### Capacity Overview

| Member | Status | Tasks | Workload | Capacity | Gap | Velocity |
|--------|--------|-------|----------|----------|-----|----------|
| bibonihongo | 🟢 On Track | 3 | 56h | 60h | +4h | 5.6h/day |
| Nguyen Hoang Duong | ✅ Surplus | 5 | 48h | 80h | +32h | 4.8h/day |

### 🟢 bibonihongo

- **Tasks:** 3 open
- **Workload:** 56h remaining
- **Capacity:** 60h (10 days × 6h/day)
- **Gap:** +4h (can support others)
- **Due Range:** 2026-02-03 → 2026-02-06

**Gap:** Available hours until due_date minus remaining hours. Positive = buffer time, Negative = not enough time.

| Issue | Summary | Est | Act | Due | Gap | Alert |
|-------|---------|-----|-----|-----|-----|-------|
| BKT-2 | [SUBTASK] Thiết kế UI phò | 40h | 16h | 02/03 | -6h | 🔴 Deficit |
| BKT-5 | [BUG-PROD] API timeout kh | 16h | 0h | 02/06 | +14h | ✅ |
| BKT-7 | [ISSUE] Performance degra | 48h | 32h | 02/03 | -10h | ⚠️ RESCHED |

### ✅ Nguyen Hoang Duong

- **Tasks:** 5 open
- **Workload:** 48h remaining
- **Capacity:** 80h (10 days × 8h/day)
- **Gap:** +32h (can support others)
- **Due Range:** 2026-01-29 → 2026-02-06

**Gap:** Available hours until due_date minus remaining hours. Positive = buffer time, Negative = not enough time.

| Issue | Summary | Est | Act | Due | Gap | Alert |
|-------|---------|-----|-----|-----|-----|-------|
| BKT-3 | [BUG-INT] Nút đăng nhập k | 16h | 12h | 01/29 | -4h | 🔴 Deficit |
| BKT-1 | [TASK] Triển khai chức nă | 16h | 4h | 01/30 | -4h | 🔴 Deficit |
| BKT-8 | [FEEDBACK] Yêu cầu dark m | 8h | 4h | 02/06 | +44h | ✅ |
| BKT-4 | [BUG-UAT] Hiển thị sai số | 8h | 0h | 02/03 | +8h | ✅ |
| BKT-6 | [RISK] Dependency outdate | 20h | 0h | 02/04 | +4h | ✅ |

### ⚠️ Action Required - Tasks Need Rescheduling

These tasks have start_date = due_date but remaining work exceeds daily capacity.
**Impossible to complete in 1 day.** Please extend due_date or reduce scope.

| Issue | Summary | Start | Due | Remaining | Capacity | Assignee |
|-------|---------|-------|-----|-----------|----------|----------|
| BKT-7 | [ISSUE] Performance  | 02/03 | 02/03 | **16h** | 6h/day | bibonihongo |

### 💡 Recommendations

- **⚠️ URGENT:** 1 tasks have impossible schedule (start=due, extend due_date)
- **Available support:** Nguyen Hoang Duong has +32h surplus capacity

## Daily Schedule (Gantt) - PROPOSED

⚠️ **Note:** Schedule below is a **PROPOSAL** based on actual capacity. Tasks with infeasible due_dates are auto-extended.

### bibonihongo (6h/day)

| Task | 30F | 02M | 03T | 04W | 05T | 06F | 09M | 10T | 12T | 13F |
|------|----|----|----|----|----|----|----|----|----|----|
| **📅 BKT-2 (24h)** | 6 | 6 | 6 | 6⚠️ |  |  |  |  |  |  |
| **📅 BKT-5 (16h)** |  |  |  |  | 6 | 6 | 4⚠️ |  |  |  |
| **📅 BKT-7 (16h)** |  |  |  |  |  |  | 2 | 6 | 6 | 2⚠️ |
|------|----|----|----|----|----|----|----|----|----|----|
| **Daily Total** | 6h | 6h | 6h | 6h | 6h | 6h | 6h | 6h | 6h | 2h |


**Legend:** ✅ = on-time | ⚠️ = late (past due) | ↑Xh = need X more hours | **📅 BOLD** = proposed schedule

### Nguyen Hoang Duong (8h/day)

| Task | 30F | 02M | 03T | 04W | 05T | 06F | 09M | 10T | 12T | 13F |
|------|----|----|----|----|----|----|----|----|----|----|
| **📅 BKT-3 (4h)** | 4⚠️ |  |  |  |  |  |  |  |  |  |
| **📅 BKT-1 (12h)** | 4 | 8⚠️ |  |  |  |  |  |  |  |  |
| BKT-8 (4h) |  |  | 4✅ |  |  |  |  |  |  |  |
| **📅 BKT-4 (8h)** |  |  | 4 | 4⚠️ |  |  |  |  |  |  |
| **📅 BKT-6 (20h)** |  |  |  | 4 | 8 | 8⚠️ |  |  |  |  |
|------|----|----|----|----|----|----|----|----|----|----|
| **Daily Total** | 8h | 8h | 8h | 8h | 8h | 8h |  |  |  |  |


**Legend:** ✅ = on-time | ⚠️ = late (past due) | ↑Xh = need X more hours | **📅 BOLD** = proposed schedule
