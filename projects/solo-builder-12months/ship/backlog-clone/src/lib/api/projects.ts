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

  // Use RPC to create project and add member atomically
  const { data: project, error } = await supabase.rpc('create_project_with_member', {
    p_org_id: profile.org_id,
    p_name: data.name,
    p_key: data.key,
    p_description: data.description || null,
    p_user_id: user.id
  })

  if (error) {
    if (error.code === '23505' || error.message?.includes('duplicate')) {
      throw new Error('Project key already exists in this organization')
    }
    throw new Error(error.message || 'Failed to create project')
  }

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
  return data.map(d => d.project).filter(Boolean)
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

export async function updateProject(
  projectId: number,
  updates: {
    name?: string
    description?: string
    key?: string
  }
) {
  const supabase = createClient()

  if (updates.key) {
    updates.key = updates.key.toUpperCase()
  }

  const { data, error } = await supabase
    .from('projects')
    .update(updates)
    .eq('id', projectId)
    .select()
    .single()

  if (error) throw error
  return data
}

export async function deleteProject(projectId: number) {
  const supabase = createClient()

  const { error } = await supabase
    .from('projects')
    .delete()
    .eq('id', projectId)

  if (error) throw error
}
