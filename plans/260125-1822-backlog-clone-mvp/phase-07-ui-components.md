# Phase 7: UI Components & Polish

## Overview

| Attribute | Value |
|-----------|-------|
| Priority | P1 - Important |
| Status | ⬜ Not Started |
| Estimated | 4-6 hours |
| Depends On | Phase 6 |
| UI/UX Consulted | ✅ /ui-ux-pro-max (2026-01-25) |

Build polished UI components and complete the user experience.

---

## Design System (Consulted via /ui-ux-pro-max)

### Style: Swiss Modernism / Minimalism

| Aspect | Value |
|--------|-------|
| Style | Swiss Modernism 2.0 + Minimalism |
| Keywords | Clean, grid-based, functional, spacious, professional |
| Performance | Excellent |
| Accessibility | WCAG AAA |
| Complexity | Low |

### Color Palette (SaaS Dashboard)

```css
:root {
  /* Primary - Trust Blue */
  --primary: #2563EB;
  --primary-light: #3B82F6;
  --primary-dark: #1D4ED8;

  /* Secondary */
  --secondary: #64748B;
  --secondary-light: #94A3B8;

  /* CTA/Accent */
  --cta: #F97316;
  --cta-hover: #EA580C;

  /* Background */
  --bg-primary: #FFFFFF;
  --bg-secondary: #F8FAFC;
  --bg-tertiary: #F1F5F9;

  /* Text */
  --text-primary: #1E293B;
  --text-secondary: #475569;
  --text-muted: #64748B;

  /* Border */
  --border: #E2E8F0;
  --border-focus: #2563EB;

  /* Status Colors */
  --status-open: #6B7280;
  --status-in-progress: #2563EB;
  --status-resolved: #16A34A;
  --status-closed: #9CA3AF;

  /* Issue Type Colors */
  --type-bug: #DC2626;
  --type-feature: #7C3AED;
  --type-task: #0891B2;
  --type-improvement: #059669;
}
```

### Typography

| Element | Font | Weight | Size | Color |
|---------|------|--------|------|-------|
| H1 | Plus Jakarta Sans | 700 | 2rem (32px) | text-primary |
| H2 | Plus Jakarta Sans | 600 | 1.5rem (24px) | text-primary |
| H3 | Plus Jakarta Sans | 600 | 1.25rem (20px) | text-primary |
| Body | Plus Jakarta Sans | 400 | 1rem (16px) | text-secondary |
| Caption | Plus Jakarta Sans | 400 | 0.875rem (14px) | text-muted |
| Small | Plus Jakarta Sans | 400 | 0.75rem (12px) | text-muted |

**Google Fonts Import:**
```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
```

### Tailwind Config Extension

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss"

