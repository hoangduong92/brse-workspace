# Code Review Report: Backlog Clone MVP

**Date:** 2026-01-25
**Reviewer:** code-reviewer agent
**Work Context:** c:\Users\duongbibo\brse-workspace\projects\solo-builder-12months\ship\backlog-clone

---

## Code Review Summary

### Scope
- Files reviewed: 59 TypeScript files
- Core focus areas:
  - `src/lib/api/*` (8 API modules)
  - `src/lib/supabase/*` (2 client modules)
  - `src/middleware.ts` (auth middleware)
  - `supabase/migrations/*` (3 SQL migrations)
- Review focus: Security, architecture, TypeScript quality
- Build status: ✅ Passes compilation

### Overall Assessment
Code quality is **good** with strong RLS implementation and clean architecture. TypeScript usage is solid with no `any` types found. Build compiles without errors. Several security concerns and architectural improvements identified.

---

## Critical Issues

### 1. **RLS Helper Function Logic Error** (CRITICAL)
**File:** `supabase/migrations/003_rls_policies.sql:36-47`

```sql
CREATE OR REPLACE FUNCTION is_org_admin(p_org_id BIGINT)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM profiles p
    JOIN project_members pm ON pm.user_id = p.id
    JOIN roles r ON r.id = pm.role_id
    WHERE p.id = auth.uid()
    AND p.org_id = p_org_id  -- ❌ WRONG: checks profile.org_id = parameter
    AND r.name = 'Admin'
    AND r.is_system = TRUE
  );
$$ LANGUAGE sql SECURITY DEFINER;
```

**Problem:** Logic joins `project_members` but checks `p.org_id = p_org_id` instead of role org. This means org-level admin checks fail if user is not in a project, even if they're org admin.

**Impact:** Organization admins cannot create organizations, projects, or perform org-level operations unless they're also in a project with admin role.

**Fix:**
```sql
CREATE OR REPLACE FUNCTION is_org_admin(p_org_id BIGINT)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM profiles p
    JOIN roles r ON r.org_id = p.org_id
    WHERE p.id = auth.uid()
    AND p.org_id = p_org_id
    AND r.name = 'Admin'
    AND r.is_system = TRUE
  );
$$ LANGUAGE sql SECURITY DEFINER;
```

### 2. **Organization Creation Without RLS Check** (CRITICAL)
**File:** `src/lib/api/organizations.ts:3-35`

**Problem:** `createOrganization()` allows ANY authenticated user to create organizations without checking if they're admin. RLS policy at line 88-90 checks `is_org_admin(id)` but new org doesn't exist yet, so check always fails.

**Impact:** Either nobody can create orgs (RLS blocks), or first user creates org but can't become admin.

**Recommendation:**
1. Create org-creation trigger that auto-assigns creator as admin
2. Or use service role key for org creation + profile update in transaction
3. Update RLS policy to allow inserts by authenticated users, then auto-grant admin via trigger

### 3. **Missing Auth Verification in API Functions** (HIGH)
**Files:** Multiple API modules

Several functions check `user` but don't verify project/org membership before operations:

- `organizations.ts:62-74` - `updateOrganization()` - no auth check
- `organizations.ts:76-85` - `deleteOrganization()` - no auth check
- `projects.ts:88-111` - `updateProject()` - no auth check
- `projects.ts:113-122` - `deleteProject()` - no auth check

**Problem:** While RLS policies protect at database level, client-side functions should fail fast with clear error messages before hitting database.

**Recommendation:** Add user auth + membership checks at function level:
```typescript
export async function updateOrganization(orgId: number, updates: {...}) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  // Verify user is org member
  const { data: profile } = await supabase
    .from('profiles')
    .select('org_id')
    .eq('id', user.id)
    .single()

  if (profile?.org_id !== orgId) {
    throw new Error('Not authorized')
  }

  // ... rest of function
}
```

---

## High Priority Findings

### 4. **Race Condition in Issue Number Generation** (HIGH)
**File:** `supabase/migrations/001_initial_schema.sql:249-262`

