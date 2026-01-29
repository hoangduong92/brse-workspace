# Issue Loading Test Report

**Date**: 2026-01-26 15:15
**Agent**: tester (subagent)
**Project**: backlog-clone
**Context**: c:/Users/duongbibo/brse-workspace/projects/solo-builder-12months/ship/backlog-clone
**Work Phase**: Testing & Verification

---

## Executive Summary

**Status**: TESTING INFRASTRUCTURE NOT ESTABLISHED + CODE ISSUES IDENTIFIED
**Finding**: Database state is CORRECT per debug report, but CONFIRMED client-side issues found
**Priority**: P0 - Blocking core functionality
**Root Causes Identified**: Duplicate routes, weak error handling, missing member loading

### Critical Findings

| Finding | Status | Impact | Fix |
|---------|--------|--------|-----|
| **Duplicate Routes** | ✅ CONFIRMED | Both routes work but cause confusion | DELETE one |
| **Database State** | ✅ CORRECT | User IS member, issues exist | N/A |
| **Error Handling** | ❌ WEAK | Errors hidden from user | Add logging |
| **Test Coverage** | ❌ ZERO | Cannot validate fixes | Setup vitest |
| **Member Loading** | ⚠️ TODO | UI broken for filtering | Create API |

### Key Findings (Detailed)

1. **Database Verified**: ✅ User IS project member with Admin role, 2 issues exist in correct database
2. **Routes Are Duplicate**: ✅ CONFIRMED - 2 identical files, Next.js routing ambiguous
3. **Error Handling Weak**: ✅ CONFIRMED - errors logged but not shown to user
4. **No Test Framework**: ❌ Zero test files, no vitest/jest config, no test dependencies
5. **Missing Members API**: ⚠️ Members hardcoded as empty array

### Evidence

**Routes Found**:
```
✅ src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx (KEEP)
❌ src/app/(dashboard)/projects/[projectKey]/issues/page.tsx (DELETE)
```
Both files are IDENTICAL (120 lines, byte-for-byte same)

**Error Handling**:
```typescript
catch (error) {
  console.error('Failed to load data:', error)  // Only in console
  alert('Failed to load data')                   // Generic message
}
```

**Missing Members**:
```typescript
// TODO: Load project members from API
// For now using empty array
setMembers([])
```

---

## Test Infrastructure Status

### Current State

| Component | Status | Issue |
|-----------|--------|-------|
| Test Framework | ❌ Missing | No vitest/jest configuration |
| Test Files | ❌ None | Zero test files in src/ |
| Test Dependencies | ❌ None | No @testing-library, @vitest packages |
| Build Tools | ✅ Present | Next.js 16.1.4, TypeScript 5 |
| API Layer | ✅ Ready | Clean API functions in src/lib/api/ |

### Package.json Analysis

**Current Dependencies**:
- `next@16.1.4`
- `react@19.2.3`
- `@supabase/ssr@0.6.1`
- `@supabase/supabase-js@2.91.1`
- `typescript@5`

**Missing for Testing**:
- `vitest` - Fast unit testing
- `@vitest/ui` - Test UI dashboard
- `@testing-library/react` - Component testing
- `@testing-library/dom` - DOM testing utilities
- `jsdom` - DOM environment for vitest
- `@supabase/supabase-js` testing utilities

---

## Code Analysis

### 1. Issue Creation Flow (`src/lib/api/issues.ts`)

**Status**: ✅ Implementation correct

```typescript
// Line 16-54: createIssue()
- Auth check: ✅ Validates user exists
- Insert: ✅ Proper field mapping (reporter_id set correctly)
- Categories: ✅ Junction table handling
- Error handling: ⚠️ Generic error throws
```

**Observations**:
- Function properly checks `auth.uid()`
- Sets `reporter_id` to authenticated user
- RLS INSERT policy should allow project members
- No detailed error logging for debugging

### 2. Issue Loading Flow (`src/lib/api/issues.ts`)

