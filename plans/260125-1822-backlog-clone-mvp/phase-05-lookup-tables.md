# Phase 5: Lookup Tables Management

## Overview

| Attribute | Value |
|-----------|-------|
| Priority | P1 - Important |
| Status | ✅ Completed |
| Estimated | 2 hours |
| Actual | 25 minutes |
| Depends On | Phase 4 |
| Completed | 2026-01-25 19:15 |

Implement CRUD for customizable lookup tables: statuses, issue_types, categories.

## Requirements

- Admin can add/edit/delete statuses
- Admin can reorder statuses (display_order)
- Admin can customize colors
- Admin can add/edit/delete issue types
- Admin can add/edit/delete categories
- Categories have `allow_multiple` toggle

## Files to Create

```
src/
├── lib/api/
│   ├── statuses.ts
│   ├── issue-types.ts
│   └── categories.ts
├── app/(dashboard)/projects/[projectKey]/settings/
│   ├── page.tsx
│   ├── statuses/page.tsx
│   ├── types/page.tsx
│   └── categories/page.tsx
└── components/settings/
    ├── status-manager.tsx
    ├── type-manager.tsx
    └── category-manager.tsx
```

## API Functions

```typescript
// Each lookup table needs:
- create(projectId, data)
- getAll(projectId)
- update(id, data)
- delete(id)
- reorder(projectId, orderedIds)  // for statuses
```

## Todo List

- [x] Create statuses API
- [x] Create issue_types API
- [x] Create categories API
- [x] Build settings page layout
- [x] Build status manager with up/down reorder
- [x] Build type manager with color picker
- [x] Build category manager with allow_multiple toggle
- [x] Prevent deleting if items are in use

## Success Criteria

- [x] Can add custom statuses
- [x] Can reorder statuses
- [x] Can customize colors
- [x] Can add custom issue types
- [x] Can add categories with multi-select option

---

_Created: 2026-01-25_
