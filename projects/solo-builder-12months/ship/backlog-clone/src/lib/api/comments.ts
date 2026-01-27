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
