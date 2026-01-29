# Solo Builder 12-Month Journey

Hành trình 12 tháng trở thành indie maker với AI Mentor + PM support.

## Quick Start

```bash
# Từ brse-workspace, gõ:
/sb                    # Dashboard - xem status hiện tại
/sb check-in           # Weekly review
/sb learn <topic>      # Học concept (Socratic method)
/sb build              # Bắt đầu/tiếp tục build
/sb ideas              # Quản lý product ideas
```

## Cách Sử Dụng

### Hàng Ngày
1. Mở Claude Code trong `brse-workspace`
2. Gõ `/sb` để xem dashboard
3. Build theo plan, khi gặp concept lạ → gõ `/sb learn <concept>`

### Hàng Tuần
1. Cuối tuần gõ `/sb check-in`
2. Review tasks completed
3. Update hours & energy
4. Plan next week

### Khi Có Ý Tưởng Mới
```
/sb ideas add          # Thêm idea
/sb ideas validate     # Score idea theo framework
```

## Cấu Trúc Thư Mục

```
solo-builder-12months/
├── README.md              ← Bạn đang đây
├── docs/
│   ├── plan.md            ← 12-month detailed plan
│   ├── ideas.md           ← Product ideas backlog
│   └── resources.md       ← Learning resources
├── progress/
│   ├── status.yaml        ← Metrics & current position
│   ├── learner-profile.md ← Learning tracking
│   └── weekly/            ← Weekly check-ins
├── mentor-notes/          ← AI Mentor session notes
└── ship/                  ← Products you build (coming soon)
```

## Targets

| Metric | Target |
|--------|--------|
| Duration | 12 months (48 weeks) |
| Weekly Hours | 20h |
| Products | 5-8 |
| Revenue | $500+ MRR |

## Phases

1. **Month 1-2**: Build First (ship something live)
2. **Month 3-4**: Backend + Database
3. **Month 5-6**: AI Integration
4. **Month 7-8**: Growth
5. **Month 9-10**: Advanced + Hedge
6. **Month 11-12**: Decision Time

## AI Mentor Modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **PM** | `/sb`, `/sb check-in` | Track progress, accountability |
| **Mentor** | `/sb learn`, "tại sao..." | Socratic teaching |
| **Build** | `/sb build` | Support while coding |

## Tips

- **Không cần cd** vào thư mục này, dùng `/sb` từ brse-workspace
- **Mọi skill khác** vẫn dùng được (git, cook, plan, etc.)
- **AI writes, you read** - Focus on understanding, not typing
- **Ship > Perfect** - Done is better than perfect

---

*Started: 2026-01-24*