```sql
CREATE OR REPLACE FUNCTION set_issue_number()
RETURNS TRIGGER AS $$
BEGIN
  SELECT COALESCE(MAX(issue_number), 0) + 1
  INTO NEW.issue_number
  FROM issues
  WHERE project_id = NEW.project_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Problem:** Concurrent inserts can generate duplicate issue numbers. `MAX + 1` pattern is not atomic.

**Fix:** Use sequence or `FOR UPDATE` lock:
```sql
CREATE OR REPLACE FUNCTION set_issue_number()
RETURNS TRIGGER AS $$
BEGIN
  SELECT COALESCE(MAX(issue_number), 0) + 1
  INTO NEW.issue_number
  FROM issues
  WHERE project_id = NEW.project_id
  FOR UPDATE;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 5. **Missing Error Handling in Server Components** (HIGH)
**File:** `src/lib/supabase/server.ts:17-28`

```typescript
set(name: string, value: string, options: CookieOptions) {
  try {
    cookieStore.set({ name, value, ...options })
  } catch {
    // Handle cookie setting error in Server Components
  }
}
```

**Problem:** Silent error swallowing. Auth session may fail to persist without user knowing.

**Recommendation:** Log errors for debugging:
```typescript
set(name: string, value: string, options: CookieOptions) {
  try {
    cookieStore.set({ name, value, ...options })
  } catch (error) {
    console.error('[Supabase SSR] Failed to set cookie:', error)
    // Re-throw in development
    if (process.env.NODE_ENV === 'development') throw error
  }
}
```

### 6. **Soft Delete Not Enforced in Queries** (HIGH)
**File:** `src/lib/api/issues.ts:56-84`

`getIssues()` correctly filters `is('deleted_at', null)` at line 73, but `getIssue()` at line 86 does NOT check soft delete status.

**Impact:** Deleted issues can be accessed directly via URL.

**Fix:** Add filter to `getIssue()`:
```typescript
.is('deleted_at', null)
```

### 7. **Environment Variables Not Validated** (MEDIUM)
**Files:** `src/lib/supabase/client.ts`, `server.ts`, `middleware.ts`

All use non-null assertion `!` on env vars without runtime validation.

**Recommendation:** Add env validation on app startup:
```typescript
// src/lib/env.ts
function validateEnv() {
  const required = [
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY'
  ]

  const missing = required.filter(key => !process.env[key])
  if (missing.length > 0) {
    throw new Error(`Missing required env vars: ${missing.join(', ')}`)
  }
}

validateEnv()
```

---

## Medium Priority Improvements

### 8. **Inconsistent Error Messages** (MEDIUM)
Error messages vary across files:
- `'Not authenticated'` (most files)
- `'No organization'` (projects.ts:19)
- `'Project not found'` (issues.ts:96)

**Recommendation:** Standardize error messages and codes:
```typescript
// src/lib/errors.ts
export const ErrorMessages = {
  NOT_AUTHENTICATED: 'Authentication required',
  NOT_AUTHORIZED: 'Insufficient permissions',
  NOT_FOUND: (resource: string) => `${resource} not found`,
  ORG_REQUIRED: 'User must belong to an organization',
} as const
```

### 9. **Missing Input Validation** (MEDIUM)
API functions accept parameters without validation:
- Project key length/format not validated before uppercase conversion
- Email format not validated in profile creation
- Color hex codes not validated in status/type creation

**Recommendation:** Add validation layer using Zod or similar.

### 10. **SQL Injection Risk (Low)** (MEDIUM)
While Supabase client uses parameterized queries, the direct string concatenation in RLS functions uses `auth.uid()` which is safe. However, custom functions could be vulnerable if extended.

**Recommendation:** Document that all RLS functions must use parameterized patterns, never string interpolation.

### 11. **Missing Indexes on Foreign Keys** (MEDIUM)
**File:** `001_initial_schema.sql`

Some foreign keys lack indexes:
- `issues.parent_id` (line 142) - no index
- `documents.parent_id` (line 203) - no index

