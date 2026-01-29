# Solo Builder Learner Profile

> Persistent memory - Auto-updated by Stop hook

---

## 📊 Overview

| Metric | Value |
|--------|-------|
| First session | 2026-01-24 |
| Total sessions | 81 |
| Last active | 2026-01-24 00:09

### Journey Info
- **Current Phase**: 2 - Backend + Database (Fast-track)
- **Current Week**: 1 (Calendar) / Week 13 (Curriculum - API Patterns)

---

## Learning Style
| Aspect | Preference |
|--------|------------|
| Pace | Fast (with assessment gates) |
| Examples | Prefer code examples |
| Depth | Understand why before how |
| Language | Vietnamese + English terms |
| Assessment | Quiz + Explain-to-me (no coding challenges) |
| Books | English technical books |
| Philosophy | AI era = read code, not write. Understanding > memorizing syntax |

---

## Tech Background
| Area | Level (1-5) | Notes |
|------|-------------|-------|
| JavaScript | 1 | Starting |
| React/Next.js | 3 | Props, useState, useEffect, event handling, conditional rendering |
| TypeScript | 2 | Interface for props, type annotations |
| Node.js | 1 | - |
| SQL/Database | 2 | Supabase CRUD, basic SQL |
| Git | 2 | Commit, push, GitHub repo |
| API Design | 1 | - |
| AI/LLM APIs | 1 | - |
| Deployment | 2 | Vercel, CI/CD flow |

---

## 🎯 Learning Journey

### Topics Learned
<!-- Format: - [date] Topic: brief description -->
- [2026-01-24] **Next.js App Structure**: src/app/, page.tsx, layout.tsx
- [2026-01-24] **File-based Routing**: folder = URL path
- [2026-01-24] **Link Component**: Client-side navigation vs `<a>` reload
- [2026-01-24] **Vercel Deployment**: GitHub → Vercel CI/CD flow
- [2026-01-24] **Serverless**: Code chạy on-demand, không 24/7
- [2026-01-24] **Config Files**: next.config.ts, eslint.config.mjs, tsconfig.json
- [2026-01-24] **React Component Basics**: Component = function trả về JSX, uppercase vs lowercase, children prop, layout composition
- [2026-01-24] **React useState**: State vs let, "use client" requirement, memory-based (lost on refresh), React DevTools
- [2026-01-24] **Props & Interface**: Props = component parameters, Interface = type contract for TypeScript
- [2026-01-24] **Event Handling**: onChange, onClick, onKeyDown, event object (e.target, e.key)
- [2026-01-24] **Conditional Rendering**: `{condition && <Component />}`, ternary operator
- [2026-01-24] **useEffect**: Side effects after render, dependency array, cleanup function
- [2026-01-24] **useEffect Cleanup**: return () => cleanup, runs before re-run or unmount
- [2026-01-24] **localStorage**: getItem/setItem, JSON.parse/stringify, browser persistence
- [2026-01-24] **Dependency Array**: [] = once on mount, [x] = when x changes
- [2026-01-24] **Supabase Client**: createClient, env vars, NEXT_PUBLIC_ prefix
- [2026-01-24] **Database CRUD**: select, insert, update, delete với Supabase
- [2026-01-24] **Supabase Auth**: user context, session management, user_id foreign key
- [2026-01-24] **Supabase URL Config**: Site URL + Redirect URLs must match production domain
- [2026-01-25] **Entity vs Column**: Table khi có data riêng, Column khi chỉ là value
- [2026-01-25] **1:N Relationship**: One-to-Many, dùng FK column (assignee_id)
- [2026-01-25] **N:M Relationship**: Many-to-Many, cần junction table (project_members)
- [2026-01-25] **Junction Table**: Bảng trung gian connect 2 tables N:M
- [2026-01-25] **Lookup Tables**: Chứa options/choices, ít thay đổi (statuses, roles)
- [2026-01-25] **First Normal Form (1NF)**: Không lưu multiple values trong 1 column
- [2026-01-25] **allow_multiple Pattern**: UI setting, không đổi schema, chỉ đổi app logic
- [2026-01-25] **deleted_at vs is_deleted**: Timestamp > boolean, có thêm info thời gian
- [2026-01-25] **REST HTTP Methods**: GET = read (idempotent), POST = create/write (side effects)
- [2026-01-25] **401 vs 403**: 401 = not authenticated, 403 = not authorized (có quyền khác)
- [2026-01-25] **API Error Format**: Consistent format giúp frontend handle errors dễ hơn
- [2026-01-25] **Plural Endpoints**: REST convention luôn dùng plural (/users, /users/123)
- [2026-01-25] **Pagination**: Tránh load quá nhiều data, performance + memory
- [2026-01-26] **Database Index**: Mục lục giúp query nhanh, dùng cho FK/WHERE/ORDER BY columns
- [2026-01-26] **B-tree Index**: Data sorted, works for exact match & prefix search, NOT for `%keyword%`
- [2026-01-26] **Index Trade-off**: Read faster ↔ Write slower, chỉ index khi table lớn & query nhiều
- [2026-01-26] **DB Design Checklist**: 6 categories - Integrity, Normalization, Relationships, Performance, Scalability, Security
- [2026-01-26] **Index Types**: B-tree (default), GIN (full-text/JSONB), GiST (geo), BRIN (time-series)
- [2026-01-26] **PUT vs PATCH**: PUT = replace all, PATCH = update part (90% dùng PATCH)
- [2026-01-26] **HTTP Status Codes**: 200 OK, 201 Created, 204 No Content, 400/409/422 client errors
- [2026-01-26] **HTTP Request Structure**: Request line + Headers + Empty line + Body
- [2026-01-26] **MIME Types**: type/subtype format (application/json, text/html, image/png)
- [2026-01-26] **Token in Header vs URL**: Header safer by default (not logged/stored), not because hidden in transmission
- [2026-01-26] **Host Header**: Cho phép 1 IP host nhiều sites (virtual hosting)
- [2026-01-26] **Pagination Edge Case**: page > totalPages → return 200 + empty array (not error)

