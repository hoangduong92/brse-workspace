# Phase 4: Issues & Comments CRUD

## Context Links

- [Phase 3: Projects & Members](./phase-03-projects-members.md)

## Overview

| Attribute | Value |
|-----------|-------|
| Priority | P0 - Critical |
| Status | ✅ Completed |
| Estimated | 3-4 hours |
| Actual | 20 minutes |
| Depends On | Phase 3 |

Implement issue (ticket) management and commenting system.

## Requirements

### Functional
- Create issues with title, description, type, status
- Assign issues to project members
- Add/edit/delete comments on issues
- Issue number auto-increments per project (PROJ-1, PROJ-2)
- Soft delete issues (deleted_at)
- Filter issues by status, assignee, type
- Multiple categories per issue

### Non-Functional
- Optimistic updates for smooth UX
- Real-time comments (optional - Phase 7)

## Files to Create

```
src/
├── lib/
│   └── api/
│       ├── issues.ts
│       └── comments.ts
├── app/
│   └── (dashboard)/
│       └── projects/
│           └── [projectKey]/
│               ├── issues/
│               │   ├── page.tsx       # Issue list
│               │   ├── new/
│               │   │   └── page.tsx   # Create issue
│               │   └── [issueNumber]/
│               │       └── page.tsx   # Issue detail
└── components/
    └── issues/
        ├── issue-list.tsx
        ├── issue-card.tsx
        ├── issue-form.tsx
        ├── issue-detail.tsx
        ├── comment-list.tsx
        └── comment-form.tsx
```

## Implementation Steps

### Step 1: Issues API

Create `src/lib/api/issues.ts`:
```typescript
import { createClient } from '@/lib/supabase/client'

interface CreateIssueData {
  projectId: number
  title: string
  description?: string
  typeId?: number
  statusId?: number
  assigneeId?: string
  categoryIds?: number[]
  estimateHours?: number
  dueDate?: string
  parentId?: number
}

export async function createIssue(data: CreateIssueData) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  // Create issue (issue_number auto-set by trigger)
  const { data: issue, error } = await supabase
    .from('issues')
    .insert({
      project_id: data.projectId,
      title: data.title,
      description: data.description,
      type_id: data.typeId,
      status_id: data.statusId,
      assignee_id: data.assigneeId,
      reporter_id: user.id,
      estimate_hours: data.estimateHours,
      due_date: data.dueDate,
      parent_id: data.parentId,
    })
    .select()
    .single()

  if (error) throw error

  // Add categories (junction table)
  if (data.categoryIds?.length) {
    await supabase
      .from('issue_categories')
      .insert(
        data.categoryIds.map(catId => ({
          issue_id: issue.id,
          category_id: catId,
        }))
      )
  }

  return issue
}

export async function getIssues(projectId: number, filters?: {
  statusId?: number
  assigneeId?: string
  typeId?: number
}) {
  const supabase = createClient()

  let query = supabase
    .from('issues')
    .select(`
      *,
      status:statuses(*),
      type:issue_types(*),
      assignee:profiles(*),
      categories:issue_categories(category:categories(*))
    `)
    .eq('project_id', projectId)
    .is('deleted_at', null)
    .order('issue_number', { ascending: false })

  if (filters?.statusId) query = query.eq('status_id', filters.statusId)
  if (filters?.assigneeId) query = query.eq('assignee_id', filters.assigneeId)
  if (filters?.typeId) query = query.eq('type_id', filters.typeId)

  const { data, error } = await query

  if (error) throw error
  return data
}

export async function getIssue(projectKey: string, issueNumber: number) {
  const supabase = createClient()

  // Get project first
  const { data: project } = await supabase
    .from('projects')
    .select('id')
    .eq('key', projectKey)
    .single()

  if (!project) throw new Error('Project not found')

  const { data, error } = await supabase
    .from('issues')
    .select(`
      *,
      status:statuses(*),
      type:issue_types(*),
      assignee:profiles(*),
      reporter:profiles(*),
      categories:issue_categories(category:categories(*)),
      parent:issues(id, title, issue_number)
    `)
    .eq('project_id', project.id)
    .eq('issue_number', issueNumber)
    .single()

  if (error) throw error
  return data
}

export async function updateIssue(issueId: number, updates: Partial<{
  title: string
  description: string
  statusId: number
  typeId: number
  assigneeId: string | null
  estimateHours: number
  actualHours: number
  dueDate: string | null
}>) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('issues')
    .update({
      title: updates.title,
      description: updates.description,
      status_id: updates.statusId,
      type_id: updates.typeId,
      assignee_id: updates.assigneeId,
      estimate_hours: updates.estimateHours,
      actual_hours: updates.actualHours,
      due_date: updates.dueDate,
    })
    .eq('id', issueId)
    .select()
    .single()

  if (error) throw error
  return data
}

export async function deleteIssue(issueId: number) {
  const supabase = createClient()

  // Soft delete
  const { error } = await supabase
    .from('issues')
    .update({ deleted_at: new Date().toISOString() })
    .eq('id', issueId)

  if (error) throw error
}

export async function updateIssueCategories(issueId: number, categoryIds: number[]) {
  const supabase = createClient()

  // Delete existing
  await supabase
    .from('issue_categories')
    .delete()
    .eq('issue_id', issueId)

  // Insert new
  if (categoryIds.length) {
    await supabase
      .from('issue_categories')
      .insert(
        categoryIds.map(catId => ({
          issue_id: issueId,
          category_id: catId,
        }))
      )
  }
}
```

