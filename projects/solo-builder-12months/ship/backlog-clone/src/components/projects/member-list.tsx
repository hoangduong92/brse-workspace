'use client'

import { useEffect, useState } from 'react'
import { getProjectMembers, removeProjectMember } from '@/lib/api/members'
import { Database } from '@/types/database'

type ProjectMember = {
  id: number
  project_id: number
  user_id: string
  role_id: number | null
  created_at: string
  user: Database['public']['Tables']['profiles']['Row']
  role: Database['public']['Tables']['roles']['Row'] | null
}

interface MemberListProps {
  projectId: number
}

export function MemberList({ projectId }: MemberListProps) {
  const [members, setMembers] = useState<ProjectMember[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadMembers()
  }, [projectId])

  async function loadMembers() {
    try {
      const data = await getProjectMembers(projectId)
      setMembers(data as ProjectMember[])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load members')
    } finally {
      setLoading(false)
    }
  }

  async function handleRemoveMember(userId: string) {
    if (!confirm('Are you sure you want to remove this member?')) return

    try {
      await removeProjectMember(projectId, userId)
      setMembers(prev => prev.filter(m => m.user_id !== userId))
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to remove member')
    }
  }

  if (loading) {
    return <div className="text-gray-500">Loading members...</div>
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-600">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-gray-900">Project Members</h3>
      <div className="border border-gray-200 rounded-lg divide-y">
        {members.map((member) => (
          <div key={member.id} className="p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-gray-600">
                  {member.user.full_name?.[0]?.toUpperCase() || member.user.email[0].toUpperCase()}
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-900">
                  {member.user.full_name || member.user.email}
                </p>
                <p className="text-sm text-gray-500">{member.role?.name || 'No role'}</p>
              </div>
            </div>
            <button
              onClick={() => handleRemoveMember(member.user_id)}
              className="text-sm text-red-600 hover:text-red-700"
            >
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
