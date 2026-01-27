import { createClient } from '@/lib/supabase/client'
import { Database } from '@/types/database'

type Category = Database['public']['Tables']['categories']['Row']
type CategoryInsert = Database['public']['Tables']['categories']['Insert']
type CategoryUpdate = Database['public']['Tables']['categories']['Update']

export async function createCategory(projectId: number, data: {
  name: string
  allow_multiple?: boolean
}) {
  const supabase = createClient()

  const { data: category, error } = await supabase
    .from('categories')
    .insert({
      project_id: projectId,
      name: data.name,
      allow_multiple: data.allow_multiple ?? false,
    } as CategoryInsert)
    .select()
    .single()

  if (error) throw error
  return category as Category
}

export async function getCategories(projectId: number) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('categories')
    .select('*')
    .eq('project_id', projectId)
    .order('created_at', { ascending: true })

  if (error) throw error
  return data as Category[]
}

export async function updateCategory(
  id: number,
  updates: {
    name?: string
    allow_multiple?: boolean
  }
) {
  const supabase = createClient()

  const { data, error } = await supabase
    .from('categories')
    .update(updates as CategoryUpdate)
    .eq('id', id)
    .select()
    .single()

  if (error) throw error
  return data as Category
}

export async function deleteCategory(id: number) {
  const supabase = createClient()

  // Check if category is in use
  const { data: issueCats } = await supabase
    .from('issue_categories')
    .select('id')
    .eq('category_id', id)
    .limit(1)

  if (issueCats && issueCats.length > 0) {
    throw new Error('Cannot delete category that is in use by issues')
  }

  const { error } = await supabase
    .from('categories')
    .delete()
    .eq('id', id)

  if (error) throw error
}
