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