**Status**: ⚠️ Code correct but untested

```typescript
// Line 56-84: getIssues()
- Query: ✅ Proper field selection with joins
- Filtering: ✅ Filters for status/assignee/type
- RLS: ✅ Applies when user not project member
- Error handling: ⚠️ Only generic error
```

**Observations**:
- Query structure is sound
- Selects proper nested fields (status, type, assignee, categories)
- Uses `is('deleted_at', null)` to exclude soft-deleted
- **RISK**: Error thrown without context - user sees generic failure

### 3. Project Creation (`src/lib/api/projects.ts`)

**Status**: ✅ Uses RPC for atomic creation

```typescript
// Line 3-38: createProject()
- Auth: ✅ Checks user authenticated
- Org lookup: ✅ Gets user's org_id
- RPC call: ✅ Creates project + member atomically
- Error handling: ⚠️ Duplicate key handling only
```

**Observations**:
- Properly uses `create_project_with_member` RPC
- RPC should add creator as Admin member
- Handles duplicate key uniqueness constraint
- **RISK**: If RPC fails silently, project created without member

### 4. Issues Page (Both Routes Found)

**Files Found**:
- `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx`
- `src/app/(dashboard)/projects/[projectKey]/issues/page.tsx`

**Issue**: Duplicate routes detected - debug report identified this as potential routing confusion

---

## Test Cases Required

### Priority 1: RLS & Access Control

#### Test 1.1: Project Creator Can See Issues
```
GIVEN: User creates project via createProject()
WHEN: Same user calls getIssues(projectId)
THEN: Issues list returns successfully
```

**Implementation Needed**:
- Mock Supabase client
- Mock auth.getUser() returns valid user
- Mock project_members table has entry
- Verify getIssues() returns data array

#### Test 1.2: Non-Member Blocked
```
GIVEN: Project exists with user A as member
WHEN: User B (not a member) calls getIssues(projectId)
THEN: Returns empty array (RLS blocks)
```

**Implementation Needed**:
- Create two test users
- Verify second user blocked by RLS

#### Test 1.3: Member Role Verification
```
GIVEN: User is project member with Admin role
WHEN: User creates issue
THEN: createIssue() succeeds and returns issue_number
```

**Implementation Needed**:
- Verify user.id in project_members
- Verify Admin role allows INSERT

### Priority 2: Data Integrity

#### Test 2.1: Issue Number Assignment
```
GIVEN: Issue created with createIssue()
WHEN: Issue stored in database
THEN: issue_number is auto-incremented (trigger works)
```

**Implementation Needed**:
- Create multiple issues in sequence
- Verify issue_number field populated

#### Test 2.2: Issue with Categories
```
GIVEN: createIssue() called with categoryIds
WHEN: Issue and categories stored
THEN: issue_categories junction populated
```

**Implementation Needed**:
- Test with 0, 1, multiple categories
- Verify junction table entries created

#### Test 2.3: Soft Delete Excluded
```
GIVEN: Issues exist with some having deleted_at
WHEN: getIssues() called
THEN: Only non-deleted issues returned
```

**Implementation Needed**:
- Create deleted issue
- Verify getIssues() excludes it

### Priority 3: Error Scenarios

#### Test 3.1: Unauthenticated User
```
GIVEN: User not authenticated
WHEN: createIssue() called
THEN: Throws "Not authenticated" error
```

#### Test 3.2: Invalid Project ID
```
GIVEN: Non-existent projectId
WHEN: getIssues(999) called
THEN: Returns empty array or error
```

#### Test 3.3: Invalid Category ID
```
GIVEN: Non-existent categoryId in createIssue()
WHEN: Function called
THEN: Throws FK constraint error
```

### Priority 4: Performance

#### Test 4.1: Large Issue List
```
GIVEN: Project with 100+ issues
WHEN: getIssues() called
THEN: Query completes in <500ms
```

