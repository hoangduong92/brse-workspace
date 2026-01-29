# Week 13: API Patterns

> Phase 2: Backend + Database | Focus: REST API Design & Implementation

---

## 🎯 Week Goals

| Goal | Status |
|------|--------|
| Build API endpoints for Backlog Clone | ⏳ |
| Practice error handling patterns | ⏳ |
| Implement pagination | ⏳ |

---

## 📚 Topics Already Learned (from Week 12)

- [x] REST HTTP Methods (GET/POST)
- [x] PUT vs PATCH
- [x] HTTP Status Codes (200, 201, 204, 400, 409, 422)
- [x] HTTP Request Structure
- [x] 401 vs 403
- [x] API Error Format
- [x] Pagination concepts
- [x] Token in Header vs URL

---

## ✅ API Design Checklist

### Endpoints
- [ ] Use plural nouns (`/users`, `/issues`)
- [ ] Use HTTP methods correctly (GET=read, POST=create, PATCH=update, DELETE=remove)
- [ ] Consistent URL structure (`/resources/:id`)

### Error Handling
- [ ] Consistent error format: `{ error: { code, message, status } }`
- [ ] Correct status codes (400=bad request, 401=unauth, 403=forbidden, 404=not found)
- [ ] Validation errors include field names

### Pagination
- [ ] Support `?page=1&limit=20` params
- [ ] Return pagination metadata: `{ data, pagination: { page, limit, total, totalPages } }`
- [ ] Return empty array (not error) for out-of-range pages

### Security
- [ ] Validate all inputs
- [ ] Check user authorization
- [ ] Don't expose sensitive data in responses

---

## 🔨 Practice: Backlog Clone Endpoints

### Organizations
- [ ] `GET /api/organizations` - List user's orgs
- [ ] `POST /api/organizations` - Create org
- [ ] `GET /api/organizations/:id` - Get org details
- [ ] `PATCH /api/organizations/:id` - Update org
- [ ] `DELETE /api/organizations/:id` - Soft delete

### Projects
- [ ] `GET /api/organizations/:orgId/projects` - List projects
- [ ] `POST /api/organizations/:orgId/projects` - Create project
- [ ] `GET /api/projects/:id` - Get project details
- [ ] `PATCH /api/projects/:id` - Update project

### Issues
- [ ] `GET /api/projects/:projectId/issues` - List issues (with pagination)
- [ ] `POST /api/projects/:projectId/issues` - Create issue
- [ ] `GET /api/issues/:id` - Get issue details
- [ ] `PATCH /api/issues/:id` - Update issue

---

## 📅 Check-in Notes

**Date:** 2026-01-26
**Energy:** 10/10
**Blockers:** Need measurable checklists (addressed above)
**Wins:** 3-day streak với high energy và quyết tâm cao!

---

_Created: 2026-01-26_
