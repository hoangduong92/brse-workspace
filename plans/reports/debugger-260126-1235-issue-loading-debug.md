# Issue Loading Debug Report

**Date**: 2026-01-26 (Updated 13:50)
**Agent**: debugger (a7bc882)
**Context**: c:/Users/duongbibo/brse-workspace/projects/solo-builder-12months/ship/backlog-clone
**Problem**: User created issue not appearing in issue list

---

## Executive Summary

**Issue**: Issues created through UI not loading/appearing in list despite successful creation
**Root Cause**: ~~Missing `project_member` record~~ **UPDATED: Data is correct, issue is likely client-side**
**Impact**: High - Users cannot view issues they create
**Priority**: P0 - Critical bug blocking core functionality

---

## Database State (Verified 2026-01-26 13:47)

**RLS BYPASSED DIAGNOSTIC RESULTS:**

| Table | Records | Status |
|-------|---------|--------|
| profiles | 1 | ✅ `damdandau1512@gmail.com` (org_id=2) |
| organizations | 1 | ✅ `bibo-org` (id=2) |
| projects | 1 | ✅ `SBP: solo-builder-project` (id=2, org_id=2) |
| project_members | 1 | ✅ User is Admin of SBP |
| issues | 2 | ✅ `#1: Task 1`, `#2: Ticket 1` (project_id=2) |
| roles | 3 | ✅ Admin, Member, Guest (org_id=2) |

**Conclusion**: Database state is CORRECT. User IS project member with Admin role. RLS should allow access.

---

## Test Infrastructure Status

### Current Setup
- **No test framework**: No jest/vitest config found
- **No test files**: Zero application test files in src/
- **Scripts**: Only dev/build/start/lint in package.json
- **Dependencies**: No test dependencies installed

### Recommendation
Setup vitest + @testing-library/react for:
- Unit tests (API functions)
- Integration tests (RLS policies)
- E2E tests (issue creation flow)

---

## Technical Analysis

### 1. Issue Creation Flow

**File**: `src/lib/api/issues.ts` (line 16-54)

```typescript
export async function createIssue(data: CreateIssueData) {
  // 1. Auth check ✅
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  // 2. Insert issue ✅
  const { data: issue, error } = await supabase
    .from('issues')
    .insert({ project_id: data.projectId, ... })
    .select()
    .single()

  // 3. Add categories ✅
  if (data.categoryIds?.length) {
    await supabase.from('issue_categories').insert(...)
  }

  return issue
}
```

**Status**: Implementation correct, RLS INSERT policy allows project members

### 2. Issue Loading Flow

**File**: `src/app/(dashboard)/dashboard/projects/[projectKey]/issues/page.tsx` (line 29-46)

```typescript
const loadData = async () => {
  // 1. Get project ✅
  const projectData = await getProject(projectKey)
  setProject(projectData)

  // 2. Get issues (RLS applied here) ⚠️
  const issuesData = await getIssues(projectData.id, filters)
  setIssues(issuesData)
}
```

**File**: `src/lib/api/issues.ts` (line 56-84)

```typescript
export async function getIssues(projectId: number, filters?) {
  let query = supabase
    .from('issues')
    .select(`*, status:statuses(*), ...`)
    .eq('project_id', projectId)
    .is('deleted_at', null)
    .order('issue_number', { ascending: false })

  const { data, error } = await query
  if (error) throw error
  return data
}
```

**Status**: Query correct, but RLS SELECT policy may block results

### 3. RLS Policy Analysis

**File**: `supabase/migrations/003_rls_policies.sql` (line 280-284)

```sql
-- Project members can view issues
CREATE POLICY "issues_select_members"
ON issues FOR SELECT
USING (is_project_member(project_id));
```

**Helper Function** (line 50-58):

