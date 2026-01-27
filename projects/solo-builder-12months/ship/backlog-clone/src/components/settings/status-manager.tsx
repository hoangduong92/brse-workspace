'use client'

import { useState, useEffect } from 'react'
import { getStatuses, createStatus, updateStatus, deleteStatus, reorderStatuses } from '@/lib/api/statuses'
import { Database } from '@/types/database'

type Status = Database['public']['Tables']['statuses']['Row']

interface StatusManagerProps {
  projectId: number
}

export function StatusManager({ projectId }: StatusManagerProps) {
  const [statuses, setStatuses] = useState<Status[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [newStatus, setNewStatus] = useState({ name: '', color: '#6B7280' })
  const [editData, setEditData] = useState({ name: '', color: '' })

  useEffect(() => {
    loadStatuses()
  }, [projectId])

  async function loadStatuses() {
    try {
      const data = await getStatuses(projectId)
      setStatuses(data)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to load statuses')
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate() {
    if (!newStatus.name.trim()) return

    try {
      const created = await createStatus(projectId, newStatus)
      setStatuses([...statuses, created])
      setNewStatus({ name: '', color: '#6B7280' })
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to create status')
    }
  }

  async function handleUpdate(id: number) {
    if (!editData.name.trim()) return

    try {
      const updated = await updateStatus(id, editData)
      setStatuses(statuses.map(s => s.id === id ? updated : s))
      setEditingId(null)
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to update status')
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Delete this status?')) return

    try {
      await deleteStatus(id)
      setStatuses(statuses.filter(s => s.id !== id))
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Failed to delete status')
    }
  }

  async function moveUp(index: number) {
    if (index === 0) return

    const newOrder = [...statuses]
    const temp = newOrder[index]
    newOrder[index] = newOrder[index - 1]
    newOrder[index - 1] = temp

    setStatuses(newOrder)

    try {
      await reorderStatuses(projectId, newOrder.map(s => s.id))
    } catch (error) {
      loadStatuses() // Revert on error
      alert(error instanceof Error ? error.message : 'Failed to reorder')
    }
  }

  async function moveDown(index: number) {
    if (index === statuses.length - 1) return

    const newOrder = [...statuses]
    const temp = newOrder[index]
    newOrder[index] = newOrder[index + 1]
    newOrder[index + 1] = temp

    setStatuses(newOrder)

    try {
      await reorderStatuses(projectId, newOrder.map(s => s.id))
    } catch (error) {
      loadStatuses() // Revert on error
      alert(error instanceof Error ? error.message : 'Failed to reorder')
    }
  }

  function startEdit(status: Status) {
    setEditingId(status.id)
    setEditData({ name: status.name, color: status.color })
  }

  if (loading) {
    return <div className="text-gray-500">Loading statuses...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Statuses</h3>

        {/* Create new status */}
        <div className="flex gap-2 mb-4 p-4 bg-gray-50 rounded-lg">
          <input
            type="text"
            placeholder="New status name"
            value={newStatus.name}
            onChange={(e) => setNewStatus(prev => ({ ...prev, name: e.target.value }))}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="color"
            value={newStatus.color}
            onChange={(e) => setNewStatus(prev => ({ ...prev, color: e.target.value }))}
            className="w-16 h-10 border border-gray-300 rounded-lg cursor-pointer"
          />
          <button
            onClick={handleCreate}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Add
          </button>
        </div>

        {/* Status list */}
        <div className="space-y-2">
          {statuses.map((status, index) => (
            <div
              key={status.id}
              className="flex items-center gap-2 p-3 bg-white border border-gray-200 rounded-lg"
            >
              {editingId === status.id ? (
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
                    onClick={() => handleUpdate(status.id)}
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
                    style={{ backgroundColor: status.color }}
                  />
                  <span className="flex-1 font-medium">{status.name}</span>
                  <div className="flex gap-1">
                    <button
                      onClick={() => moveUp(index)}
                      disabled={index === 0}
                      className="px-2 py-1 text-gray-600 hover:bg-gray-100 rounded disabled:opacity-30"
                    >
                      ↑
                    </button>
                    <button
                      onClick={() => moveDown(index)}
                      disabled={index === statuses.length - 1}
                      className="px-2 py-1 text-gray-600 hover:bg-gray-100 rounded disabled:opacity-30"
                    >
                      ↓
                    </button>
                  </div>
                  <button
                    onClick={() => startEdit(status)}
                    className="px-3 py-1 text-blue-600 hover:bg-blue-50 rounded"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(status.id)}
                    className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
                  >
                    Delete
                  </button>
                </>
              )}
            </div>
          ))}
        </div>

        {statuses.length === 0 && (
          <p className="text-gray-500 text-center py-8">No statuses yet. Add one above.</p>
        )}
      </div>
    </div>
  )
}
