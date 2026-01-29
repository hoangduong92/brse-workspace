# BrseKit Operation Vision - Brainstorm Summary

**Date:** 2026-01-28
**Context:** Defining operational standards for BrseKit as a standard AI kit

---

## Problem Statement

BrseKit cần có Operation Vision rõ ràng để:

1. Các dự án có thể tune theo chuẩn chung
2. Đảm bảo security và quality consistency
3. Track performance và optimize

---

## Operation Vision (3 Layers)

### Layer 1: Integration Layer

| Priority | Integration                    | Status       |
| -------- | ------------------------------ | ------------ |
| **MVP**  | Nulab Backlog                  | Required     |
| Future   | Slack                          | Nice-to-have |
| Future   | Google Workspace (Chat, Drive) | Nice-to-have |

**MVP Focus:** Chỉ Backlog, thêm Slack/GWS sau khi validate core skills.

---

### Layer 2: Security Gate

| Action              | Gate Level | Implementation             |
| ------------------- | ---------- | -------------------------- |
| **Delete tickets**  | BLOCKED    | PreToolUse hook            |
| **Update status**   | APPROVAL   | User confirmation required |
| **Update assignee** | APPROVAL   | User confirmation required |
| Create ticket       | ALLOWED    | No gate                    |
| Add comment         | ALLOWED    | No gate                    |
| Read operations     | ALLOWED    | No gate                    |

**Implementation:** Claude hooks (PreToolUse) để intercept và gate actions.

---

### Layer 3: Evaluation Gate

#### Global Standards

| Metric              | Target | Description                           |
| ------------------- | ------ | ------------------------------------- |
| **Max agent turns** | 5      | Skill phải hoàn thành trong 5 turns   |
| Token efficiency    | TBD    | Track token cost per skill invocation |

#### Per-Skill Metrics

| Skill          | Metrics        | Target                        |
| -------------- | -------------- | ----------------------------- |
| `bk-status`    | Execution time | < 30s for 100 issues          |
| `bk-status`    | Accuracy       | 100% late task detection      |
| `bk-report`    | Time           | < 60s for weekly report       |
| `bk-task`      | Turns          | ≤ 3 turns to create task      |
| `bk-translate` | Quality        | Preserve 100% technical terms |
| `bk-write`     | Consistency    | Same template output          |

---

## Architecture Impact

```
BrseKit/
├── CLAUDE.md                 # Kit overview + operation vision
├── OPERATION.md              # Detailed standards (future)
├── hooks/
│   ├── security-gate.py      # Block deletes, gate critical updates
│   └── eval-tracker.py       # Track turns, time, metrics
├── skills/
│   ├── bk-status/
│   │   └── eval-config.yaml  # Skill-specific metrics
│   └── ...
└── evals/
    └── benchmarks/           # Automated evaluation tests
```

---

## Confirmed Decisions

| Decision            | Choice                   | Rationale                    |
| ------------------- | ------------------------ | ---------------------------- |
| Integration MVP     | Backlog only             | Focus, validate core first   |
| Security Gate scope | Delete + critical fields | Balance security vs UX       |
| Global turn limit   | 5 turns                  | Reasonable for complex tasks |
| bk-status metrics   | Time + Accuracy          | Core quality indicators      |

---

## Action Items

- [ ] Add Operation Vision section to parent BrseKit MVP plan
- [ ] Implement security-gate hook (block delete, gate critical)
- [ ] Define eval-config.yaml schema for per-skill metrics
- [ ] Create baseline benchmarks after bk-status implementation

---

## Unresolved Questions

1. Token cost tracking - how to implement? (Claude API usage?)
2. Automated eval pipeline - CI/CD integration?
3. Slack/GWS integration timeline - post-MVP priority order?

## Onboarding guidelines

1. Cách brse sử dụng brsekit
2. Bước đầu tiên brsekit sẽ quét các skill trong bộ kit, và yêu cầu user cung cấp các thông tin cần thiết, ví dụ project ID, nublab api KEY, ..
3. Hỏi user về việc quy tắc vận hành backlog, slack, google workspace. Ví dụ custom field trong backlog sẽ có vai trò gì trong việc quản lý dự án. Từ đó sẽ udpate skill hiện có liên quan đến backlog.
   Cách tiếp cận với user là :

- Với skill hiện tại thì output sẽ là
- Nếu bổ sung thêm các custom field thì output sẽ là..
  Để từ đó user quyết định có update bộ brsekit hay không.
