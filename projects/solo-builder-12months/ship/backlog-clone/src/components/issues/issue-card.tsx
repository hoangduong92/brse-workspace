'use client'

import Link from 'next/link'
import { DynamicIcon } from '@/components/ui/dynamic-icon'

interface IssueCardProps {
  issue: {
    id: number
    issue_number: number
    title: string
    description: string | null
    status: { name: string; color: string } | null
    type: { name: string; color: string; icon: string | null } | null
    assignee: { full_name: string | null; avatar_url: string | null } | null
    due_date: string | null
  }
  projectKey: string
}

export function IssueCard({ issue, projectKey }: IssueCardProps) {
  return (
    <Link
      href={`/projects/${projectKey}/issues/${issue.issue_number}`}
      className="block p-4 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors bg-white"
    >
      <div className="flex items-start gap-3">
        {/* Type icon */}
        {issue.type && (
          <div
            className="w-6 h-6 rounded flex items-center justify-center text-white text-xs"
            style={{ backgroundColor: issue.type.color }}
          >
            {issue.type.icon ? (
              <DynamicIcon name={issue.type.icon} fallback={issue.type.name} size={14} />
            ) : (
              issue.type.name.charAt(0)
            )}
          </div>
        )}

        <div className="flex-1 min-w-0">
          {/* Issue number and title */}
          <div className="flex items-center gap-2 mb-1">
            <span className="text-sm font-mono text-gray-500">
              {projectKey}-{issue.issue_number}
            </span>
            <h3 className="font-medium text-gray-900 truncate">
              {issue.title}
            </h3>
          </div>

          {/* Description preview */}
          {issue.description && (
            <p className="text-sm text-gray-600 line-clamp-1 mb-2">
              {issue.description}
            </p>
          )}

          {/* Footer: status, assignee, due date */}
          <div className="flex items-center gap-3 text-xs">
            {issue.status && (
              <span
                className="px-2 py-1 rounded-full text-white"
                style={{ backgroundColor: issue.status.color }}
              >
                {issue.status.name}
              </span>
            )}

            {issue.assignee && (
              <div className="flex items-center gap-1">
                {issue.assignee.avatar_url ? (
                  <img
                    src={issue.assignee.avatar_url}
                    alt={issue.assignee.full_name || 'User'}
                    className="w-5 h-5 rounded-full"
                  />
                ) : (
                  <div className="w-5 h-5 rounded-full bg-gray-300 flex items-center justify-center">
                    <span className="text-xs text-gray-600">
                      {issue.assignee.full_name?.charAt(0) || '?'}
                    </span>
                  </div>
                )}
                <span className="text-gray-600">{issue.assignee.full_name}</span>
              </div>
            )}

            {issue.due_date && (
              <span className="text-gray-500">
                Due: {new Date(issue.due_date).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}
