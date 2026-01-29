# Backlog Clone MVP - Implementation Plan

## Overview

| Attribute | Value |
|-----------|-------|
| Project | Backlog Clone (Nulab Backlog alternative) |
| Phase | Phase 2: Backend + Database (Week 11-16) |
| Started | 2026-01-25 |
| Target | Week 16 |

## Goals

Build a functional project management tool similar to Nulab Backlog with:
- Multi-tenant organization support
- Project & issue management
- User roles & permissions
- Comments & documents

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15 (App Router) + TypeScript |
| Backend | Supabase (PostgreSQL + Auth + RLS) |
| Styling | Tailwind CSS + shadcn/ui |
| Deployment | Vercel |

## Design System

| Aspect | Value |
|--------|-------|
| UI/UX Skill | /ui-ux-pro-max consulted (2026-01-25) |
| Style | Swiss Modernism + Minimalism |
| Font | Plus Jakarta Sans |
| Primary Color | #2563EB (Trust Blue) |
| Accessibility | WCAG AAA |
| Details | See [Phase 7](./phase-07-ui-components.md) |

## Phase Overview

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Database Schema Setup | ✅ |
| 2 | Core CRUD: Organizations & Users | ✅ |
| 3 | Core CRUD: Projects & Members | ✅ |
| 4 | Core CRUD: Issues & Comments | ✅ |
| 5 | Lookup Tables: Status, Types, Categories | ✅ |
| 6 | Row Level Security (RLS) | ✅ |
| 7 | UI Components & Pages | ✅ |

## Detailed Phases

- [Phase 1: Database Schema](./phase-01-database-schema.md)
- [Phase 2: Organizations & Users CRUD](./phase-02-organizations-users.md)
- [Phase 3: Projects & Members CRUD](./phase-03-projects-members.md)
- [Phase 4: Issues & Comments CRUD](./phase-04-issues-comments.md)
- [Phase 5: Lookup Tables](./phase-05-lookup-tables.md)
- [Phase 6: Row Level Security](./phase-06-rls.md)
- [Phase 7: UI Components](./phase-07-ui-components.md)

## Key Files

```
projects/solo-builder-12months/ship/backlog-clone/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [projectKey]/
│   │   │   │       ├── page.tsx
│   │   │   │       ├── issues/
│   │   │   │       └── settings/
│   │   │   └── settings/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/
│   │   ├── issues/
│   │   ├── projects/
│   │   └── common/
│   ├── lib/
│   │   ├── supabase/
│   │   │   ├── client.ts
│   │   │   ├── server.ts
│   │   │   └── middleware.ts
│   │   ├── hooks/
│   │   └── utils/
│   └── types/
│       └── database.ts
├── supabase/
│   └── migrations/
│       └── 001_initial_schema.sql
└── docs/
    └── er-diagram.md
```

## Success Criteria

- [ ] All 13 tables created in Supabase
- [ ] CRUD operations working for all entities
- [ ] RLS policies protecting data
- [ ] Users can create org, invite members, manage projects
- [ ] Issues can be created, assigned, commented on
- [ ] Deployed to Vercel

## Dependencies

- Supabase project (existing or new)
- Vercel account
- GitHub repo

---

_Created: 2026-01-25_
