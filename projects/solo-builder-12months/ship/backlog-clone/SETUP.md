# Backlog Clone - Setup Guide

## Prerequisites

- Node.js 20+
- Supabase account (free tier works)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Supabase

1. Create a new project in [Supabase](https://supabase.com)
2. Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```
3. Add your Supabase credentials to `.env.local`:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

### 3. Run Database Migrations

Execute SQL files in order via Supabase Dashboard → SQL Editor:

1. `supabase/migrations/001_initial_schema.sql` - Database schema
2. `supabase/migrations/002_auth_trigger.sql` - Profile auto-creation

### 4. Start Development Server

```bash
npm run dev
```

Visit http://localhost:3000

## First Time Setup Flow

1. **Sign Up**
   - Navigate to /signup
   - Create account with email/password
   - Profile auto-created via trigger

2. **Create Organization**
   - Redirected to /dashboard/onboarding
   - Enter organization name & slug
   - Organization created with default roles

3. **Access Dashboard**
   - Redirected to /dashboard
   - View organization info in nav
   - Ready to create projects

## Auth Features

- ✅ Email/Password signup
- ✅ Email/Password login
- ✅ Profile auto-creation
- ✅ Organization management
- ✅ Protected routes via middleware
- ✅ Automatic redirects

## Project Structure

```
src/
├── app/
│   ├── (auth)/           # Auth pages (login, signup)
│   └── (dashboard)/      # Protected dashboard pages
├── components/
│   └── auth/             # Auth-related components
├── lib/
│   ├── api/              # API functions
│   └── supabase/         # Supabase clients
├── middleware.ts         # Route protection
└── types/
    └── database.ts       # TypeScript types
```

## Common Issues

### "Invalid API key"
- Check `.env.local` has correct Supabase URL & anon key
- Restart dev server after changing env vars

### "Profile not found"
- Ensure `002_auth_trigger.sql` executed in Supabase
- Check Supabase logs for trigger errors

### "Organization not created"
- Check Supabase table browser for organizations table
- Verify RLS policies allow authenticated inserts

## Next Steps

After setup complete:
- Phase 3: Projects & Members CRUD
- Phase 4: Issues & Statuses
- Phase 5: UI Polish & UX

## Tech Stack

- **Framework:** Next.js 16.1.4 (App Router)
- **Auth:** Supabase Auth
- **Database:** Supabase (PostgreSQL)
- **Styling:** Tailwind CSS 4
- **Language:** TypeScript 5
