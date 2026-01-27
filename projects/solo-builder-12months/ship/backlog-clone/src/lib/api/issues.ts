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
      assignee:profiles!issues_assignee_id_fkey(*),
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
      assignee:profiles!issues_assignee_id_fkey(*),
      reporter:profiles!issues_reporter_id_fkey(*),
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
