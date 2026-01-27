'use client'

import { useState, useEffect } from 'react'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/lib/api/categories'
import { Database } from '@/types/database'

type Category = Database['public']['Tables']['categories']['Row']

interface CategoryManagerProps {
  projectId: number
}

export function CategoryManager({ projectId }: CategoryManagerProps) {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [newCategory, setNewCategory] = useState({ name: '', allow_multiple: false })
  const [editData, setEditData] = useState({ name: '', allow_multiple: false })

  useEffect(() => {
    loadCategories()
  }, [projectId])

  async function loadCategories() {
    try {
      const data = await getCategories(projectId)
      setCategories(data)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to load categories')
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate() {
    if (!newCategory.name.trim()) return

    try {
      const created = await createCategory(projectId, newCategory)
      setCategories([...categories, created])
      setNewCategory({ name: '', allow_multiple: false })
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create category')
    }
  }

  async function handleUpdate(id: number) {
    if (!editData.name.trim()) return

    try {
      const updated = await updateCategory(id, editData)
      setCategories(categories.map(c => c.id === id ? updated : c))
      setEditingId(null)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to update category')
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this category?')) return

    try {
      await deleteCategory(id)
      setCategories(categories.filter(c => c.id !== id))
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to delete category')
    }
  }

  function startEdit(category: Category) {
    setEditingId(category.id)
    setEditData({ name: category.name, allow_multiple: category.allow_multiple })
  }

  if (loading) {
    return <div className="text-gray-500">Loading categories...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Categories</h3>

        {/* Create new category */}
        <div className="flex gap-2 mb-4 p-4 bg-gray-50 rounded-lg">
          <input
            type="text"
            placeholder="Category name"
            value={newCategory.name}
            onChange={(e) => setNewCategory(prev => ({ ...prev, name: e.target.value }))}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <label className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg cursor-pointer">
            <input
              type="checkbox"
              checked={newCategory.allow_multiple}
              onChange={(e) => setNewCategory(prev => ({ ...prev, allow_multiple: e.target.checked }))}
              className="w-4 h-4"
            />
            <span className="text-sm">Allow Multiple</span>
          </label>
          <button
            onClick={handleCreate}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Add
          </button>
        </div>

        {/* Category list */}
        <div className="space-y-2">
          {categories.map((category) => (
            <div
              key={category.id}
              className="flex items-center gap-2 p-3 bg-white border border-gray-200 rounded-lg"
            >
              {editingId === category.id ? (
                <>
                  <input
                    type="text"
                    value={editData.name}
                    onChange={(e) => setEditData(prev => ({ ...prev, name: e.target.value }))}
                    className="flex-1 px-3 py-1 border border-gray-300 rounded"
                  />
                  <label className="flex items-center gap-2 px-3 py-1">
                    <input
                      type="checkbox"
                      checked={editData.allow_multiple}
                      onChange={(e) => setEditData(prev => ({ ...prev, allow_multiple: e.target.checked }))}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">Multiple</span>
                  </label>
                  <button
                    onClick={() => handleUpdate(category.id)}
                    className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    className="px-3 py-1 bg-gray-400 text-white rounded hover:bg-gray-500"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <>
                  <span className="flex-1 font-medium">{category.name}</span>
                  {category.allow_multiple && (
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                      Multiple
                    </span>
                  )}
                  <button
                    onClick={() => startEdit(category)}
                    className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(category.id)}
                    className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          ))}
        </div>

        {categories.length === 0 && (
          <p className="text-gray-500 text-center py-8">No categories yet. Add one above.</p>
        )}
      </div>
    </div>
  )
}