const config: Config = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#2563EB",
          light: "#3B82F6",
          dark: "#1D4ED8",
        },
        secondary: {
          DEFAULT: "#64748B",
          light: "#94A3B8",
        },
        cta: {
          DEFAULT: "#F97316",
          hover: "#EA580C",
        },
        status: {
          open: "#6B7280",
          "in-progress": "#2563EB",
          resolved: "#16A34A",
          closed: "#9CA3AF",
        },
        issue: {
          bug: "#DC2626",
          feature: "#7C3AED",
          task: "#0891B2",
          improvement: "#059669",
        },
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "system-ui", "sans-serif"],
      },
    },
  },
}
```

---

## shadcn/ui Components

Use shadcn blocks for scaffolding. Install required components:

```bash
npx shadcn@latest add button card dialog dropdown-menu input label select separator sheet sidebar skeleton table tabs textarea toast avatar badge
```

### Core Components Mapping

| Component | shadcn | Custom Styling |
|-----------|--------|----------------|
| Sidebar | sidebar-01 | Fixed left, collapsible |
| Navbar | - | Custom with user menu |
| Cards | card | rounded-lg shadow-sm |
| Forms | form + inputs | Consistent spacing |
| Modals | dialog | Max 600px width |
| Dropdowns | dropdown-menu | 8px radius |
| Tables | table | Striped rows |
| Badges | badge | Status/type colors |

---

## UI Components

### Layout Components
- [ ] Sidebar navigation (shadcn sidebar)
- [ ] Top navbar with org switcher + user menu
- [ ] Breadcrumbs (custom)
- [ ] Mobile responsive layout (sheet for mobile nav)

### Dashboard
- [ ] Project cards grid (Bento style)
- [ ] Quick stats cards (open issues, assigned to me)
- [ ] Recent activity feed

### Project View
- [ ] Issue board (Kanban - optional)
- [ ] Issue list with filters/sorting
- [ ] Project sidebar (statuses, members, filters)

### Issue Components
- [ ] Issue card (compact, hover state)
- [ ] Issue detail page/modal
- [ ] Status badge with semantic color
- [ ] Type icon with color (Lucide icons)
- [ ] Assignee avatar (avatar component)
- [ ] Comment thread
- [ ] Rich text editor (optional - tiptap)

### Forms
- [ ] Create project form
- [ ] Create issue form
- [ ] Comment form
- [ ] Settings forms

---

## UX Guidelines

### Animation & Transitions

| Interaction | Duration | Easing |
|-------------|----------|--------|
| Hover | 150-200ms | ease-out |
| Modal open | 200-300ms | ease-out |
| Page transition | 200ms | ease-out |
| Skeleton pulse | 2s loop | ease-in-out |

```css
/* Base transition class */
.transition-base {
  @apply transition-all duration-200 ease-out;
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Loading States

- [ ] Skeleton screens for lists/cards
- [ ] Button loading spinners (disable + spinner)
- [ ] Page loading indicator (top progress bar)
- [ ] Optimistic updates for smooth UX

### Interaction Rules

| Rule | Implementation |
|------|----------------|
| Cursor | `cursor-pointer` on all clickables |
| Hover | Color/shadow change, no layout shift |
| Focus | Visible focus ring (outline-2 outline-primary) |
| Disabled | Reduced opacity (0.5) + cursor-not-allowed |
| Loading buttons | disabled + spinner icon |

### Accessibility (WCAG AAA)

- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] Tab order matches visual order
- [ ] Focus visible on all interactive elements
- [ ] Minimum touch target 44x44px
- [ ] Text contrast ratio 4.5:1 minimum

---

## Pages Checklist

### Auth Pages
- [ ] `/login` - Login with email/password
- [ ] `/signup` - Signup with org creation

### Dashboard
- [ ] `/dashboard` - Main dashboard (projects overview)
- [ ] `/dashboard/projects` - Projects list
- [ ] `/dashboard/projects/new` - Create project form

### Project Pages
- [ ] `/dashboard/projects/[key]` - Project board/kanban
- [ ] `/dashboard/projects/[key]/issues` - Issues list
- [ ] `/dashboard/projects/[key]/issues/new` - Create issue
- [ ] `/dashboard/projects/[key]/issues/[num]` - Issue detail
- [ ] `/dashboard/projects/[key]/settings` - Project settings

### Settings
- [ ] `/dashboard/settings` - User/org settings
- [ ] `/dashboard/settings/members` - Member management

---

## Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, sheet nav |
| Tablet | 640-1024px | Collapsible sidebar |
| Desktop | 1024-1440px | Fixed sidebar |
| Wide | > 1440px | Centered max-w-7xl |

---

## Pre-Delivery Checklist

### Visual Quality
- [ ] No emojis as icons (use Lucide/Heroicons SVG)
- [ ] All icons from consistent set (Lucide)
- [ ] Hover states don't cause layout shift
- [ ] Theme colors used directly (not var() wrapper)

### Interaction
- [ ] All clickable elements have cursor-pointer
- [ ] Hover states provide clear feedback
- [ ] Transitions 150-300ms
- [ ] Focus states visible for keyboard nav

### Light/Dark Mode
- [ ] Light mode text has 4.5:1 contrast
- [ ] Borders visible in both modes
- [ ] Test both modes before delivery

### Layout
- [ ] Floating elements have proper edge spacing
- [ ] No content behind fixed navbar
- [ ] Responsive at 375px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile

---

## Optional Enhancements

- [ ] Real-time updates with Supabase subscriptions
- [ ] Drag-and-drop Kanban board (dnd-kit)
- [ ] Markdown support in descriptions (react-markdown)
- [ ] File attachments (Supabase storage)
- [ ] Notifications (toast + bell icon)
- [ ] Dark mode toggle

---

## Success Criteria

- [ ] All pages functional and styled
- [ ] Mobile responsive (375px+)
- [ ] Loading states implemented
- [ ] Error handling with user feedback
- [ ] Accessibility audit passed
- [ ] Deployed to Vercel

---

_Created: 2026-01-25_
_UI/UX Consulted: /ui-ux-pro-max skill_