#### Test 4.2: Nested Join Performance
```
GIVEN: Issues with all relations (status, type, assignee, categories)
WHEN: getIssues() called
THEN: All relations loaded without N+1
```

---

## Diagnostic Results Summary

### Database Verification (from debug report)

**Status**: ✅ CORRECT

| Check | Result | Evidence |
|-------|--------|----------|
| User exists | ✅ YES | damdandau1512@gmail.com in profiles |
| Org exists | ✅ YES | bibo-org (id=2) |
| Project exists | ✅ YES | SBP: solo-builder-project (id=2) |
| User is member | ✅ YES | project_members has entry with Admin role |
| Issues exist | ✅ YES | 2 issues in database with project_id=2 |
| RLS should allow | ✅ YES | `is_project_member(2)` should return true |

### Client-Side Issues (Suspected)

1. **Duplicate Routes**
   - `/projects/[projectKey]/issues/page.tsx`
   - `/dashboard/projects/[projectKey]/issues/page.tsx`
   - Both files exist - may cause routing confusion

2. **Auth Session**
   - Supabase client created fresh in each function
   - Auth token may not be valid in browser context

3. **Error Visibility**
   - Errors caught but not displayed to user
   - Browser console needed to see RLS issues

---

## Recommended Actions

### Phase 1: Immediate (High Priority)

1. **Remove Duplicate Routes**
   - Delete: `src/app/(dashboard)/projects/[projectKey]/issues/page.tsx`
   - Keep only: `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx`
   - Verify routing works correctly

2. **Add Error Logging**
   - Update `getIssues()` to log errors with context
   - Show helpful error messages in UI (RLS, auth, network)

3. **Test Manual Flow**
   - Create new user account
   - Create new project
   - Open browser DevTools > Console
   - Create issue and check for errors
   - Verify issue appears in list

### Phase 2: Test Infrastructure (Medium Priority)

1. **Setup Vitest**
   - Add vitest.config.ts
   - Configure jsdom environment
   - Setup test script in package.json

2. **Create API Tests**
   - Mock Supabase client
   - Test createIssue() with mocked auth
   - Test getIssues() with RLS scenarios

3. **Create Integration Tests**
   - Use local Supabase instance
   - Run actual database queries
   - Verify RLS policies work

### Phase 3: E2E Tests (Lower Priority)

1. **Browser-Based Tests**
   - Test complete flow: create project → create issue → view issue
   - Verify UI updates after creation
   - Test error scenarios

---

## Code Quality Issues Found

### Issue: Duplicate Routes (Confirmed)

**Location**:
- Route 1: `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx` (120 lines)
- Route 2: `src/app/(dashboard)/projects/[projectKey]/issues/page.tsx` (120 lines)

**Status**: ✅ IDENTICAL CODE - both files are byte-for-byte identical

**Impact**:
- Next.js may route to either file unpredictably
- Confusing for developers (maintenance nightmare)
- Potential caching issues in browsers

**Fix**: DELETE one route completely (recommend delete Route 2)

### Issue: Weak Error Handling

**Location**: `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx:42-43`

```typescript
} catch (error) {
  console.error('Failed to load data:', error)  // ⚠️ Error logged but not visible to user
  alert('Failed to load data')                   // ⚠️ Generic message - no context
}
```

