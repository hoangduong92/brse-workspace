'use client'

import { useState } from 'react'
import { IssueCard } from './issue-card'

interface IssueListProps {
  issues: Array<{
    id: number
    issue_number: number
    title: string
    description: string | null
    status: { id: number; name: string; color: string } | null
    type: { id: number; name: string; color: string; icon: string | null } | null
    assignee: { id: string; full_name: string | null; avatar_url: string | null } | null
    due_date: string | null
  }>
  projectKey: string
  statuses: Array<{ id: number; name: string }>
  types: Array<{ id: number; name: string }>
  members: Array<{ id: string; full_name: string | null }>
  onFilterChange?: (filters: {
    statusId?: number
    typeId?: number
    assigneeId?: string
  }) => void
}

export function IssueList({ issues, projectKey, statuses, types, members, onFilterChange }: IssueListProps) {
  const [statusFilter, setStatusFilter] = useState<number | undefined>()
  const [typeFilter, setTypeFilter] = useState<number | undefined>()
  const [assigneeFilter, setAssigneeFilter] = useState<string | undefined>()

  const handleFilterChange = (newFilters: {
    statusId?: number
    typeId?: number
    assigneeId?: string
  }) => {
    onFilterChange?.(newFilters)
  }

  const handleStatusChange = (value: string) => {
    const statusId = value ? Number(value) : undefined
    setStatusFilter(statusId)
    handleFilterChange({ statusId, typeId: typeFilter, assigneeId: assigneeFilter })
  }

  const handleTypeChange = (value: string) => {
    const typeId = value ? Number(value) : undefined
    setTypeFilter(typeId)
    handleFilterChange({ statusId: statusFilter, typeId, assigneeId: assigneeFilter })
  }

  const handleAssigneeChange = (value: string) => {
    const assigneeId = value || undefined
    setAssigneeFilter(assigneeId)
    handleFilterChange({ statusId: statusFilter, typeId: typeFilter, assigneeId })
  }

  return (
    <div>
      {/* Filters */}
      <div className="mb-6 flex gap-4">
        <select
          value={statusFilter || ''}
          onChange={(e) => handleStatusChange(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">All Statuses</option>
          {statuses.map((status) => (
            <option key={status.id} value={status.id}>
              {status.name}
            </option>
          ))}
        </select>

        <select
          value={typeFilter || ''}
          onChange={(e) => handleTypeChange(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">All Types</option>
          {types.map((type) => (
            <option key={type.id} value={type.id}>
              {type.name}
            </option>
          ))}
        </select>

        <select
          value={assigneeFilter || ''}
          onChange={(e) => handleAssigneeChange(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
        >
          <option value="">All Assignees</option>
          {members.map((member) => (
            <option key={member.id} value={member.id}>
              {member.full_name || 'Unnamed'}
            </option>
          ))}
        </select>
      </div>

      {/* Issue list */}
      <div className="space-y-3">
        {issues.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No issues found
          </div>
        ) : (
          issues.map((issue) => (
            <IssueCard key={issue.id} issue={issue} projectKey={projectKey} />
          ))
        )}
      </div>
    </div>
  )
}
