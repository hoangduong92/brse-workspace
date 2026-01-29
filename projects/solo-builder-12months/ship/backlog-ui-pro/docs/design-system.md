# Backlog UI Pro - Design System

## Overview

A Nulab Backlog clone with modern SaaS aesthetics. Swiss Minimalism style with professional blue palette.

## Design Philosophy

- **Style**: Swiss Minimalism + Bento Grid
- **Approach**: Clean, functional, data-dense dashboard
- **Framework**: Next.js 15 + Tailwind CSS + shadcn/ui

---

## Color Palette

### Primary Colors

| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| Primary | `#2563EB` | `blue-600` | Main actions, links, selected states |
| Primary Hover | `#1D4ED8` | `blue-700` | Hover states |
| Primary Light | `#DBEAFE` | `blue-100` | Backgrounds, badges |

### Semantic Colors

| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| Success | `#16A34A` | `green-600` | Completed, resolved |
| Warning | `#CA8A04` | `yellow-600` | In progress, attention |
| Danger | `#DC2626` | `red-600` | Errors, critical |
| Info | `#0891B2` | `cyan-600` | Information, tips |

### Neutral Colors

| Name | Hex | Tailwind | Usage |
|------|-----|----------|-------|
| Background | `#F8FAFC` | `slate-50` | Page background |
| Surface | `#FFFFFF` | `white` | Cards, panels |
| Border | `#E2E8F0` | `slate-200` | Borders, dividers |
| Text Primary | `#0F172A` | `slate-900` | Headings, primary text |
| Text Secondary | `#475569` | `slate-600` | Body text, descriptions |
| Text Muted | `#94A3B8` | `slate-400` | Placeholders, hints |

### Issue Priority Colors

| Priority | Hex | Tailwind |
|----------|-----|----------|
| High | `#DC2626` | `red-600` |
| Normal | `#F97316` | `orange-500` |
| Low | `#16A34A` | `green-600` |

### Issue Status Colors

| Status | Hex | Tailwind |
|--------|-----|----------|
| Open | `#3B82F6` | `blue-500` |
| In Progress | `#F59E0B` | `amber-500` |
| Resolved | `#10B981` | `emerald-500` |
| Closed | `#6B7280` | `gray-500` |

---

## Typography

### Font Family

```css
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
```

```js
// tailwind.config.js
fontFamily: {
  sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
}
```

### Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 30px / `text-3xl` | 700 | 1.2 |
| H2 | 24px / `text-2xl` | 600 | 1.25 |
| H3 | 20px / `text-xl` | 600 | 1.3 |
| H4 | 16px / `text-base` | 600 | 1.4 |
| Body | 14px / `text-sm` | 400 | 1.5 |
| Small | 12px / `text-xs` | 400 | 1.5 |

---

## Spacing System

Use Tailwind's 4px base:

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Tight spacing |
| `space-2` | 8px | Between related items |
| `space-3` | 12px | Component padding |
| `space-4` | 16px | Section spacing |
| `space-6` | 24px | Card padding |
| `space-8` | 32px | Section margins |

---

## Component Specifications

### Sidebar

- Width: `256px` (collapsed: `64px`)
- Background: `slate-900` (dark mode style)
- Item height: `40px`
- Active indicator: `2px` left border `blue-500`

### Header

- Height: `56px`
- Background: `white`
- Border bottom: `1px` `slate-200`
- Shadow: `sm`

### Cards

- Background: `white`
- Border: `1px` `slate-200`
- Border radius: `8px` / `rounded-lg`
- Padding: `16px` / `p-4`
- Shadow: `sm` on hover

### Buttons

| Variant | Background | Text | Border |
|---------|------------|------|--------|
| Primary | `blue-600` | `white` | none |
| Secondary | `white` | `slate-700` | `slate-200` |
| Ghost | `transparent` | `slate-600` | none |
| Danger | `red-600` | `white` | none |

- Height: `36px` (default), `32px` (sm), `40px` (lg)
- Border radius: `6px`
- Padding: `12px 16px`

### Badges

| Type | Background | Text |
|------|------------|------|
| Default | `slate-100` | `slate-700` |
| Primary | `blue-100` | `blue-700` |
| Success | `green-100` | `green-700` |
| Warning | `yellow-100` | `yellow-700` |
| Danger | `red-100` | `red-700` |

- Border radius: `9999px` / `rounded-full`
- Padding: `2px 8px`
- Font size: `12px`

### Tables

- Header: `slate-50` background, `font-medium`
- Row height: `48px`
- Hover: `slate-50` background
- Border: `1px` bottom `slate-100`

### Forms

- Input height: `36px`
- Border: `1px` `slate-200`
- Focus: `2px` ring `blue-500`
- Border radius: `6px`
- Label: `text-sm font-medium text-slate-700`

---

## Layout Structure

```
+------------------+----------------------------------------+
|     Sidebar      |              Header                    |
|     (256px)      |              (56px)                    |
|                  +----------------------------------------+
|                  |                                        |
|   - Logo         |           Main Content                 |
|   - Navigation   |                                        |
|   - Projects     |   +----------------------------------+  |
|                  |   |          Page Header             |  |
|                  |   +----------------------------------+  |
|                  |   |                                  |  |
|                  |   |          Content Area            |  |
|                  |   |                                  |  |
|                  |   +----------------------------------+  |
|                  |                                        |
+------------------+----------------------------------------+
```

---

## Z-Index Scale

| Layer | Value | Usage |
|-------|-------|-------|
| Base | 0 | Default content |
| Dropdown | 10 | Menus, popovers |
| Sticky | 20 | Sticky headers |
| Modal backdrop | 40 | Overlay |
| Modal | 50 | Modal dialogs |
| Toast | 60 | Notifications |
| Tooltip | 70 | Tooltips |

---

## Icons

Use **Lucide React** icons:

```bash
npm install lucide-react
```

Common icons for Backlog:
- `FolderKanban` - Projects
- `ListTodo` - Issues
- `Users` - Members
- `GitBranch` - Git
- `FileText` - Wiki
- `BarChart3` - Charts
- `Settings` - Settings
- `Search` - Search
- `Plus` - Add new
- `MoreHorizontal` - More actions

---

## Responsive Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| `sm` | 640px | Mobile landscape |
| `md` | 768px | Tablet |
| `lg` | 1024px | Small desktop |
| `xl` | 1280px | Desktop |
| `2xl` | 1536px | Large desktop |

### Sidebar Behavior

- `< 1024px`: Collapsed to icons only or drawer
- `>= 1024px`: Full sidebar visible

---

## Animation

- Duration: `150-200ms` for micro-interactions
- Easing: `ease-out` for entrances, `ease-in` for exits
- Use `transform` and `opacity` only for performance

```css
.transition-default {
  @apply transition-all duration-150 ease-out;
}
```

---

## Accessibility Checklist

- [ ] Color contrast ratio >= 4.5:1 for text
- [ ] Focus visible on all interactive elements
- [ ] Touch targets >= 44x44px on mobile
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Keyboard navigation works
- [ ] `prefers-reduced-motion` respected

---

## Anti-Patterns to Avoid

- No emojis as icons - use Lucide icons
- No layout shift on hover - use opacity/color only
- No `z-index: 9999` - use defined scale
- No infinite animations except loaders
- No transparent text on light backgrounds
- No `cursor-default` on clickable elements
