'use client'

import { useState } from 'react'

interface IssueFormProps {
  projectId: number
  statuses: Array<{ id: number; name: string }>
  types: Array<{ id: number; name: string }>
  members: Array<{ id: string; full_name: string | null }>
  categories: Array<{ id: number; name: string; allow_multiple: boolean }>
  onSubmit: (data: {
    title: string
    description?: string
    typeId?: number
    statusId?: number
    assigneeId?: string
    categoryIds?: number[]
    estimateHours?: number
    dueDate?: string
  }) => Promise<void>
  onCancel?: () => void
  initialData?: {
    title?: string
    description?: string
    typeId?: number
    statusId?: number
    assigneeId?: string
    categoryIds?: number[]
    estimateHours?: number
    dueDate?: string
  }
}

export function IssueForm({
  projectId,
  statuses,
  types,
  members,
  categories,
  onSubmit,
  onCancel,
  initialData
}: IssueFormProps) {
  const [title, setTitle] = useState(initialData?.title || '')
  const [description, setDescription] = useState(initialData?.description || '')
  const [typeId, setTypeId] = useState<number | undefined>(initialData?.typeId)
  const [statusId, setStatusId] = useState<number | undefined>(initialData?.statusId)
  const [assigneeId, setAssigneeId] = useState<string | undefined>(initialData?.assigneeId)
  const [categoryIds, setCategoryIds] = useState<number[]>(initialData?.categoryIds || [])
  const [estimateHours, setEstimateHours] = useState<number | undefined>(initialData?.estimateHours)
  const [dueDate, setDueDate] = useState<string | undefined>(initialData?.dueDate)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleCategoryToggle = (categoryId: number) => {
    setCategoryIds(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    setIsSubmitting(true)
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
        typeId,
        statusId,
        assigneeId,
        categoryIds: categoryIds.length > 0 ? categoryIds : undefined,
        estimateHours,
        dueDate: dueDate || undefined,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title *
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter issue title"
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter issue description"
        />
      </div>

      {/* Type and Status */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-1">
            Type
          </label>
          <select
            id="type"
            value={typeId || ''}
            onChange={(e) => setTypeId(e.target.value ? Number(e.target.value) : undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select type</option>
            {types.map((type) => (
              <option key={type.id} value={type.id}>
                {type.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status"
            value={statusId || ''}
            onChange={(e) => setStatusId(e.target.value ? Number(e.target.value) : undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select status</option>
            {statuses.map((status) => (
              <option key={status.id} value={status.id}>
                {status.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Assignee */}
      <div>
        <label htmlFor="assignee" className="block text-sm font-medium text-gray-700 mb-1">
          Assignee
        </label>
        <select
          id="assignee"
          value={assigneeId || ''}
          onChange={(e) => setAssigneeId(e.target.value || undefined)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Unassigned</option>
          {members.map((member) => (
            <option key={member.id} value={member.id}>
              {member.full_name || 'Unnamed'}
            </option>
          ))}
        </select>
      </div>

      {/* Categories */}
      {categories.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Categories
          </label>
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                type="button"
                onClick={() => handleCategoryToggle(category.id)}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  categoryIds.includes(category.id)
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Estimate and Due Date */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="estimate" className="block text-sm font-medium text-gray-700 mb-1">
            Estimate (hours)
          </label>
          <input
            type="number"
            id="estimate"
            value={estimateHours || ''}
            onChange={(e) => setEstimateHours(e.target.value ? Number(e.target.value) : undefined)}
            min="0"
            step="0.5"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="0"
          />
        </div>

        <div>
          <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
            Due Date
          </label>
          <input
            type="date"
            id="dueDate"
            value={dueDate || ''}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isSubmitting || !title.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Saving...' : 'Save Issue'}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  )
}
