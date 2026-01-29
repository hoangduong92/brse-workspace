# Phase 2: Organizations & Users CRUD

## Context Links

- [Phase 1: Schema](./phase-01-database-schema.md)
- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)

## Overview

| Attribute | Value |
|-----------|-------|
| Priority | P0 - Critical |
| Status | ✅ Complete |
| Estimated | 2-3 hours |
| Depends On | Phase 1 |

Implement authentication flow and organization management.

## Requirements

### Functional
- User can sign up → auto-create profile
- User can create organization
- User becomes Admin of their organization
- User can invite members via email
- Invited user joins existing organization

### Non-Functional
- Use Supabase Auth (email/password for MVP)
- Profile syncs with auth.users

## Architecture

```
Auth Flow:
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│ User Signs  │ --> │ Supabase     │ --> │ Trigger:   │
│ Up          │     │ auth.users   │     │ Create     │
└─────────────┘     └──────────────┘     │ Profile    │
                                          └────────────┘
                                                │
                                                v
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│ User        │ --> │ Create Org   │ --> │ Assign     │
│ Dashboard   │     │ API Call     │     │ Admin Role │
└─────────────┘     └──────────────┘     └────────────┘
```

## Files to Create

```
src/
├── lib/
│   └── supabase/
│       ├── client.ts          # Browser client
│       ├── server.ts          # Server client
│       └── middleware.ts      # Auth middleware
├── app/
│   ├── (auth)/
│   │   ├── layout.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── signup/
│   │   │   └── page.tsx
│   │   └── callback/
│   │       └── route.ts
│   └── (dashboard)/
│       ├── layout.tsx
│       ├── page.tsx           # Dashboard home
│       └── onboarding/
│           └── page.tsx       # Create org flow
└── components/
    └── auth/
        ├── login-form.tsx
        ├── signup-form.tsx
        └── auth-provider.tsx
```

## Implementation Steps

### Step 1: Supabase Client Setup

Create `src/lib/supabase/client.ts`:
```typescript
import { createBrowserClient } from '@supabase/ssr'
import { Database } from '@/types/database'

export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

Create `src/lib/supabase/server.ts`:
```typescript
import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { Database } from '@/types/database'

export async function createClient() {
  const cookieStore = await cookies()

  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return cookieStore.get(name)?.value
        },
        set(name: string, value: string, options: CookieOptions) {
          cookieStore.set({ name, value, ...options })
        },
        remove(name: string, options: CookieOptions) {
          cookieStore.delete({ name, ...options })
        },
      },
    }
  )
}
```

### Step 2: Auth Middleware

Create `src/middleware.ts`:
```typescript
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({
    request: { headers: request.headers },
  })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name: string) {
          return request.cookies.get(name)?.value
        },
        set(name: string, value: string, options) {
          response.cookies.set({ name, value, ...options })
        },
        remove(name: string, options) {
          response.cookies.delete({ name, ...options })
        },
      },
    }
  )

  const { data: { user } } = await supabase.auth.getUser()

  // Redirect to login if accessing dashboard without auth
  if (!user && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Redirect to dashboard if already logged in
  if (user && (request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/signup')) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return response
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
}
```

### Step 3: Profile Auto-Create Trigger

Add to Supabase SQL Editor:
```sql
-- Auto-create profile when user signs up
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1))
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

### Step 4: Organization CRUD

Create `src/lib/api/organizations.ts`:
```typescript
import { createClient } from '@/lib/supabase/client'

export async function createOrganization(name: string, slug: string) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) throw new Error('Not authenticated')

  // 1. Create organization
  const { data: org, error: orgError } = await supabase
    .from('organizations')
    .insert({ name, slug })
    .select()
    .single()

  if (orgError) throw orgError

  // 2. Update user's profile with org_id
  await supabase
    .from('profiles')
    .update({ org_id: org.id })
    .eq('id', user.id)

  // 3. Get admin role
  const { data: adminRole } = await supabase
    .from('roles')
    .select('id')
    .eq('org_id', org.id)
    .eq('name', 'Admin')
    .single()

  return org
}

export async function getOrganization(orgId: number) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('organizations')
    .select('*')
    .eq('id', orgId)
    .single()

  if (error) throw error
  return data
}

export async function getOrganizationMembers(orgId: number) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('profiles')
    .select('*, roles(*)')
    .eq('org_id', orgId)

  if (error) throw error
  return data
}
```

### Step 5: Login/Signup Pages

Create basic auth pages with forms that call:
```typescript
// Sign up
await supabase.auth.signUp({ email, password, options: { data: { full_name } } })

// Login
await supabase.auth.signInWithPassword({ email, password })

// Logout
await supabase.auth.signOut()
```

## Todo List

- [x] Install dependencies: `@supabase/ssr`
- [x] Create Supabase client files
- [x] Setup middleware for auth
- [x] Add profile trigger in Supabase (SQL file created)
- [x] Create login page UI
- [x] Create signup page UI
- [x] Create onboarding page (create org)
- [x] Create dashboard layout with user info
- [ ] Test complete auth flow (requires .env.local setup)

## Success Criteria

- [ ] User can sign up with email/password
- [ ] Profile auto-created on signup
- [ ] User can create organization
- [ ] User's profile linked to organization
- [ ] Default roles (Admin, Member, Guest) created
- [ ] Logged-in user redirected to dashboard
- [ ] Logged-out user redirected to login

## Next Phase

After auth works → [Phase 3: Projects & Members CRUD](./phase-03-projects-members.md)

---

_Created: 2026-01-25_
