# BrseKit Glossary & Conventions

Reference guide for BrSE using BrseKit tools.

## Report Metrics

### Gap (Effort Gap)

Difference between available hours and remaining hours for a task/member.

| Value | Meaning | Action |
|-------|---------|--------|
| **+Xh** | Surplus - có thừa X giờ effort | Member có thể hỗ trợ người khác |
| **-Xh** | Deficit - thiếu X giờ effort | Cần hỗ trợ hoặc reschedule |
| **0h** | On Track - vừa đủ capacity | Theo dõi, không cần action |

**Formula:**
```
Gap = Available Hours - Remaining Hours
Available Hours = Working Days × Hours Per Day
Remaining Hours = Estimated Hours - Actual Hours (min: 0)
```

### Working Days

Số ngày làm việc từ today đến due date, không tính weekend (Sat, Sun) và holidays.

**Example:**
- Today: 2026-01-28 (Tue)
- Due: 2026-02-03 (Tue)
- Working Days: 5 (28, 29, 30, 02, 03) - không tính 31/01 (Sat), 01/02 (Sun)

### Overtime Percent

Tỷ lệ thời gian thực tế so với estimate.

| Value | Status | Meaning |
|-------|--------|---------|
| **< 100%** | Normal | Đang trong estimate |
| **100-120%** | Warning | Gần hết estimate |
| **> 120%** | Alert | Underestimated - cần re-estimate |
| **> 200%** | Critical | Severely underestimated |

**Formula:**
```
Overtime % = (Actual Hours / Estimated Hours) × 100
```

### Remaining Hours

Số giờ còn lại để hoàn thành task.

**Formula:**
```
Remaining = max(0, Estimated - Actual)
```

**Note:** Remaining không bao giờ âm. Nếu Actual > Estimated thì Remaining = 0.

## Member Status

| Status | Icon | Condition | Action |
|--------|------|-----------|--------|
| **Surplus** | ✅ | Gap >= 1 day capacity | Có thể support members khác |
| **On Track** | 🟢 | Gap >= 0 | Đúng tiến độ |
| **At Risk** | ⚠️ | Gap between -1 day and 0 | Cần theo dõi sát |
| **Overloaded** | 🔴 | Gap < -1 day | Cần hỗ trợ ngay |

## Alerts

### Underestimate Alert

Xuất hiện khi Overtime % > 120%.

**Required Actions:**
1. Re-estimate task với estimate mới phản ánh thực tế
2. Reschedule nếu cần điều chỉnh due date
3. Notify stakeholders về sự thay đổi timeline

### Deficit Alert

Xuất hiện khi Gap < 0 cho một task.

**Required Actions:**
1. Xem xét reassign task cho member có surplus
2. Hoặc điều chỉnh due date
3. Hoặc tăng capacity (overtime, thêm người)

## Report Sections

### Summary
- Total Issues: Tổng số issues trong project
- Closed: Số issues đã đóng
- Progress: Tỷ lệ hoàn thành (Closed/Total × 100)

### Hours Progress
- Estimated Hours: Tổng giờ estimate
- Actual Hours: Tổng giờ đã làm
- Progress: Tỷ lệ hoàn thành theo giờ (Actual/Estimated × 100)

### BrSE Insights - Member Capacity
- Capacity Overview: Bảng tóm tắt capacity của từng member
- Per-member details: Chi tiết từng task của mỗi member
- Alerts: Các tasks có vấn đề cần xử lý
- Recommendations: Đề xuất hành động

## Configuration

### Hours Per Day

Số giờ làm việc hiệu quả mỗi ngày (không tính meetings, admin work).

| Value | Use Case |
|-------|----------|
| **6h** | Default - phổ biến nhất |
| **4h** | Part-time hoặc nhiều meetings |
| **8h** | Full capacity, ít meetings |

### Overloaded Threshold

Số issues mở tối đa trước khi member được coi là overloaded.

| Value | Use Case |
|-------|----------|
| **5** | Default |
| **3** | Strict, tasks phức tạp |
| **7** | Loose, tasks đơn giản |

## Abbreviations

| Abbr | Full | Vietnamese |
|------|------|------------|
| Est | Estimated Hours | Giờ ước tính |
| Act | Actual Hours | Giờ thực tế |
| Rem | Remaining Hours | Giờ còn lại |
| WD | Working Days | Ngày làm việc |
| OT% | Overtime Percent | Phần trăm vượt estimate |

## Examples

### Example 1: Healthy Task
```
Task: BKT-2
Estimated: 40h
Actual: 16h
Remaining: 24h
Due: 2026-02-03 (5 working days)
Available: 30h (5 × 6)
Gap: +6h (Surplus)
OT%: 40% (Normal)
```
**Insight:** Task đúng tiến độ, member còn thừa 6h có thể support.

### Example 2: Underestimated Task
```
Task: BKT-3
Estimated: 2h
Actual: 12h
Remaining: 0h
OT%: 600% (Critical!)
```
**Insight:** Task bị underestimate nghiêm trọng. Cần:
- Cập nhật estimate (ví dụ: 15h)
- Notify PM/stakeholders
- Xem xét nguyên nhân (requirement unclear, technical complexity)

### Example 3: Deficit Task
```
Task: BKT-6
Estimated: 20h
Actual: 0h
Remaining: 20h
Due: 2026-02-04 (6 working days)
Available: 36h (6 × 6)
Gap: +16h (Surplus per task)
```
**Note:** Task này có Gap dương nhưng nếu member có nhiều tasks khác, tổng Gap của member có thể âm.

## Related Documentation

- [PM-FRAMEWORK.md](./PM-FRAMEWORK.md) - Capacity planning mindset & best practices
- [master.yaml](./master.yaml) - Configuration reference

## Contact

For questions about BrseKit conventions, contact the project maintainer.
