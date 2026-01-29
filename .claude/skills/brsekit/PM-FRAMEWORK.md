# PM Framework - Capacity Planning & Risk Management

Reference guide for Project Management mindset when using BrseKit.

## Capacity Planning Model

### Why 6h/day instead of 8h?

```
┌─────────────────────────────────────────────────────┐
│ 8h/day (actual working hours)                       │
├─────────────────────────────────────────────────────┤
│ 6h productive work      │ 2h buffer                 │
│ (coding, tasks)         │ - Daily standup/meetings  │
│                         │ - Context switching       │
│                         │ - Code reviews            │
│                         │ - Slack/communication     │
│                         │ - Unexpected issues       │
│                         │ - Mental breaks           │
└─────────────────────────────────────────────────────┘
```

**Research backing:**
- **Maker's Schedule**: Developers need ~4h uninterrupted blocks to be productive
- **Hofstadter's Law**: Everything takes longer than expected, even when you account for this law
- **Context Switching Cost**: Each switch = 15-25 min recovery time

### Sprint Capacity Calculation

**2-week sprint:**
```
10 working days × 6h/day = 60h standard capacity
```

**Per-member capacity varies:**
```yaml
# In master.yaml
members:
  - name: "Senior Dev"
    capacity: 6  # Standard
  - name: "Junior Dev"
    capacity: 4  # More support needed, learning time
  - name: "Tech Lead"
    capacity: 4  # More meetings, code reviews
```

## Risk Levels by Capacity Utilization

### Member-Level Risk (Sprint capacity = 60h)

| Workload | % Capacity | Risk Level | Status | Action |
|----------|------------|------------|--------|--------|
| ≤54h | ≤90% | 🟢 **Low** | Healthy | Can support others |
| 54-60h | 90-100% | 🟡 **Medium** | Tight | Monitor closely |
| 60-72h | 100-120% | 🔴 **High** | Overloaded | Redistribute tasks |
| >72h | >120% | 🚨 **Critical** | Burnout risk | Immediate action |

### Why These Thresholds?

**≤90% (Low Risk)**
- Buffer exists for unexpected issues
- Member can help struggling teammates
- Room for "stretch goals" or learning

**90-100% (Medium Risk)**
- Technically achievable but no buffer
- Any delay cascades to deadline miss
- Need daily progress tracking

**>100% (High Risk)**
- Mathematically impossible at standard pace
- Requires overtime or scope reduction
- Indicator of planning issues

## Task-Level Risk Assessment

### Issue Types

| Type | Icon | Meaning | Required Action |
|------|------|---------|-----------------|
| **Overdue** | 🔴 | Past due date, not closed | Immediate escalation |
| **Needs Overtime** | ⚠️ | Required velocity > capacity | Monitor daily or redistribute |
| **Impossible Schedule** | 🔴 | start=due but remaining > 1 day | Extend due_date |
| **Needs Re-estimate** | 🔴 | Actual >= Estimated | Update estimate in Backlog |
| **On Track** | ✅ | Gap >= 0 | No action needed |

### Understanding "Needs Overtime" (At Risk)

**Definition:** Task requires working faster than daily capacity to meet deadline.

**Example:**
```
Remaining: 24h
Days until due: 3
Required velocity: 24h / 3 = 8h/day
Capacity: 6h/day
Gap: (3 × 6) - 24 = -6h

→ Need 8h/day but only have 6h → NEEDS OVERTIME
```

**Options:**
1. Work overtime (8h instead of 6h)
2. Extend due date
3. Reduce scope
4. Get help from teammates with surplus

## Interpreting the Report

### Executive Summary (Quick Look)

Look at these first:
1. **Tasks cần hành động ngay** - Any red flags?
2. **Member capacity overview** - Anyone overloaded?
3. **Recommendations** - Follow suggested actions

### Action Priority Matrix

| Priority | Condition | Action |
|----------|-----------|--------|
| **P0** | Task overdue | Escalate immediately |
| **P1** | Impossible schedule (start=due) | Reschedule today |
| **P2** | Member overloaded (>120%) | Redistribute tasks |
| **P3** | Needs re-estimate | Update Backlog |
| **P4** | Needs overtime | Monitor daily |
| **P5** | Medium risk (90-100%) | Weekly check |

### Daily Standup Questions

Use report to answer:
1. "Ai có task cần hỗ trợ?" → Check **Deficit** alerts
2. "Ai có thể support?" → Check **Surplus** members
3. "Task nào sẽ miss deadline?" → Check **Needs Overtime** list
4. "Estimate có chính xác không?" → Check **Overtime %**

## Best Practices

### Planning Phase

1. **Don't overcommit** - Aim for 80-90% capacity utilization
2. **Include buffer** - Unexpected issues WILL happen
3. **Front-load risky tasks** - Tackle uncertain tasks early
4. **Break down large tasks** - Max 16h per task (2-3 days)

### Execution Phase

1. **Update actuals daily** - Accuracy depends on fresh data
2. **Re-estimate when needed** - Don't hide scope creep
3. **Communicate early** - Flag issues before they become blockers
4. **Use Gantt as guide** - It's a PROPOSAL, not a rigid plan

### Retrospective Questions

1. Were estimates accurate? (Check average Overtime %)
2. Did we have buffer issues? (Check how many "Needs Overtime")
3. Who was overloaded? (Plan better distribution next sprint)
4. What caused re-estimates? (Address root causes)

## Common Scenarios

### Scenario 1: New Sprint Planning

```
Sprint capacity: 10 days × 6h × 2 members = 120h
Backlog: 130h of tasks

Decision:
- Option A: Cut 10h of tasks (recommended)
- Option B: Increase capacity (overtime)
- Option C: Accept risk (not recommended)
```

### Scenario 2: Mid-Sprint Crisis

```
Day 5 of 10: Member A has -20h gap (overloaded)
Member B has +15h gap (surplus)

Action:
1. Identify which of A's tasks can be moved to B
2. Reassign task in Backlog
3. Re-run bk-status to verify
```

### Scenario 3: Underestimated Task

```
Task BKT-5: Estimated 8h, Actual 20h, Still not done
Overtime%: 250%

Action:
1. Stop and re-estimate (likely needs 30-40h total)
2. Update Backlog estimate
3. Notify PM about timeline impact
4. Consider splitting into subtasks
```

## Related Documentation

- [GLOSSARY.md](./GLOSSARY.md) - Metrics definitions and formulas
- [master.yaml](./master.yaml) - Configuration reference

## Changelog

| Date | Change |
|------|--------|
| 2026-01-29 | Initial PM Framework documentation |
