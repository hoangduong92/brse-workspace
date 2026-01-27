import { createClient } from '@/lib/supabase/client'
import { Database } from '@/types/database'

type Status = Database['public']['Tables']['statuses']['Row']
type StatusInsert = Database['public']['Tables']['statuses']['Insert']
type StatusUpdate = Database['public']['Tables']['statuses']['Update']

export async function createStatus(projectId: number, data: {
  name: string
  color?: string
}) {
  const supabase = createClient()

  // Get current max display_order
  const { data: maxOrder } = await supabase
    .from('statuses')
    .select('display_order')
    .eq('project_id', projectId)
    .order('display_order', { ascending: false })
    .limit(1)
    .single()

  const newOrder = (maxOrder?.display_order ?? -1) + 1

  const { data: status, error } = await supabase
    .from('statuses')
    .insert({
      project_id: projectId,
      name: data.name,
      color: data.color || '#6B7280',
      display_order: newOrder,
    } as StatusInsert)
    .select()
    .single()

  if (error) throw error
  return status as Status
}

export async function getStatuses(projectId: number) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('statuses')
    .select('*')
    .eq('project_id', projectId)
    .order('display_order', { ascending: true })

  if (error) throw error
  return data as Status[]
}

export async function updateStatus(
  id: number,
  updates: {
    name?: string
    color?: string
  }
) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('statuses')
    .update(updates as StatusUpdate)
    .eq('id', id)
    .select()
    .single()

  if (error) throw error
  return data as Status
}

export async function deleteStatus(id: number) {
  const supabase = createClient()

  // Check if status is in use
  const { data: issues } = await supabase
    .from('issues')
    .select('id')
    .eq('status_id', id)
    .limit(1)

  if (issues && issues.length > 0) {
    throw new Error('Cannot delete status that is in use by issues')
  }

  const { error } = await supabase
    .from('statuses')
    .delete()
    .eq('id', id)

  if (error) throw error
}

export async function reorderStatuses(projectId: number, orderedIds: number[]) {
  const supabase = createClient()

  // Update display_order for each status
  const updates = orderedIds.map((id, index) =>
    supabase
      .from('statuses')
      .update({ display_order: index } as StatusUpdate)
      .eq('id', id)
      .eq('project_id', projectId)
  )

  const results = await Promise.all(updates)

  const errors = results.filter(r => r.error)
  if (errors.length > 0) {
    throw errors[0].error
  }
}