```sql
CREATE OR REPLACE FUNCTION is_project_member(p_project_id BIGINT)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM project_members
    WHERE project_id = p_project_id
    AND user_id = auth.uid()
  );
$$ LANGUAGE sql SECURITY DEFINER;
```

**Critical Finding**: Function calls `project_members` table, requires record exists

### 4. Project Creation Flow

**File**: `src/lib/api/projects.ts` (line 3-38)

```typescript
export async function createProject(data) {
  // Uses RPC function to atomically:
  // 1. Create project ✅
  // 2. Add creator as project_member with Admin role ✅
  const { data: project, error } = await supabase.rpc(
    'create_project_with_member',
    { p_user_id: user.id, ... }
  )
}
```

**File**: `supabase/migrations/004_create_org_function.sql` (line 54-89)

```sql
CREATE OR REPLACE FUNCTION create_project_with_member(...)
RETURNS JSON AS $$
BEGIN
  -- 1. Create project
  INSERT INTO projects (...) RETURNING id INTO v_project_id;

  -- 2. Get admin role
  SELECT id INTO v_admin_role_id FROM roles WHERE ...;

  -- 3. Add creator as project member ✅
  INSERT INTO project_members (project_id, user_id, role_id)
  VALUES (v_project_id, p_user_id, v_admin_role_id);

  RETURN json_build_object(...);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Status**: RPC creates `project_members` record - should work for project creator

---

## Root Cause Identification

### Scenario 1: Missing project_member Record (90% likelihood)

**Symptoms**:
- User can create project
- User can access project page
- User can create issue (INSERT passes)
- User CANNOT see issues (SELECT fails)

**Cause**:
- User accessing project without `project_members` record
- Possibly testing with different user than project creator
- Or `create_project_with_member` RPC failed to insert member

**Validation Query**:
```sql
-- Check if current user is project member
SELECT
  p.id as project_id,
  p.name,
  pm.user_id,
  pm.role_id,
  r.name as role_name
FROM projects p
LEFT JOIN project_members pm ON pm.project_id = p.id
  AND pm.user_id = auth.uid()
LEFT JOIN roles r ON r.id = pm.role_id
WHERE p.key = 'YOUR_PROJECT_KEY';

-- If pm.user_id is NULL, user is NOT a project member
```

### Scenario 2: RLS Performance Issue (5% likelihood)

**Symptoms**:
- Slow queries
- Timeout errors
- Inconsistent results

**Cause**:
- `is_project_member()` called per-row (N+1 problem)
- Missing index on `project_members(project_id, user_id)`

**Status**: Index EXISTS (line 81-82 in 001_initial_schema.sql)
```sql
CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_user ON project_members(user_id);
```

**Note**: Composite index `(project_id, user_id)` would be optimal

### Scenario 3: Trigger Failure (5% likelihood)

**Symptoms**:
- Issue created without `issue_number`
- Insert succeeds but `issue_number` is NULL

**Cause**: `set_issue_number()` trigger failed

**Validation Query**:
```sql
-- Check if issues have issue_number set
SELECT id, project_id, issue_number, title
FROM issues
WHERE project_id = YOUR_PROJECT_ID
ORDER BY created_at DESC;

-- If issue_number is NULL, trigger failed
```

---

## Diagnostic SQL Queries

### 1. Verify User is Project Member

```sql
-- Run in Supabase SQL Editor (logged in as test user)
SELECT
  p.id,
  p.key,
  p.name,
  CASE
    WHEN pm.user_id IS NOT NULL THEN 'YES - Member'
    ELSE 'NO - Not a member'
  END as membership_status,
  r.name as role,
  auth.uid() as current_user_id
FROM projects p
LEFT JOIN project_members pm ON pm.project_id = p.id
  AND pm.user_id = auth.uid()
