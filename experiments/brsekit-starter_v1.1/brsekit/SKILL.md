---
name: brsekit
description: BrseKit help and documentation. Use when asking about BrseKit features, installation, or usage.
argument-hint: "[help|install|skills|glossary]"
user-invocable: true
---

# BrseKit - BrSE Toolkit

Bộ công cụ AI hỗ trợ Bridge System Engineer trong công việc hàng ngày.

## Quick Help

```bash
/brsekit help      # Xem hướng dẫn đầy đủ
/brsekit install   # Hướng dẫn cài đặt
/brsekit skills    # Danh sách skills
/brsekit glossary  # Xem glossary IT terms
```

## Available Skills

| Skill | Mô tả | Command |
|-------|-------|---------|
| **bk-track** | Project tracking, báo cáo tuần | `/bk-track status\|report\|summary` |
| **bk-capture** | Parse tasks, meeting notes | `/bk-capture task\|meeting\|email` |
| **bk-spec** | Requirement analysis, test docs | `/bk-spec analyze\|test\|feature` |
| **bk-recall** | Memory layer, search context | `/bk-recall sync\|search\|summary` |
| **bk-convert** | JA↔VI translation | `/bk-convert <text>` |

## Quick Examples

```bash
# Kiểm tra tiến độ dự án
/bk-track status --threshold 3 --lang ja

# Tạo báo cáo tuần PowerPoint
/bk-track report --format pptx --output weekly.pptx

# Parse task từ email
/bk-capture task "明日までにログイン機能を実装"

# Tạo test documents
/bk-spec test requirements.md --type all

# Tìm kiếm context
/bk-recall search "payment integration"

# Dịch JA→VI
/bk-convert "テストを実施しました"
```

## Documentation

- [Onboarding Guide](onboarding-guide.md) - Hướng dẫn cài đặt cho BrSE mới
- [Glossary](GLOSSARY.md) - IT terms JA↔VI
- [PM Framework](PM-FRAMEWORK.md) - Project management framework

## Environment Setup

Required `.env` variables:
```
BACKLOG_SPACE_URL=https://xxx.backlog.jp
BACKLOG_API_KEY=your-api-key
BACKLOG_PROJECT_KEY=PROJECT
GOOGLE_API_KEY=your-gemini-key  # for semantic search
```

## Support

- Issues: Tạo issue trong repository
- Slack: #brsekit-support
