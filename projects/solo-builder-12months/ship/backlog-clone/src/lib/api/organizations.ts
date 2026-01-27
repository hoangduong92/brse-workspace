import { createClient } from '@/lib/supabase/client'

export async function createOrganization(name: string, slug: string) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) throw new Error('Not authenticated')

  // Use RPC to create organization and link profile atomically
  // This bypasses RLS issues during the bootstrap process
  const { data, error } = await supabase.rpc('create_organization_with_profile', {
    p_name: name,
    p_slug: slug,
    p_user_id: user.id
  })

  if (error) {
    // Handle specific error cases
    if (error.code === '23505' || error.message?.includes('duplicate')) {
      throw new Error('Organization slug already exists. Please choose a different slug.')
    }
    throw new Error(error.message || 'Failed to create organization')
  }

  return data
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

export async function updateOrganization(orgId: number, updates: { name?: string; slug?: string }) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('organizations')
    .update(updates)
    .eq('id', orgId)
    .select()
    .single()

  if (error) throw error
  return data
}

export async function deleteOrganization(orgId: number) {
  const supabase = createClient()

  const { error } = await supabase
    .from('organizations')
    .delete()
    .eq('id', orgId)

  if (error) throw error
}
