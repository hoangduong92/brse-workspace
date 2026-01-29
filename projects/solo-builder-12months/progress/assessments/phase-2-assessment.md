# Phase 2 Assessment: Backend + Database

> Complete this before moving to Phase 3 (AI Integration)

## Part A: Quiz (15 questions)

### Database Design (5 questions)

**Q1.** Khi nào dùng **column** vs **separate table**?
- A) Column khi data nhỏ, table khi data lớn
- B) Column khi chỉ là value, table khi có data riêng (created_at, metadata)
- C) Không quan trọng, chọn gì cũng được
- D) Luôn dùng separate table cho tất cả

**Q2.** Junction table dùng khi nào?
- A) 1:1 relationship
- B) 1:N relationship
- C) N:M relationship
- D) Khi muốn thêm index

**Q3.** Tại sao dùng `deleted_at` thay vì `is_deleted`?
- A) Ngắn hơn
- B) Có thêm timestamp info, audit trail
- C) Database yêu cầu
- D) Performance tốt hơn

**Q4.** Lookup table là gì?
- A) Table chứa foreign keys
- B) Table chứa options/choices ít thay đổi (statuses, roles)
- C) Table để search nhanh
- D) Table tạm thời

**Q5.** First Normal Form (1NF) nghĩa là?
- A) Mỗi table chỉ có 1 column
- B) Không lưu multiple values trong 1 column
- C) Phải có primary key
- D) Phải có foreign key

### Supabase + Auth (5 questions)

**Q6.** `NEXT_PUBLIC_` prefix trong env var có nghĩa gì?
- A) Variable public trên internet
- B) Variable accessible từ browser (client-side)
- C) Variable cho production only
- D) Variable cho Next.js internal

**Q7.** Row Level Security (RLS) dùng để làm gì?
- A) Encrypt data
- B) Giới hạn user chỉ access data của họ
- C) Speed up queries
- D) Backup data

**Q8.** Supabase Auth session được lưu ở đâu?
- A) Database
- B) Browser cookies/localStorage
- C) Server memory
- D) Vercel

**Q9.** Khi user logout, điều gì xảy ra với session?
- A) Session bị xóa khỏi browser
- B) Session vẫn còn nhưng invalid
- C) Database row bị delete
- D) Không có gì

**Q10.** Foreign key constraint đảm bảo điều gì?
- A) Data unique
- B) Referenced row phải tồn tại
- C) Column not null
- D) Fast query

### API Design (5 questions)

**Q11.** REST API: GET vs POST khác nhau thế nào?
- A) GET lấy data, POST tạo/update data
- B) GET nhanh hơn POST
- C) Không khác nhau
- D) GET cho authenticated, POST cho public

**Q12.** HTTP status 401 vs 403?
- A) 401 = not found, 403 = error
- B) 401 = not authenticated, 403 = not authorized
- C) Giống nhau
- D) 401 = success, 403 = redirect

**Q13.** Tại sao API nên return consistent error format?
- A) Đẹp hơn
- B) Frontend dễ handle, debug dễ hơn
- C) Database yêu cầu
- D) Security

**Q14.** API endpoint nên dùng plural hay singular? `/user` vs `/users`
- A) Singular cho 1 item, plural cho collection
- B) Luôn plural (convention)
- C) Luôn singular
- D) Không quan trọng

**Q15.** Pagination trong API quan trọng vì?
- A) Đẹp hơn
- B) Tránh load quá nhiều data, performance + memory
- C) Security
- D) SEO

---

## Part B: Explain-to-me (Pick 1)

Chọn 1 trong các options sau, mở code và giải thích cho mentor:

### Option 1: Database Schema
Mở file SQL migration của Backlog Clone, giải thích:
- Tại sao có table này?
- Relationship giữa các tables?
- Lookup tables nào và tại sao?

### Option 2: Auth Flow
Mở auth code trong Personal Dashboard, giải thích:
- User login → session created → how?
- Protected route hoạt động thế nào?
- Logout flow?

### Option 3: CRUD Operations
Mở CRUD code, giải thích:
- Create flow từ button click → database
- Error handling ở đâu?
- Optimistic update là gì (nếu có)?

---

## Scoring

| Part | Weight | Your Score |
|------|--------|------------|
| Part A: Quiz | 60% | ___ / 15 |
| Part B: Explain | 40% | ___ / 10 |
| **Total** | 100% | ___ % |

**Pass threshold: 70%**

---

## After Assessment

- [ ] Review incorrect answers
- [ ] Re-read relevant chapters
- [ ] Retake if needed
- [ ] Move to Phase 3 when passed

---

_Assessment v1.0 - 2026-01-25_