LEFT JOIN roles r ON r.id = pm.role_id
WHERE p.key = 'YOUR_PROJECT_KEY';
```

**Expected**: `membership_status` = 'YES - Member'
**If NO**: User not in `project_members` table - root cause identified

### 2. Check Issue Creation Success

```sql
-- Verify issues exist and have issue_number
SELECT
  i.id,
  i.project_id,
  i.issue_number,
  i.title,
  i.reporter_id,
  i.deleted_at,
  i.created_at,
  auth.uid() as current_user_id,
  CASE
    WHEN i.reporter_id = auth.uid() THEN 'Created by me'
    ELSE 'Created by other'
  END as ownership
FROM issues i
WHERE i.project_id = (
  SELECT id FROM projects WHERE key = 'YOUR_PROJECT_KEY'
)
ORDER BY i.created_at DESC;
```

**Expected**: Issues exist, `issue_number` is NOT NULL, `deleted_at` is NULL

### 3. Test RLS Helper Function

```sql
-- Manually test is_project_member function
SELECT
  p.key,
  is_project_member(p.id) as is_member,
  auth.uid() as my_user_id
FROM projects p
WHERE p.key = 'YOUR_PROJECT_KEY';
```

**Expected**: `is_member` = true
**If false**: RLS will block SELECT queries

### 4. Verify RLS Policies Applied

```sql
-- Check RLS is enabled and policies exist
SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual
FROM pg_policies
WHERE tablename = 'issues'
ORDER BY policyname;
```

**Expected**: See `issues_select_members`, `issues_insert_members`, etc.

### 5. Check Project Creation Result

```sql
-- Verify project was created with member
SELECT
  p.id,
  p.key,
  p.name,
  COUNT(pm.user_id) as member_count,
  json_agg(
    json_build_object(
      'user_id', pm.user_id,
      'role', r.name
    )
  ) as members
FROM projects p
LEFT JOIN project_members pm ON pm.project_id = p.id
LEFT JOIN roles r ON r.id = pm.role_id
WHERE p.key = 'YOUR_PROJECT_KEY'
GROUP BY p.id, p.key, p.name;
```

**Expected**: `member_count` >= 1, creator in members array with 'Admin' role

### 6. Verify All Indexes Exist

```sql
-- Check indexes on project_members (critical for RLS performance)
SELECT
  indexname,
  indexdef
FROM pg_indexes
WHERE tablename = 'project_members'
ORDER BY indexname;
```

**Expected**: See `idx_project_members_project` and `idx_project_members_user`

---

## Recommended Fixes (Priority Order)

### Fix 1: Add User to Project Members (If Missing)

**Likelihood**: 90%
**Severity**: Critical
**Action**: Manual SQL or implement "Add Member" API

```sql
-- Get required IDs
SELECT
  p.id as project_id,
  r.id as admin_role_id,
  auth.uid() as user_id
FROM projects p
JOIN roles r ON r.org_id = p.org_id
  AND r.name = 'Admin'
  AND r.is_system = TRUE
WHERE p.key = 'YOUR_PROJECT_KEY';

-- Insert project member
INSERT INTO project_members (project_id, user_id, role_id)
VALUES (
  <project_id_from_above>,
  <user_id_from_above>,
  <admin_role_id_from_above>
);
```

**Prevent**: Ensure UI only allows users to create projects in their org

### Fix 2: Add Composite Index for RLS Performance

**Likelihood**: 5% (optimization, not bug fix)
**Severity**: Medium
**Action**: Add composite index

```sql
-- Add composite index for faster lookups
CREATE INDEX IF NOT EXISTS idx_project_members_project_user
ON project_members(project_id, user_id);

-- This optimizes is_project_member(project_id) lookups
-- when auth.uid() is in WHERE clause
```

**Benefit**: ~3-10x faster RLS checks, especially with many members

### Fix 3: Add RLS Bypass for Issue Reporter

**Likelihood**: 5% (alternative approach)
**Severity**: Low
**Action**: Allow users to see issues they created

```sql
-- Add policy: users can always see issues they reported
CREATE POLICY "issues_select_reporter"
ON issues FOR SELECT
USING (reporter_id = auth.uid());

