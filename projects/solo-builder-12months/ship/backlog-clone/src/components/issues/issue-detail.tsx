'use client'

import { useState } from 'react'
import { updateIssue } from '@/lib/api/issues'
import { DynamicIcon } from '@/components/ui/dynamic-icon'

interface IssueDetailProps {
  issue: {
    id: number
    issue_number: number
    title: string
    description: string | null
    status: { id: number; name: string; color: string } | null
    type: { id: number; name: string; color: string; icon: string | null } | null
    assignee: { id: string; full_name: string | null; avatar_url: string | null } | null
    reporter: { id: string; full_name: string | null; avatar_url: string | null } | null
    estimate_hours: number | null
    actual_hours: number
    due_date: string | null
    created_at: string
    updated_at: string
  }
  projectKey: string
  statuses: Array<{ id: number; name: string }>
  types: Array<{ id: number; name: string }>
  members: Array<{ id: string; full_name: string | null }>
  onUpdate?: () => void
}

export function IssueDetail({ issue, projectKey, statuses, types, members, onUpdate }: IssueDetailProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [title, setTitle] = useState(issue.title)
  const [description, setDescription] = useState(issue.description || '')
  const [statusId, setStatusId] = useState(issue.status?.id)
  const [typeId, setTypeId] = useState(issue.type?.id)
  const [assigneeId, setAssigneeId] = useState<string | null>(issue.assignee?.id || null)
  const [isUpdating, setIsUpdating] = useState(false)

  const handleSave = async () => {
    if (!title.trim()) return

    setIsUpdating(true)
    try {
      await updateIssue(issue.id, {
        title: title.trim(),
        description: description.trim() || undefined,
        statusId,
        typeId,
        assigneeId,
      })
      setIsEditing(false)
      onUpdate?.()
    } catch (error) {
      console.error('Failed to update issue:', error)
      alert('Failed to update issue')
    } finally {
      setIsUpdating(false)
    }
  }

  const handleCancel = () => {
    setTitle(issue.title)
    setDescription(issue.description || '')
    setStatusId(issue.status?.id)
    setTypeId(issue.type?.id)
    setAssigneeId(issue.assignee?.id || null)
    setIsEditing(false)
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-3">
          {issue.type && (
            <div
              className="w-8 h-8 rounded flex items-center justify-center text-white"
              style={{ backgroundColor: issue.type.color }}
            >
              {issue.type.icon ? (
                <DynamicIcon name={issue.type.icon} fallback={issue.type.name} size={18} />
              ) : (
                issue.type.name.charAt(0)
              )}
            </div>
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-mono text-gray-500">
                {projectKey}-{issue.issue_number}
              </span>
              {!isEditing ? (
                <h1 className="text-2xl font-bold text-gray-900">{issue.title}</h1>
              ) : (
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="text-2xl font-bold border-b-2 border-blue-500 focus:outline-none px-1"
                />
              )}
            </div>
          </div>
        </div>

        {!isEditing ? (
          <button
            onClick={() => setIsEditing(true)}
            className="px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
          >
            Edit
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              disabled={isUpdating}
              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isUpdating ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={handleCancel}
              className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-4 mb-6 pb-6 border-b border-gray-200">
        <div>
          <label className="text-sm font-medium text-gray-500 block mb-1">Status</label>
          {!isEditing ? (
            issue.status && (
              <span
                className="inline-block px-3 py-1 rounded-full text-white text-sm"
                style={{ backgroundColor: issue.status.color }}
              >
                {issue.status.name}
              </span>
            )
          ) : (
            <select
              value={statusId || ''}
              onChange={(e) => setStatusId(e.target.value ? Number(e.target.value) : undefined)}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            >
              <option value="">No status</option>
              {statuses.map((status) => (
                <option key={status.id} value={status.id}>
                  {status.name}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 block mb-1">Type</label>
          {!isEditing ? (
            issue.type && (
              <span className="text-sm text-gray-900">{issue.type.name}</span>
            )
          ) : (
            <select
              value={typeId || ''}
              onChange={(e) => setTypeId(e.target.value ? Number(e.target.value) : undefined)}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            >
              <option value="">No type</option>
              {types.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 block mb-1">Assignee</label>
          {!isEditing ? (
            issue.assignee ? (
              <div className="flex items-center gap-2">
                {issue.assignee.avatar_url ? (
                  <img
                    src={issue.assignee.avatar_url}
                    alt={issue.assignee.full_name || 'User'}
                    className="w-6 h-6 rounded-full"
                  />
                ) : (
                  <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center">
                    <span className="text-xs text-gray-600">
                      {issue.assignee.full_name?.charAt(0) || '?'}
                    </span>
                  </div>
                )}
                <span className="text-sm text-gray-900">{issue.assignee.full_name}</span>
              </div>
            ) : (
              <span className="text-sm text-gray-500">Unassigned</span>
            )
          ) : (
            <select
              value={assigneeId || ''}
              onChange={(e) => setAssigneeId(e.target.value || null)}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            >
              <option value="">Unassigned</option>
              {members.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.full_name || 'Unnamed'}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label className="text-sm font-medium text-gray-500 block mb-1">Reporter</label>
          {issue.reporter && (
            <div className="flex items-center gap-2">
              {issue.reporter.avatar_url ? (
                <img
                  src={issue.reporter.avatar_url}
                  alt={issue.reporter.full_name || 'User'}
                  className="w-6 h-6 rounded-full"
                />
              ) : (
                <div className="w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center">
                  <span className="text-xs text-gray-600">
                    {issue.reporter.full_name?.charAt(0) || '?'}
                  </span>
                </div>
              )}
              <span className="text-sm text-gray-900">{issue.reporter.full_name}</span>
            </div>
          )}
        </div>

        {issue.estimate_hours !== null && (
          <div>
            <label className="text-sm font-medium text-gray-500 block mb-1">Estimate</label>
            <span className="text-sm text-gray-900">{issue.estimate_hours}h</span>
          </div>
        )}

        {issue.due_date && (
          <div>
            <label className="text-sm font-medium text-gray-500 block mb-1">Due Date</label>
            <span className="text-sm text-gray-900">
              {new Date(issue.due_date).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>

      {/* Description */}
      <div>
        <label className="text-sm font-medium text-gray-500 block mb-2">Description</label>
        {!isEditing ? (
          issue.description ? (
            <p className="text-gray-900 whitespace-pre-wrap">{issue.description}</p>
          ) : (
            <p className="text-gray-400 italic">No description</p>
          )
        ) : (
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        )}
      </div>

      {/* Timestamps */}
      <div className="mt-6 pt-6 border-t border-gray-200 text-xs text-gray-500">
        <div>Created: {new Date(issue.created_at).toLocaleString()}</div>
        <div>Updated: {new Date(issue.updated_at).toLocaleString()}</div>
      </div>
    </div>
  )
}
