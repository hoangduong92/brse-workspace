# Backlog Issues Filter

Filter Backlog issues và tiết kiệm tokens khi làm việc với LLM.

## Problem

Khi gọi Backlog API hoặc MCP server, response trả về **rất nhiều data** (~2000+ tokens/issue):
- Full issue details
- User info với avatars
- Custom fields
- Attachments metadata
- ...

Khi có 40+ issues → **~80,000 tokens** trong conversation!

## Solution

**Filter ngay sau khi fetch**, chỉ giữ lại fields cần thiết:
- `id`
- `issueKey` (as `key`)
- `summary`

→ Giảm xuống còn **~20 tokens/issue** → Tiết kiệm **99% tokens**!

## Setup

1. Install dependencies:
```bash
npm install
```

2. Tạo file `.env`:
```bash
cp .env.example .env
```

3. Thêm Backlog credentials vào `.env`:
```
BACKLOG_SPACE_KEY=your-space
BACKLOG_API_KEY=your-api-key
```

## Usage

### Fetch từ Backlog API (recommended)
```bash
npm start
```

Sẽ fetch subtasks chưa closed từ project 47358 và filter ngay.

### Demo với sample data
```bash
npm run demo
```

## Code Structure

- `src/backlog-client.ts` - Backlog API client với filtering built-in
- `src/fetch-subtasks.ts` - Script fetch và hiển thị filtered data
- `src/index.ts` - Core filtering logic
- `src/demo.ts` - Demo với sample data

## Benefits

✅ **Tiết kiệm tokens**: 99% reduction
✅ **Faster**: Ít data = process nhanh hơn
✅ **Cleaner**: Chỉ hiển thị info cần thiết
✅ **Cheaper**: Ít tokens = ít cost khi dùng LLM API

## Token Comparison

| Approach | Tokens | Notes |
|----------|--------|-------|
| Full MCP response | ~80,000 | 40 issues x 2000 tokens |
| Filtered response | ~800 | 40 issues x 20 tokens |
| **Savings** | **99%** | ~79,200 tokens saved! |