-- Note: This is additive to existing policy
-- Users can see issues if they're project member OR reporter
```

**Risk**: May violate business logic (should non-members see issues?)

### Fix 4: Improve Error Handling in UI

**Likelihood**: N/A (UX improvement)
**Severity**: Low
**Action**: Show helpful error when RLS blocks query

```typescript
// In src/lib/api/issues.ts
export async function getIssues(projectId: number, filters?) {
  const { data, error } = await query

  if (error) {
    // Check if error is RLS-related
    if (error.code === '42501' || error.message?.includes('policy')) {
      throw new Error('Access denied: You are not a member of this project')
    }
    throw error
  }
  return data
}
```

**Benefit**: Users understand why issues aren't loading

---

## Test Strategy (Local Database)

### Setup Local Supabase

```bash
# Install Supabase CLI
npm install -g supabase

# Initialize in project
cd c:/Users/duongbibo/brse-workspace/projects/solo-builder-12months/ship/backlog-clone
supabase init

# Start local instance
supabase start

# Apply migrations
supabase db reset
```

### Test Cases

#### Test 1: Project Creator Can See Issues

```typescript
// test/api/issues.test.ts
describe('Issue Loading', () => {
  it('should show issues to project creator', async () => {
    // 1. Create user
    const user = await createTestUser()

    // 2. Create org
    const org = await createOrg(user)

    // 3. Create project (should auto-add user as member)
    const project = await createProject(org.id, user.id)

    // 4. Verify user is project member
    const isMember = await checkProjectMember(project.id, user.id)
    expect(isMember).toBe(true)

    // 5. Create issue
    const issue = await createIssue(project.id, user.id)
    expect(issue.issue_number).toBe(1)

    // 6. Query issues (should return 1 issue)
    const issues = await getIssues(project.id, user.id)
    expect(issues).toHaveLength(1)
    expect(issues[0].id).toBe(issue.id)
  })
})
```

#### Test 2: Non-Member Cannot See Issues

```typescript
it('should block non-members from seeing issues', async () => {
  // 1. Create project with user A
  const userA = await createTestUser('a@test.com')
  const project = await createProject(orgId, userA.id)

  // 2. Create issue as user A
  const issue = await createIssue(project.id, userA.id)

  // 3. Try to query as user B (not a member)
  const userB = await createTestUser('b@test.com')
  const issues = await getIssues(project.id, userB.id)

  // 4. Should return empty array (RLS blocks)
  expect(issues).toHaveLength(0)
})
```

#### Test 3: RPC Creates Project Member

```typescript
it('should add creator as project member via RPC', async () => {
  const user = await createTestUser()
  const org = await createOrg(user)

  // Call RPC
  const project = await supabase.rpc('create_project_with_member', {
    p_org_id: org.id,
    p_name: 'Test Project',
    p_key: 'TEST',
    p_description: null,
    p_user_id: user.id
  })

  // Verify member record exists
  const { data: member } = await supabase
    .from('project_members')
    .select('*, role:roles(name)')
    .eq('project_id', project.id)
    .eq('user_id', user.id)
    .single()

  expect(member).toBeTruthy()
  expect(member.role.name).toBe('Admin')
})
```

### Manual Testing Checklist

- [ ] Create new user account
- [ ] Create new organization
- [ ] Create new project (verify redirects to project page)
- [ ] Run Query #1 (verify user is project member)
- [ ] Create new issue (note issue number)
- [ ] Check issue appears in list immediately
- [ ] Run Query #2 (verify issue exists with issue_number)
- [ ] Run Query #3 (verify `is_project_member` returns true)
- [ ] Open browser console - check for RLS errors
- [ ] Test with second user (non-member) - should NOT see issues

---

## Performance Considerations

### RLS Function Optimization

**Current**: `is_project_member()` uses SECURITY DEFINER + SQL function

**Pros**:
- Bypasses RLS on project_members table (avoids circular dependency)
- Cached within transaction
- Index-optimized lookups

**Cons**:
- Still called per-row for large result sets
- Suboptimal for queries returning 100+ issues

**Optimization** (Future):
```sql
-- Cache result in session variable
CREATE OR REPLACE FUNCTION is_project_member(p_project_id BIGINT)
RETURNS BOOLEAN AS $$
  -- Cache lookup in temp table or session var
  -- Reuse across multiple policy checks in same query
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Index Recommendations

