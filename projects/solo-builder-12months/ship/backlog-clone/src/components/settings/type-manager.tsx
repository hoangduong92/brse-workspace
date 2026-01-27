'use client'

import { useState, useEffect } from 'react'
import { getIssueTypes, createIssueType, updateIssueType, deleteIssueType } from '@/lib/api/issue-types'
import { Database } from '@/types/database'

type IssueType = Database['public']['Tables']['issue_types']['Row']

interface TypeManagerProps {
  projectId: number
}

export function TypeManager({ projectId }: TypeManagerProps) {
  const [types, setTypes] = useState<IssueType[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [newType, setNewType] = useState({ name: '', color: '#6B7280' })
  const [editData, setEditData] = useState({ name: '', color: '' })

  useEffect(() => {
    loadTypes()
  }, [projectId])

  async function loadTypes() {
    try {
      const data = await getIssueTypes(projectId)
      setTypes(data)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to load issue types')
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate() {
    if (!newType.name.trim()) return

    try {
      const created = await createIssueType(projectId, {
        name: newType.name,
        color: newType.color,
      })
      setTypes([...types, created])
      setNewType({ name: '', color: '#6B7280' })
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create issue type')
    }
  }

  async function handleUpdate(id: number) {
    if (!editData.name.trim()) return

    try {
      const updated = await updateIssueType(id, {
        name: editData.name,
        color: editData.color,
      })
      setTypes(types.map(t => t.id === id ? updated : t))
      setEditingId(null)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to update issue type')
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this issue type?')) return

    try {
      await deleteIssueType(id)
      setTypes(types.filter(t => t.id !== id))
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to delete issue type')
    }
  }

  function startEdit(type: IssueType) {
    setEditingId(type.id)
    setEditData({ name: type.name, color: type.color })
  }

  if (loading) {
    return <div className="text-gray-500">Loading issue types...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Issue Types</h3>

        {/* Create new type */}
        <div className="flex gap-2 mb-4 p-4 bg-gray-50 rounded-lg">
          <input
            type="text"
            placeholder="Type name"
            value={newType.name}
            onChange={(e) => setNewType(prev => ({ ...prev, name: e.target.value }))}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="color"
            value={newType.color}
            onChange={(e) => setNewType(prev => ({ ...prev, color: e.target.value }))}
            className="w-16 h-10 border border-gray-300 rounded-lg cursor-pointer"
          />
          <button
            onClick={handleCreate}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Add
          </button>
        </div>

        {/* Type list */}
        <div className="space-y-2">
          {types.map((type) => (
            <div
              key={type.id}
              className="flex items-center gap-2 p-3 bg-white border border-gray-200 rounded-lg"
            >
              {editingId === type.id ? (
                <>
                  <input
                    type="text"
                    value={editData.name}
                    onChange={(e) => setEditData(prev => ({ ...prev, name: e.target.value }))}
                    className="flex-1 px-3 py-1 border border-gray-300 rounded"
                  />
                  <input
                    type="color"
                    value={editData.color}
                    onChange={(e) => setEditData(prev => ({ ...prev, color: e.target.value }))}
                    className="w-16 h-8 border border-gray-300 rounded cursor-pointer"
                  />
                  <button
                    onClick={() => handleUpdate(type.id)}
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
                  <div
                    className="w-6 h-6 rounded"
                    style={{ backgroundColor: type.color }}
                  />
                  <span className="flex-1 font-medium">{type.name}</span>
                  <button
                    onClick={() => startEdit(type)}
                    className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(type.id)}
                    className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          ))}
        </div>

        {types.length === 0 && (
          <p className="text-gray-500 text-center py-8">No issue types yet. Add one above.</p>
        )}
      </div>
    </div>
  )
}
