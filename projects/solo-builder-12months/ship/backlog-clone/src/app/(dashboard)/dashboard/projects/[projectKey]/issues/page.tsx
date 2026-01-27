'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { getProject } from '@/lib/api/projects'
import { getIssues } from '@/lib/api/issues'
import { IssueList } from '@/components/issues/issue-list'

export default function IssuesPage() {
  const params = useParams()
  const router = useRouter()
  const projectKey = params.projectKey as string

  const [project, setProject] = useState<any>(null)
  const [issues, setIssues] = useState<any[]>([])
  const [members, setMembers] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filters, setFilters] = useState<{
    statusId?: number
    typeId?: number
    assigneeId?: string
  }>({})

  useEffect(() => {
    loadData()
  }, [projectKey, filters])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const projectData = await getProject(projectKey)
      setProject(projectData)

      const issuesData = await getIssues(projectData.id, filters)
      setIssues(issuesData)

      // TODO: Load project members from API
      // For now using empty array
      setMembers([])
    } catch (error) {
      console.error('Failed to load data:', error)
      alert('Failed to load data')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Project not found</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="text-sm text-gray-500 mb-1">
            <Link href={`/projects/${projectKey}`} className="hover:underline">
              {project.name}
            </Link>
            {' / '}
            <span>Issues</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Issues</h1>
        </div>
        <Link
          href={`/projects/${projectKey}/issues/new`}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Create Issue
        </Link>
      </div>

      {/* Issue List */}
      <IssueList
        issues={issues}
        projectKey={projectKey}
        statuses={project.statuses || []}
        types={project.issue_types || []}
        members={members}
        onFilterChange={setFilters}
      />
    </div>
  )
}
