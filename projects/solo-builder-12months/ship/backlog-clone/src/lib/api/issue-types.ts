import { createClient } from '@/lib/supabase/client'
import { Database } from '@/types/database'

type IssueType = Database['public']['Tables']['issue_types']['Row']
type IssueTypeInsert = Database['public']['Tables']['issue_types']['Insert']
type IssueTypeUpdate = Database['public']['Tables']['issue_types']['Update']

export async function createIssueType(projectId: number, data: {
  name: string
  color?: string
  icon?: string
}) {
  const supabase = createClient()

  const { data: issueType, error } = await supabase
    .from('issue_types')
    .insert({
      project_id: projectId,
      name: data.name,
      color: data.color || '#6B7280',
      icon: data.icon || null,
    } as IssueTypeInsert)
    .select()
    .single()

  if (error) throw error
  return issueType as IssueType
}

export async function getIssueTypes(projectId: number) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('issue_types')
    .select('*')
    .eq('project_id', projectId)
    .order('created_at', { ascending: true })

  if (error) throw error
  return data as IssueType[]
}

export async function updateIssueType(
  id: number,
  updates: {
    name?: string
    color?: string
    icon?: string | null
  }
) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('issue_types')
    .update(updates as IssueTypeUpdate)
    .eq('id', id)
    .select()
    .single()

  if (error) throw error
  return data as IssueType
}

export async function deleteIssueType(id: number) {
  const supabase = createClient()

  // Check if issue type is in use
  const { data: issues } = await supabase
    .from('issues')
    .select('id')
    .eq('type_id', id)
    .limit(1)

  if (issues && issues.length > 0) {
    throw new Error('Cannot delete issue type that is in use by issues')
  }

  const { error } = await supabase
    .from('issue_types')
    .delete()
    .eq('id', id)

  if (error) throw error
}
