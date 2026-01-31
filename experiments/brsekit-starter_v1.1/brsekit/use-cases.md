# BrseKit Use Cases

40 use cases cho BrSE, ưu tiên theo pain points thực tế.

**Legend:** ✅ Sẵn sàng | ⚠️ Cần upgrade | 🔴 Cần develop

---

## PRIORITY 1: Tiếng Nhật chuẩn mực (`/bk-write`)

| # | Use Case | Command | Status |
|---|----------|---------|--------|
| UC01 | Email báo delay (khách khó tính) | `/bk-write email --tone careful --explain "delay 2 ngày"` | ⚠️ |
| UC02 | Email xin lỗi chuyên nghiệp | `/bk-write email --tone apologetic --explain "miss deadline"` | ⚠️ |
| UC03 | Status update hàng ngày | `/bk-write daily-report` | 🔴 |
| UC04 | Issue description tiếng Nhật | `/bk-write issue "login timeout bug"` | ✅ |
| UC05 | Email escalation | `/bk-write email --tone urgent "critical bug"` | ✅ |
| UC06 | Email hỏi ý kiến khách | `/bk-write email --tone humble "xin confirm spec"` | ⚠️ |

**Test:**
- [ ] UC01 - [ ] UC02 - [ ] UC03 - [ ] UC04 - [ ] UC05 - [ ] UC06

---

## PRIORITY 2: BA Skill + Spec (`/bk-spec`)

| # | Use Case | Command | Status |
|---|----------|---------|--------|
| UC07 | Phân tích requirement | `/bk-spec analyze requirements.md` | ✅ |
| UC08 | Output Excel spec | `/bk-spec analyze req.md --output spec.xlsx` | 🔴 |
| UC09 | Tạo test cases | `/bk-spec test requirements.md --type all` | ✅ |
| UC10 | Tìm gaps trong spec | `/bk-spec analyze spec.md --gaps` | ✅ |
| UC11 | Q&A list từ meeting notes | `/bk-spec analyze meeting.txt --type hearing-qa` | 🔴 |
| UC12 | Checklist trước khi code | `/bk-spec checklist --type pre-code` | 🔴 |
| UC13 | Checklist trước deploy | `/bk-spec checklist --type pre-deploy` | 🔴 |

**Test:**
- [ ] UC07 - [ ] UC08 - [ ] UC09 - [ ] UC10 - [ ] UC11 - [ ] UC12 - [ ] UC13

---

## PRIORITY 3: Morning Routine (`/bk-morning`)

| # | Use Case | Command | Status |
|---|----------|---------|--------|
| UC14 | Morning brief tổng hợp | `/bk-morning` | ✅ |
| UC15 | Unread comments từ 18:00 hôm trước | `/bk-morning --since 18:00` | ⚠️ |
| UC16 | Check blockers | `/bk-morning --blockers` | ⚠️ |

**Test:**
- [ ] UC14 - [ ] UC15 - [ ] UC16

---

## PRIORITY 4: Project Tracking (`/bk-track`)

| # | Use Case | Command | Status |
|---|----------|---------|--------|
| UC17 | Check tiến độ sprint | `/bk-track status --threshold 3` | ✅ |
| UC18 | Tạo báo cáo tuần PPTX | `/bk-track report --format pptx` | ✅ |
| UC19 | Báo cáo tiếng Nhật | `/bk-track status --lang ja` | ✅ |
| UC20 | Tìm task bị delay | `/bk-track status --threshold 0` | ✅ |
| UC21 | Check member actual time | `/bk-track status --members` | 🔴 |
| UC22 | Summary cho khách | `/bk-track summary --lang ja` | ✅ |

**Test:**
- [ ] UC17 - [ ] UC18 - [ ] UC19 - [ ] UC20 - [ ] UC21 - [ ] UC22

---

## PRIORITY 5: Memory & Knowledge (`/bk-recall`)