**Impact:** Slow queries for subtasks and nested documents.

**Recommendation:** Add indexes:
```sql
CREATE INDEX idx_issues_parent ON issues(parent_id);
CREATE INDEX idx_documents_parent ON documents(parent_id);
```

### 12. **Roles Table Permissions Not Checked** (MEDIUM)
**File:** `003_rls_policies.sql:133-141`

```sql
CREATE POLICY "roles_insert_admins"
ON roles FOR INSERT
WITH CHECK (is_org_admin(org_id));
```

**Problem:** Functions like `createProject()` query roles table but don't verify permissions JSONb structure.

**Recommendation:** Add permission checking helper function or document permission structure.

---

## Low Priority Suggestions

### 13. **TODO Comments in Production Code** (LOW)
**Files:** Multiple page components

```typescript
// TODO: Load project members from API
```

Found in:
- `src/app/(dashboard)/projects/[projectKey]/issues/[issueNumber]/page.tsx:49`
- `src/app/(dashboard)/projects/[projectKey]/issues/new/page.tsx:29`
- `src/app/(dashboard)/projects/[projectKey]/issues/page.tsx:38`

**Recommendation:** Complete member loading implementation or convert to GitHub issues.

### 14. **Unused Display Order in Categories** (LOW)
**File:** `001_initial_schema.sql:119`

Categories have `allow_multiple` field but no `display_order` like statuses have.

**Recommendation:** Add display_order if categories should be sortable.

### 15. **Hard-coded Default Values** (LOW)
Default statuses, types, colors are hard-coded in triggers. Consider making configurable via seed data or admin panel.

---

## Positive Observations

✅ **Excellent RLS Coverage** - Every table has RLS enabled with comprehensive policies
✅ **Type Safety** - No `any` types found, proper TypeScript usage throughout
✅ **Clean Architecture** - Good separation between API layer and Supabase clients
✅ **Consistent Patterns** - API functions follow similar structure across modules
✅ **Soft Delete Pattern** - Proper implementation for issues table
✅ **Audit Fields** - created_at/updated_at with triggers on all key tables
✅ **Build Quality** - Zero compilation errors, clean build process
✅ **Environment Separation** - Proper use of NEXT_PUBLIC_ prefix for client vars

---

## Recommended Actions

### Immediate (Fix Before Production)
1. Fix `is_org_admin()` function logic (Critical Issue #1)
2. Fix organization creation flow with proper RLS (Critical Issue #2)
3. Add `FOR UPDATE` lock to issue number generation (Issue #4)
4. Add deleted_at check to `getIssue()` (Issue #6)

### Short Term (Next Sprint)
5. Add auth checks to all update/delete API functions (Issue #3)
6. Improve error handling in server component cookies (Issue #5)
7. Add environment variable validation (Issue #7)
8. Add missing database indexes (Issue #11)

### Medium Term (Future Improvements)
9. Implement input validation layer with Zod
10. Standardize error messages (Issue #8)
11. Complete TODO items for member loading (Issue #13)
12. Document RLS security patterns

---

## Metrics

- **Type Coverage:** 100% (no `any` types detected)
- **Build Status:** ✅ Pass
- **Linting Issues:** 0 errors
- **Security Issues:** 2 critical, 5 high priority
- **Files with TODOs:** 3
- **Total Lines of SQL:** ~419 lines
- **Total TypeScript Files:** 59

---

## Unresolved Questions

1. **Organization Bootstrap:** How should first user become org admin? Is there a separate admin panel or CLI tool?
2. **Service Role Usage:** Should org creation use service role key to bypass RLS temporarily?
3. **Member Permissions:** What specific permissions should "Member" and "Guest" roles have beyond read/write/delete booleans?
4. **Project Key Validation:** What regex pattern should validate project keys (length, allowed chars)?
5. **Testing Strategy:** Are integration tests planned for RLS policies? Manual testing is error-prone.

---

**Review Status:** Complete
**Severity:** Fix critical issues before production deployment
**Next Steps:** Address critical and high-priority findings, then re-review RLS logic