### In Progress
<!-- Topics đang học dở -->
- Tailwind CSS basics
- Deploying fullstack apps

### Queued (Phase 2)
<!-- Topics user muốn học tiếp -->
- ~~Supabase setup & SQL basics~~ ✅
- ~~Database CRUD operations~~ ✅
- ~~Authentication (Supabase Auth)~~ ✅
- Payment integration
- Row Level Security (RLS)

---

## 💪 Strengths
<!-- Concepts user đã master -->

---

## 🔧 Areas to Improve
<!-- Concepts user còn yếu, cần review lại -->

---

## 📝 Quiz Performance

### Recent Quizzes
<!-- Format: - [date] Topic: score/total - notes -->
- [2026-01-24] File-based Routing: 1/1 ✅ - Biết tạo page ở đâu
- [2026-01-24] Điểm tốt trong design hiện tại: 1/1 ✅
- [2026-01-24] Link vs `<a>`: 1/1 ✅ - Hiểu tại sao cần Link
- [2026-01-24] Serverless: 1/1 ✅ - Hiểu code nằm ở Vercel
- [2026-01-24] Layout usage: 1/1 ✅ - Biết đặt navbar ở layout
- [2026-01-24] React Component Basics: 3/3 ✅ - Component=function, uppercase/lowercase, layout/children
- [2026-01-24] React useState: 3/3 ✅ - State vs let, "use client", memory persistence
- [2026-01-24] Props: 1/1 ✅ - Biết thêm prop vào interface
- [2026-01-24] Conditional Rendering: 0/1 ❌ - Nhầm Timer button là component riêng, không phải trong TodoList
- [2026-01-24] useEffect Cleanup: 0.5/1 ⚠️ - Biết A chạy, nhưng quên B (cleanup) chạy trước
- [2026-01-24] Dependency Array: 1/1 ✅ - Hiểu [] vs [todos], biết data sẽ mất nếu dùng sai
- [2026-01-25] **Phase 2 Assessment: 11/15 (73%) ✅ PASSED**
  - Database Design: 5/5 ✅ Perfect
  - Supabase + Auth: 2/5 ⚠️ Need review (NEXT_PUBLIC_, session storage, logout)
  - API Design: 4/5 ✅ Good (plural endpoints convention)
