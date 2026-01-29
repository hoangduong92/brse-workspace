# Phase 3: Projects & Members CRUD

## Context Links

- [Phase 2: Organizations & Users](./phase-02-organizations-users.md)

## Overview

| Attribute | Value |
|-----------|-------|
| Priority | P0 - Critical |
| Status | ✅ Completed |
| Estimated | 2-3 hours |
| Depends On | Phase 2 |

Implement project creation and member management.

## Requirements

### Functional
- Admin can create project within organization
- Project has unique key (e.g., "PROJ", "BACK")
- Admin can add members to project
- Members can have different roles per project
- Default statuses/types created with project

## Files to Create

```
src/
├── lib/
│   └── api/
│       ├── projects.ts
│       └── members.ts
├── app/
│   └── (dashboard)/
│       ├── projects/
│       │   ├── page.tsx           # List projects
│       │   ├── new/
│       │   │   └── page.tsx       # Create project
│       │   └── [projectKey]/
│       │       ├── page.tsx       # Project dashboard
│       │       └── settings/
│       │           └── page.tsx   # Project settings
└── components/
    └── projects/
        ├── project-list.tsx
        ├── project-card.tsx
        ├── create-project-form.tsx
        └── member-list.tsx
```

## Implementation Steps

### Step 1: Projects API

Create `src/lib/api/projects.ts`:
```typescript
import { createClient } from '@/lib/supabase/client'

export async function createProject(data: {
  name: string
  key: string
  description?: string
}) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  // Get user's org_id
  const { data: profile } = await supabase
    .from('profiles')
    .select('org_id')
    .eq('id', user.id)
    .single()

  if (!profile?.org_id) throw new Error('No organization')

  // Create project
  const { data: project, error } = await supabase
    .from('projects')
    .insert({
      org_id: profile.org_id,
      name: data.name,
      key: data.key.toUpperCase(),
      description: data.description,
    })
    .select()
    .single()

  if (error) throw error

  // Add creator as project member (Admin)
  const { data: adminRole } = await supabase
    .from('roles')
    .select('id')
    .eq('org_id', profile.org_id)
    .eq('name', 'Admin')
    .single()

  await supabase
    .from('project_members')
    .insert({
      project_id: project.id,
      user_id: user.id,
      role_id: adminRole?.id,
    })

  return project
}

export async function getProjects() {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) throw new Error('Not authenticated')

  const { data, error } = await supabase
    .from('project_members')
    .select(`
      project:projects(*)
    `)
    .eq('user_id', user.id)

  if (error) throw error
  return data.map(d => d.project)
}

export async function getProject(projectKey: string) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('projects')
    .select(`
      *,
      statuses(*),
      issue_types(*),
      categories(*)
    `)
    .eq('key', projectKey.toUpperCase())
    .single()

  if (error) throw error
  return data
}
```

### Step 2: Members API

Create `src/lib/api/members.ts`:
```typescript
import { createClient } from '@/lib/supabase/client'

export async function addProjectMember(
  projectId: number,
  userId: string,
  roleId: number
) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('project_members')
    .insert({
      project_id: projectId,
      user_id: userId,
      role_id: roleId,
    })
    .select()
    .single()

  if (error) throw error
  return data
}

export async function getProjectMembers(projectId: number) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('project_members')
    .select(`
      *,
      user:profiles(*),
      role:roles(*)
    `)
    .eq('project_id', projectId)

  if (error) throw error
  return data
}

export async function removeProjectMember(projectId: number, userId: string) {
  const supabase = createClient()

  const { error } = await supabase
    .from('project_members')
    .delete()
    .eq('project_id', projectId)
    .eq('user_id', userId)

  if (error) throw error
}

export async function updateMemberRole(
  projectId: number,
  userId: string,
  roleId: number
) {
  const supabase = createClient()

  const { error } = await supabase
    .from('project_members')
    .update({ role_id: roleId })
    .eq('project_id', projectId)
    .eq('user_id', userId)

  if (error) throw error
}
```

## Todo List

- [x] Create projects API functions
- [x] Create members API functions
- [x] Build project list page
- [x] Build create project form
- [x] Build project dashboard page
- [x] Build member management UI
- [x] Test creating project with default statuses
- [x] Test adding/removing members

## Success Criteria

- [x] User can create project with unique key
- [x] Default statuses, types auto-created
- [x] Creator auto-added as Admin
- [x] Can add org members to project
- [x] Can change member roles
- [x] Can remove members

## Next Phase

After projects work → [Phase 4: Issues & Comments CRUD](./phase-04-issues-comments.md)

---

_Created: 2026-01-25_