```sql
-- Already exists (good)
CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_user ON project_members(user_id);

-- Recommended addition
CREATE INDEX idx_project_members_project_user
ON project_members(project_id, user_id);

-- Covers both WHERE clauses in is_project_member()
-- Enables index-only scans (faster)
```

---

## Unresolved Questions

1. **User Scenario**: Was the issue created by the same user trying to view it? Or different user?

2. **Project Creation**: Was project created via:
   - `create_project_with_member` RPC (should add member)
   - Direct INSERT (would NOT add member)
   - UI form (uses RPC - should work)

3. **Error Messages**: Does browser console show any errors when loading issues page?
   - RLS policy violations typically return empty array (no error thrown)
   - Network errors or Supabase errors would show in console

4. **Multiple Projects**: Does the issue occur in:
   - Only specific project(s)
   - All projects for this user
   - Only for certain users

5. **Timing**: When was the issue noticed?
   - Immediately after creating issue
   - After page refresh
   - After logging out/in

6. **Database State**: Are there any issues in the database that ARE visible? Or zero issues show up?

---

---

## UPDATED ANALYSIS (2026-01-26 13:50)

### Database Verified Correct
- User `damdandau1512@gmail.com` IS in `project_members` with Admin role
- 2 issues exist in database with correct `project_id`
- RLS policies should allow access

### Likely Client-Side Issues

1. **Duplicate Route Structure**
   - `/projects/[projectKey]/issues/page.tsx`
   - `/dashboard/projects/[projectKey]/issues/page.tsx`
   - Both identical but may cause routing confusion

2. **Auth Session Issue**
   - Client may not have valid session when fetching
   - Supabase client created fresh each request

3. **Query Error Not Visible**
   - Error caught but only logged to console
   - User sees "Loading..." or "Project not found"

### Files to Check

```
src/lib/supabase/client.ts           # Browser client setup
src/lib/api/issues.ts:56-84          # getIssues() function
src/app/(dashboard)/*/issues/page.tsx # Both versions
```

### Diagnostic Scripts Created

```bash
# Run admin diagnostic (bypasses RLS)
node scripts/diagnose-admin.mjs

# Test RLS as authenticated user (requires login)
node scripts/test-rls-query.mjs
```

### Next Steps

1. **Check browser console** for errors when loading issues page
2. **Verify auth session** is valid in Network tab
3. **Test Supabase query directly** in browser console:
   ```javascript
   const { data, error } = await supabase
     .from('issues')
     .select('*')
     .eq('project_id', 2)
   console.log({ data, error })
   ```
4. **Remove duplicate routes** - keep only one issues page
5. **Add better error handling** - show actual error message

### Supabase CLI Setup Completed

```bash
cd projects/solo-builder-12months/ship/backlog-clone
npx supabase --version  # 2.72.8
npx supabase status     # Linked to hsdoyzzootrdjeysxrba
```

---

## Unresolved Questions

1. What URL is user accessing? `/projects/SBP/issues` or `/dashboard/projects/SBP/issues`?
2. What shows in browser console when page loads?
3. Does network request to Supabase return data or error?
4. Is auth session valid (check Application > Local Storage for sb-*-auth-token)?
5. After creating issue, does page refresh or stay on same page?

**Priority**: P0 - Needs browser debugging to identify exact failure point