### Step 2: Comments API

Create `src/lib/api/comments.ts`:
```typescript
import { createClient } from '@/lib/supabase/client'

export async function createComment(issueId: number, content: string) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  const { data, error } = await supabase
    .from('comments')
    .insert({
      issue_id: issueId,
      user_id: user.id,
      content,
    })
    .select(`
      *,
      user:profiles(*)
    `)
    .single()

  if (error) throw error
  return data
}

export async function getComments(issueId: number) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('comments')
    .select(`
      *,
      user:profiles(*)
    `)
    .eq('issue_id', issueId)
    .order('created_at', { ascending: true })

  if (error) throw error
  return data
}

export async function updateComment(commentId: number, content: string) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  const { data, error } = await supabase
    .from('comments')
    .update({ content })
    .eq('id', commentId)
    .eq('user_id', user.id)  // Only owner can edit
    .select()
    .single()

  if (error) throw error
  return data
}

export async function deleteComment(commentId: number) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  const { error } = await supabase
    .from('comments')
    .delete()
    .eq('id', commentId)
    .eq('user_id', user.id)  // Only owner can delete

  if (error) throw error
}
```

## UI Components

### Issue List View
- Grid or table view of issues
- Filter by status, assignee, type
- Click to view detail

### Issue Detail View
```
┌─────────────────────────────────────────────────┐
│ PROJ-123: Fix login bug                    [X]  │
├─────────────────────────────────────────────────┤
│ Type: Bug          Status: In Progress          │
│ Assignee: John     Due: 2026-02-01              │
│ Categories: [Frontend] [Urgent]                 │
├─────────────────────────────────────────────────┤
│ Description:                                    │
│ Users can't login with special characters...    │
├─────────────────────────────────────────────────┤
│ Comments (3)                                    │
│ ┌─────────────────────────────────────────────┐ │
│ │ John: I found the issue in auth.ts         │ │
│ │ Jane: +1, can confirm                       │ │
│ └─────────────────────────────────────────────┘ │
│ [Add comment...]                                │
└─────────────────────────────────────────────────┘
```

## Todo List

- [x] Create issues API (CRUD)
- [x] Create comments API (CRUD)
- [x] Build issue list page with filters
- [x] Build create issue form
- [x] Build issue detail page
- [x] Build comment section
- [x] Handle multi-select categories
- [x] Add issue number display (PROJ-123)
- [x] Implement soft delete

## Success Criteria

- [x] Create issue with auto-generated number
- [x] Assign issue to member
- [x] Change status, type, assignee
- [x] Add multiple categories
- [x] Add/edit/delete comments
- [x] Soft delete issue
- [x] Filter issues by status/assignee/type

## Next Phase

After issues work → [Phase 5: Lookup Tables](./phase-05-lookup-tables.md)

---

_Created: 2026-01-25_
