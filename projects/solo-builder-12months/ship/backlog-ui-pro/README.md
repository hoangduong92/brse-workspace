# Backlog UI Pro

A modern, clean clone of Nulab Backlog project management tool built with Next.js 15, Tailwind CSS, and shadcn/ui.

## Features

- **Dashboard** - Overview of projects, issues, and activity
- **Issues List** - Filterable, sortable issue tracking table
- **Responsive Sidebar** - Collapsible navigation with project switcher
- **Modern Design** - Swiss Minimalism style with professional blue palette

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Typography**: Plus Jakarta Sans

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Navigate to project directory
cd projects/solo-builder-12months/ship/backlog-ui-pro

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Dashboard/Home page
│   └── issues/
│       └── page.tsx        # Issues list page
├── components/
│   ├── dashboard/          # Dashboard-specific components
│   │   └── dashboard-content.tsx
│   ├── issues/             # Issue-related components
│   │   ├── issue-filters.tsx
│   │   ├── issue-table.tsx
│   │   └── issues-page-content.tsx
│   ├── layout/             # Layout components
│   │   ├── app-layout.tsx
│   │   ├── header.tsx
│   │   └── sidebar.tsx
│   └── ui/                 # shadcn/ui components
│       ├── avatar.tsx
│       ├── badge.tsx
│       ├── button.tsx
│       ├── scroll-area.tsx
│       ├── separator.tsx
│       └── tooltip.tsx
├── lib/
│   └── utils.ts            # Utility functions (cn)
└── globals.css             # Global styles & CSS variables
```

## Design System

See [docs/design-system.md](docs/design-system.md) for complete design specifications including:

- Color palette (Primary, Semantic, Neutral)
- Typography scale
- Component specifications
- Spacing system
- Z-index scale
- Accessibility guidelines

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with Turbopack |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |

## Pages

| Route | Description |
|-------|-------------|
| `/` | Dashboard with stats, recent issues, activity feed |
| `/issues` | Issue list with filters, search, and status tabs |

## License

MIT
