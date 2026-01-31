# BrseKit Onboarding Guide

Hướng dẫn cài đặt và sử dụng BrseKit cho BrSE mới.

## BrseKit là gì?

BrseKit là bộ công cụ AI hỗ trợ BrSE (Bridge System Engineer) trong công việc hàng ngày:
- **Tracking**: Theo dõi tiến độ dự án, tạo báo cáo tuần
- **Capture**: Parse tasks từ email, meeting notes
- **Spec**: Phân tích yêu cầu, tạo test documents
- **Recall**: Tìm kiếm context từ email, Backlog
- **Convert**: Dịch JA↔VI với glossary IT

---

## Yêu cầu hệ thống

- **Claude Code** (CLI hoặc VS Code extension)
- **Python 3.11+**
- **Git**
- **Backlog account** (để sync issues)
- **Google API key** (cho Gemini embeddings - optional)

---

## Cài đặt

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd brse-workspace
```

### Bước 2: Cài đặt Python dependencies

```bash
cd .claude/skills
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### Bước 3: Cấu hình environment variables

Tạo file `.env` tại root của workspace:

```bash
# Backlog Configuration (bắt buộc)
BACKLOG_SPACE_URL=https://your-space.backlog.jp
BACKLOG_API_KEY=your-backlog-api-key
BACKLOG_PROJECT_KEY=YOUR_PROJECT

# Google Gemini API (cho bk-recall semantic search)
GOOGLE_API_KEY=your-gemini-api-key

# Optional: Gmail sync
GMAIL_CREDENTIALS_PATH=~/.brsekit/gmail_credentials.json
```

### Bước 4: Verify cài đặt

Mở Claude Code và chạy:

```
/bk-track status
```

Nếu thấy output về project health → cài đặt thành công!

---

## Skills Overview

### `/bk-track` - Project Tracking

Theo dõi tiến độ dự án và tạo báo cáo.

```bash
# Kiểm tra health của project
/bk-track status

# Tạo báo cáo tuần (Markdown)
/bk-track report

# Tạo báo cáo tuần (PowerPoint)
/bk-track report --format pptx --output weekly-report.pptx

# Quick summary
/bk-track summary
```

**Options:**
| Option | Mô tả | Mặc định |
|--------|-------|----------|
| `--threshold N` | Số ngày để đánh dấu task "late" | 3 |
| `--lang en\|ja\|vi` | Ngôn ngữ output | en |
| `--format md\|pptx` | Format báo cáo | md |
| `--output FILE` | File output (bắt buộc cho pptx) | - |
| `--period N` | Số ngày cho báo cáo | 7 |

---

### `/bk-capture` - Task & Meeting Parser

Parse text thành tasks hoặc meeting minutes.

```bash
# Parse task từ text
/bk-capture task "明日までにログイン機能を実装してください"

# Parse task từ file
/bk-capture task email.txt

# Parse meeting transcript
/bk-capture meeting transcript.txt
```

**Features:**
- Auto-detect ngôn ngữ (JA/EN/VI)
- Detect deadline (明日, 今週中, by Friday)
- Detect priority (至急, ASAP, 優先度高)
- Auto-classify (Task/Issue/Risk/Question)

---

### `/bk-spec` - Requirement Analysis & Test Docs

Phân tích yêu cầu và tạo test documents.

```bash
# Phân tích requirements
/bk-spec analyze requirements.md

# Tạo test documents
/bk-spec test requirements.md --type all

# Tạo chỉ viewpoint table
/bk-spec test requirements.md --type viewpoint

# Tạo chỉ test cases
/bk-spec test requirements.md --type cases
```

**Output formats:**
- テスト計画書 (Test Plan)
- 観点表 (Viewpoint Table)
- テストケース (Test Cases)

---

### `/bk-recall` - Memory & Search

Sync và tìm kiếm context từ nhiều nguồn.

```bash
# Sync data
/bk-recall sync              # Sync tất cả
/bk-recall sync backlog      # Chỉ Backlog
/bk-recall sync email        # Chỉ email

# Tìm kiếm
/bk-recall search "login bug"
/bk-recall search "要件変更" --source email

# Tóm tắt context
/bk-recall summary "authentication"
```

---

### `/bk-convert` - JA↔VI Translation

Dịch với glossary IT terms.

```bash
# Dịch text
/bk-convert "テストを実施しました"

# Dịch file
/bk-convert --file input.txt

# Dùng custom glossary
/bk-convert --file input.txt --glossary glossaries/custom.json
```

**Glossary format:**
```json
{
  "バグ": "lỗi",
  "テスト": "kiểm thử",
  "実装": "triển khai"
}
```

---

## Common Workflows

### 1. Kiểm tra tiến độ hàng ngày

```bash
/bk-track status --threshold 2 --lang ja
```

### 2. Tạo báo cáo tuần cho khách hàng

```bash
/bk-track report --format pptx --output weekly-report.pptx
```

### 3. Parse email thành tasks

```bash
# Copy email content vào file
/bk-capture email customer-request.txt
```

### 4. Tạo test documents từ spec

```bash
/bk-spec test feature-spec.md --type all
```

### 5. Tìm context liên quan

```bash
/bk-recall search "payment integration"
```

### 6. Dịch document

```bash
/bk-convert --file japanese-spec.md
```

---

## Troubleshooting

### "Backlog not configured"

Kiểm tra `.env` file có đúng các biến:
```
BACKLOG_SPACE_URL=https://xxx.backlog.jp
BACKLOG_API_KEY=xxx
BACKLOG_PROJECT_KEY=XXX
```

### "GOOGLE_API_KEY not set"

Cần thiết cho `bk-recall` semantic search. Lấy key từ:
https://makersuite.google.com/app/apikey

### Python module not found

```bash
cd .claude/skills
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Skill không chạy

Thử chạy trực tiếp Python script:
```bash
cd .claude/skills/bk-track/scripts
..\..\..\.venv\Scripts\python.exe main.py status
```

---

## Migration từ Skills cũ

Nếu bạn đã dùng BrseKit v1:

| Skill cũ | Skill mới |
|----------|-----------|
| `/bk-status` | `/bk-track status` |
| `/bk-report` | `/bk-track report` |
| `/bk-task` | `/bk-capture task` |
| `/bk-minutes` | `/bk-capture meeting` |
| `/bk-tester` | `/bk-spec test` |
| `/bk-translate` | `/bk-convert` |

---

## Hỗ trợ

- **Issues**: Tạo issue trong repository
- **Slack**: #brsekit-support
- **Wiki**: Xem thêm tài liệu chi tiết trong `docs/`

---

*Last updated: 2026-01-30*