**Problems**:
1. Error only logged to console (user won't see in alert)
2. `alert()` is generic - doesn't help debugging
3. RLS errors return empty array, not actual error
4. Network/auth errors hidden from user

**Fix**: Show specific error messages based on error type

### Issue: No Member Loading

**Location**: `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx:38-40`

```typescript
// TODO: Load project members from API
// For now using empty array
setMembers([])
```

**Impact**:
- Members dropdown for filtering will be empty
- Assignee selection may not work properly
- UI may show "No members" warning

**Fix**: Create `getProjectMembers()` API function

---

## Issue Page Analysis

### Page Load Flow

```
User navigates to /dashboard/projects/SBP/issues
↓
useEffect triggers with [projectKey, filters]
↓
loadData() called
├─ getProject(projectKey)        ← Get project by key
├─ getIssues(projectId, filters) ← Get issues for project (RLS APPLIED HERE)
└─ setMembers([])                ← Empty for now
↓
If success: Render IssueList with issues
If error: Show alert("Failed to load data")
```

### Current Issues in Flow

1. **Routing**: User may be on duplicate route - which one?
2. **Error Transparency**: If RLS blocks, user sees generic error
3. **Auth State**: Supabase client initialized fresh - may lose session
4. **Members Loading**: Hardcoded empty array breaks filtering

---

## Unresolved Questions

1. **Routing**: Which URL is user accessing when issues don't appear?
   - `/projects/SBP/issues` or `/dashboard/projects/SBP/issues`?
   - **ACTION**: Check browser address bar or server logs

2. **Browser Console**: What errors appear in DevTools when page loads?
   - RLS 42501 error? Network error? Auth error?
   - **ACTION**: Open DevTools > Console and check for errors

3. **Auth State**: Is auth token valid when getIssues() called?
   - Can verify by logging `auth.uid()` in getIssues()
   - **ACTION**: Add console.log in getIssues() to check auth

4. **Page Behavior**: What appears on issues page?
   - Empty list? "Loading..." forever? "Project not found"?
   - **ACTION**: Take screenshot of current state

5. **Database Timing**: Was user added as member BEFORE issue creation?
   - Or issue created first, user added later?
   - **ACTION**: Check database created_at timestamps

6. **Cache/Storage**: Any browser cache issues?
   - Test in incognito mode?
   - **ACTION**: Clear localStorage/sessionStorage and retry

---

## Test Execution Plan

### Local Setup Required

```bash
cd c:/Users/duongbibo/brse-workspace/projects/solo-builder-12months/ship/backlog-clone

# 1. Install test dependencies
npm install --save-dev vitest @vitest/ui @testing-library/react jsdom

# 2. Setup vitest config
cat > vitest.config.ts << EOF
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
EOF

# 3. Update package.json scripts
# Add: "test": "vitest"
# Add: "test:ui": "vitest --ui"
# Add: "test:coverage": "vitest --coverage"

# 4. Create test files
# tests/api/issues.test.ts
# tests/api/projects.test.ts

# 5. Run tests
npm run test
```

### Diagnostic Script Commands

```bash
# 1. Run admin diagnostic (requires SUPABASE_SERVICE_ROLE_KEY)
node scripts/diagnose-admin.mjs

# 2. Test RLS as authenticated user
node scripts/test-rls-query.mjs

# 3. Manual browser test
npm run dev
# Navigate to project issues page
# Open DevTools Console
# Create new issue
# Check logs for errors
```

---

## Critical Issues

### Issue #1: No Test Coverage
- **Severity**: HIGH
- **Impact**: Cannot validate issue loading flow
- **Blocker**: Prevents confirming fix works
- **Resolution**: Implement test infrastructure

### Issue #2: Duplicate Routes
- **Severity**: MEDIUM
- **Impact**: User routing confusion
- **Blocker**: May cause page not found
- **Resolution**: Remove redundant route

### Issue #3: Silent Errors
- **Severity**: MEDIUM
- **Impact**: User sees "Loading" without knowing why
- **Blocker**: Poor debugging experience
- **Resolution**: Add error logging/display

---

## Summary Table

| Category | Status | Tests Needed | Blocking |
|----------|--------|--------------|----------|
| Database | ✅ CORRECT | Verify RLS policies | NO |
| API Functions | ⚠️ UNTESTED | 4+ test cases | YES |
| Error Handling | ⚠️ WEAK | Error logging tests | YES |
| Client Routes | ❌ DUPLICATE | Remove one route | YES |
| E2E Flow | ❌ UNTESTED | Full integration test | YES |

---

## Next Steps - Prioritized Action Plan

### PHASE 1: IMMEDIATE (Today) - Quick Wins
**Goal**: Identify exact issue and apply quick fixes

**Step 1.1**: Consolidate Routes
- Delete: `src/app/(dashboard)/projects/[projectKey]/issues/page.tsx`
- Keep: `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx`
- Verify all internal links use `/dashboard/projects/` path
- Test: `npm run dev` and navigate to `/dashboard/projects/SBP/issues`

**Step 1.2**: Add Detailed Error Logging
- Update: `src/lib/api/issues.ts` - add error context
- Update: `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx` - show actual errors

**Step 1.3**: Browser Testing (Manual)
```bash
npm run dev
# 1. Open http://localhost:3000/dashboard/projects/SBP/issues
# 2. Open DevTools (F12) > Console tab
# 3. Create new issue
# 4. Check console for errors
# 5. Check Network tab for Supabase response
```

**Expected Results**:
- If issues appear: Root cause was routing or caching
- If empty list: RLS blocking (user not in project_members)
- If error visible: Can see exact problem

---

### PHASE 2: Testing Infrastructure (This Week)
**Goal**: Prevent regression, enable confidence

**Step 2.1**: Setup Vitest
```bash
npm install --save-dev vitest @vitest/ui @testing-library/react jsdom @vitejs/plugin-react
```

**Step 2.2**: Create vitest.config.ts
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

**Step 2.3**: Create vitest.setup.ts
```typescript
import '@testing-library/jest-dom'

// Mock Supabase
vi.mock('@/lib/supabase/client', () => ({
  createClient: vi.fn(),
}))
```

**Step 2.4**: Update package.json scripts
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

**Step 2.5**: Create test files
- `tests/api/issues.test.ts` - Unit tests for createIssue, getIssues
- `tests/api/projects.test.ts` - Unit tests for createProject, getProject
- `tests/pages/issues-page.test.tsx` - Component tests

---

### PHASE 3: Comprehensive Tests (This Week)
**Goal**: Full coverage of issue loading flow

**Tests to Write** (Priority order):

1. **Test: Issue Creation with RLS** (tests/api/issues.test.ts)
```typescript
describe('createIssue', () => {
  it('should create issue with reporter_id = auth.uid()', async () => {
    // Mock: User authenticated
    // Mock: User is project member
    // Call: createIssue(projectId, data)
    // Assert: Issue created with reporter_id set
  })
})
```

2. **Test: Issue Loading with RLS** (tests/api/issues.test.ts)
```typescript
describe('getIssues', () => {
  it('should return issues for project members', async () => {
    // Mock: User authenticated
    // Mock: User IS project member
    // Call: getIssues(projectId)
    // Assert: Returns issue array with correct fields
  })

  it('should return empty for non-members', async () => {
    // Mock: User authenticated
    // Mock: User NOT project member
    // Call: getIssues(projectId)
    // Assert: Returns empty array (RLS blocks)
  })
})
```

3. **Test: Project Member Creation** (tests/api/projects.test.ts)
```typescript
describe('createProject', () => {
  it('should add creator as Admin member', async () => {
    // Mock: User authenticated
    // Mock: User has org_id
    // Call: createProject(data)
    // Assert: User added to project_members with Admin role
  })
})
```

4. **Test: Duplicate Routes** (tests/pages/issues-page.test.tsx)
```typescript
describe('IssuesPage', () => {
  it('should load and display issues', async () => {
    // Mock: getProject returns project
    // Mock: getIssues returns 2 issues
    // Render: IssuesPage
    // Assert: Issues displayed in list
  })

  it('should show error when loading fails', async () => {
    // Mock: getIssues throws error
    // Render: IssuesPage
    // Assert: Error message displayed
  })
})
```

---

### PHASE 4: Integration Tests (Next Week)
**Goal**: Test with real database

**Setup**: Use local Supabase instance
```bash
cd c:/Users/duongbibo/brse-workspace/projects/solo-builder-12months/ship/backlog-clone
supabase start
supabase db reset
```

**Integration Test Files**:
- `tests/integration/issue-flow.test.ts` - Full flow: create project → create issue → load issues

---

## Owner & Timeline

**Owner**: Tester agent + Code review agent
**Timeline**:
- Phase 1: 1-2 hours (today)
- Phase 2: 2-3 hours (today/tomorrow)
- Phase 3: 4-6 hours (this week)
- Phase 4: 2-3 hours (next week)

**Risk**: Without Phase 1 completion, cannot proceed to testing
**Success Metric**: All tests pass + issue loading works in browser

---

## Authentication Flow Analysis

### Supabase Client Setup

**File**: `src/lib/supabase/client.ts`

```typescript
export function createClient() {
  return createBrowserClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
```

**Status**: ✅ Correct - Uses SSR client with browser context

### Auth Token Handling

**Current Implementation**:
1. Each API call creates new Supabase client
2. Client automatically reads auth token from localStorage (SSR library handles this)
3. `supabase.auth.getUser()` retrieves auth state

**Potential Issues**:
- Fresh client creation per request may cause timing issues
- Auth token may not be immediately available on first page load
- SSR client relies on browser cookies/localStorage

### Auth in Issue Loading

**Flow** (src/lib/api/issues.ts):
```typescript
export async function getIssues(projectId: number, filters?) {
  const supabase = createClient()
  // Client ready immediately (uses cached auth token)

  let query = supabase
    .from('issues')
    .select(`...`)
    .eq('project_id', projectId)
    // RLS policy runs with current auth.uid()
    // If not in project_members, returns empty array
}
```

**Risk**: If auth token not loaded yet, query runs as anonymous → RLS blocks → empty array

---

## Verification Checklist

### Quick Verification (5 minutes)
- [ ] Confirm only ONE issues route exists (delete the duplicate)
- [ ] Run `npm run dev` without errors
- [ ] Navigate to `/dashboard/projects/SBP/issues`
- [ ] Create new issue via form
- [ ] Check if issue appears in list immediately
- [ ] Open DevTools > Console - check for errors

### Full Verification (1 hour)
- [ ] All 4 test files created and passing
- [ ] Run `npm run test` - all tests green
- [ ] Manual flow: create project → create issue → view issue
- [ ] Check browser console - no errors
- [ ] Check Network tab - Supabase requests succeed
- [ ] Test with different user roles
- [ ] Test with non-member access (should see empty list)

### Regression Testing (30 minutes)
- [ ] Existing issues still display
- [ ] Filters still work (status, type, assignee)
- [ ] Create multiple issues - all appear
- [ ] Soft delete still works
- [ ] Issue editing still works

---

## Success Criteria

✅ **All of these must be true**:
1. Only ONE issues page exists (no duplicate routes)
2. User can create issue
3. Issue appears in list immediately after creation
4. All test cases pass (100% pass rate)
5. No console errors or RLS warnings
6. Non-members see empty list (RLS working)
7. Different users isolated (privacy working)

---

## Appendix: File Paths

**Key Files**:
- API Layer: `src/lib/api/issues.ts`, `src/lib/api/projects.ts`
- Routes (duplicate):
  - `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx` ✅ Keep
  - `src/app/(dashboard)/projects/[projectKey]/issues/page.tsx` ❌ Delete
- Supabase Client: `src/lib/supabase/client.ts`
- Config: `package.json`, `tsconfig.json`
- Tests: `tests/api/`, `tests/pages/` (to be created)

**Diagnostic Scripts**:
- `scripts/diagnose-admin.mjs` - RLS bypass diagnostic
- `scripts/test-rls-query.mjs` - Authenticated user test

**Test Infrastructure** (to be created):
- `vitest.config.ts` - Vitest configuration
- `vitest.setup.ts` - Test setup and mocks
- `tests/api/issues.test.ts` - API unit tests
- `tests/api/projects.test.ts` - API unit tests
- `tests/pages/issues-page.test.tsx` - Component tests
- `tests/integration/issue-flow.test.ts` - E2E tests