- [2026-01-26] **Database Index: 2.5/3 (83%) ✅** - Q1 partial: B-tree sorted nature, not "absolute search"

### Common Mistakes
<!-- Patterns of mistakes để focus review -->
- useEffect cleanup order: cần nhớ cleanup chạy TRƯỚC effect mới
- Component composition: cần đọc kỹ code structure để hiểu component nào nằm trong component nào
- NEXT_PUBLIC_ prefix: nhầm "public internet" vs "browser accessible" - cần phân biệt client/server env vars
- Session storage: serverless = stateless, session phải lưu ở browser, không phải server memory
- Logout flow: signOut() XÓA token khỏi browser, không phải "không làm gì"
- B-tree index: không phải "tìm kiếm tuyệt đối" - mà là data SORTED, prefix search works, middle search doesn't

---

## 💡 Learning Insights

### Preferences
<!-- How user learns best: examples, analogies, code-first... -->
- Thích hỏi sâu về bản chất ("tại sao Link làm được?")
- Responds well to diagrams and flow charts
- Prefers Vietnamese + English technical terms
- **Build-first, Explain-from-code** approach works better than theory-first
- Likes analogies (interface=menu, cleanup=tắt đèn khi ra khỏi phòng)

### Questions Asked
<!-- Interesting questions user đã hỏi -->
- "Bản chất của Link là gì mà nó làm được điều mà thẻ a không làm được?"
- "Server là đối tượng nào? Code trong project hay hạ tầng Vercel?"
- Hỏi về config files: next.config, eslint, tsconfig
- "Interface giống class trong OOP à?" - So sánh Interface vs Class
- "useEffect dùng khi nào?" - Hiểu side effects pattern
- "Trigger unmount ở đâu trong code?" - Deep dive vào React lifecycle
- "Đâu là checklist để verify database design đã tối ưu chưa?" - Tư duy ngược từ DoD về gaps
- "Tại sao header không bị lộ? Logging được quy định ở đâu?" - Deep dive HTTP security

---

## 😊 Teaching Feedback

### Satisfaction Trend
<!-- Auto-captured from implicit sentiment analysis -->
| Date | Rating | Sentiment | Summary |
|------|--------|-----------|---------|
| 2026-01-24 | 4/10 | 😔 negative | Mild negative signals |
| 2026-01-24 | 4/10 | 😔 negative | Mild negative signals |
| 2026-01-24 | 4/10 | 😔 negative | Mild negative signals |

### What Works Well
- examples
<!-- Teaching approaches user responds positively to -->

### Pain Points
- tooSlow
- tooDetailed
- tooFast
<!-- Teaching approaches that frustrate user -->

### Suggested Adaptations
<!-- AI-generated suggestions based on feedback patterns -->

---

## 📅 Session History
<!-- Recent 10 sessions - Auto-updated -->

| Date | Time | Topics | Notes |
|------|------|--------|-------|
| 2026-01-24 | 23:55 | general | 2Q, 5/10 |
| 2026-01-24 | 23:57 | general | 1Q, 5/10 |
| 2026-01-24 | 23:57 | general | 2Q, 5/10 |
| 2026-01-24 | 23:58 | general | 2Q, 5/10 |
| 2026-01-24 | 23:59 | general | 2Q, 4/10 |
| 2026-01-24 | 00:02 | general | 2Q, 4/10 |
| 2026-01-24 | 00:02 | general | 2Q, 4/10 |
| 2026-01-24 | 00:03 | general | 2Q, 4/10 |
| 2026-01-24 | 00:08 | general | 2Q, 4/10 |
| 2026-01-24 | 00:09 | general | 2Q, 4/10 |

---

## Mentor Notes
- Week 1: Starting journey. Focus on shipping first, learning second.
- Philosophy: "Learn to Read, Not Write" - AI writes, you understand.
- **Fast-track enabled**: Completed Phase 1 (8 weeks content) in Day 1
- Moving to Phase 2 (Supabase) - "Build fast, learn when stuck" approach
- Strong quiz performance on core React concepts