| # | Use Case | Command | Status |
|---|----------|---------|--------|
| UC23 | Search context cũ | `/bk-recall search "payment integration"` | ✅ |
| UC24 | Sync Backlog comments | `/bk-recall sync` | ✅ |
| UC25 | Unread summary | `/bk-recall unread --since "18:00"` | 🔴 |
| UC26 | Tìm decision đã thống nhất | `/bk-recall search "決定事項"` | ✅ |
| UC27 | Summary theo topic | `/bk-recall summary "authentication"` | ✅ |
| UC28 | FAQ từ knowledge base | `/bk-recall faq "API rate limit là bao nhiêu?"` | 🔴 |

**Test:**
- [ ] UC23 - [ ] UC24 - [ ] UC25 - [ ] UC26 - [ ] UC27 - [ ] UC28

---

## PRIORITY 6: Capture Tasks (`/bk-capture`)

| # | Use Case | Command | Status |
|---|----------|---------|--------|
| UC29 | Parse task từ email JA | `/bk-capture task "明日までにログイン機能を..."` | ✅ |
| UC30 | Tạo meeting minutes | `/bk-capture meeting <transcript>` | ✅ |
| UC31 | Parse task từ Slack | `/bk-capture task "urgent: fix payment bug"` | ✅ |
| UC32 | Auto-create Backlog ticket | `/bk-capture task "..." --create` | 🔴 |
| UC33 | Parse deadline implicit | `/bk-capture task "来週中にテスト完了"` | ✅ |

**Test:**
- [ ] UC29 - [ ] UC30 - [ ] UC31 - [ ] UC32 - [ ] UC33

---

## PRIORITY 7: Translation (`/bk-convert`)

| # | Use Case | Command | Status |
|---|----------|---------|--------|
| UC34 | Dịch JA→VI | `/bk-convert "テストを実施しました"` | ✅ |
| UC35 | Dịch VI→JA | `/bk-convert "Đăng nhập cần xác thực 2 bước" --to ja` | ✅ |
| UC36 | Dịch với glossary | `/bk-convert "単体テストを実行する"` | ✅ |
| UC37 | Dịch technical term | `/bk-convert "結合テスト環境"` | ✅ |
| UC38 | Dịch email dài | `/bk-convert <paste email>` | ✅ |

**Test:**
- [ ] UC34 - [ ] UC35 - [ ] UC36 - [ ] UC37 - [ ] UC38

---

## FUTURE: Knowledge Base & FAQ

| # | Use Case | Command | Status |
|---|----------|---------|--------|
| UC39 | Add knowledge entry | `/bk-knowledge add "API limit: 100 req/min"` | 🔴 |
| UC40 | Query knowledge (RAG) | `/bk-knowledge query "rate limit của system?"` | 🔴 |

**Test:**
- [ ] UC39 - [ ] UC40

---

## Summary

| Priority | Category | Total | ✅ | ⚠️ | 🔴 |
|----------|----------|-------|----|----|-----|
| 1 | bk-write | 6 | 2 | 3 | 1 |
| 2 | bk-spec | 7 | 3 | 0 | 4 |
| 3 | bk-morning | 3 | 1 | 2 | 0 |
| 4 | bk-track | 6 | 5 | 0 | 1 |
| 5 | bk-recall | 6 | 4 | 0 | 2 |
| 6 | bk-capture | 5 | 4 | 0 | 1 |
| 7 | bk-convert | 5 | 5 | 0 | 0 |
| Future | bk-knowledge | 2 | 0 | 0 | 2 |
| **Total** | | **40** | **24** | **5** | **11** |

---

## Architecture Notes

### Knowledge vs Memory
```
Knowledge (Human-editable)     Memory (Auto-synced)
├─ glossary.json              ├─ backlog/ (comments, issues)
├─ faq.md                     ├─ slack/ (messages)
├─ rules.md                   ├─ email/ (threads)
└─ specs/                     └─ meetings/ (minutes)
```

### Unread Detection
- So sánh với `last_sync_time` trong metadata.db
- Hoặc so sánh với timing cụ thể (default: 18:00 hôm trước)

### bk-write --explain
- Giải thích tại sao chọn từ này
- Alternatives và khi nào nên dùng
- Keigo level explanation

---

## Test Notes

Ghi chú khi test:
-
