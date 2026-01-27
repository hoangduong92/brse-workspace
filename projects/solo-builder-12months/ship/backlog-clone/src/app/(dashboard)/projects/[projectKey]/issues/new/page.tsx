'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { getProject } from '@/lib/api/projects'
import { createIssue } from '@/lib/api/issues'
import { IssueForm } from '@/components/issues/issue-form'

export default function NewIssuePage() {
  const params = useParams()
  const router = useRouter()
  const projectKey = params.projectKey as string

  const [project, setProject] = useState<any>(null)
  const [members, setMembers] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [projectKey])

  const loadData = async () => {
    try {
      setIsLoading(true)
      const projectData = await getProject(projectKey)
      setProject(projectData)

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

  const handleSubmit = async (data: {
    title: string
    description?: string
    typeId?: number
    statusId?: number
    assigneeId?: string
    categoryIds?: number[]
    estimateHours?: number
    dueDate?: string
  }) => {
    try {
      const issue = await createIssue({
        projectId: project.id,
        ...data,
      })
      router.push(`/projects/${projectKey}/issues/${issue.issue_number}`)
    } catch (error) {
      console.error('Failed to create issue:', error)
      alert('Failed to create issue')
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
    <div className="container mx-auto px-6 py-8 max-w-3xl">
      {/* Header */}
      <div className="mb-8">
        <div className="text-sm text-gray-500 mb-1">
          <Link href={`/projects/${projectKey}`} className="hover:underline">
            {project.name}
          </Link>
          {' / '}
          <Link href={`/projects/${projectKey}/issues`} className="hover:underline">
            Issues
          </Link>
          {' / '}
          <span>New</span>
        </div>
        <h1 className="text-3xl font-bold text-gray-900">Create Issue</h1>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <IssueForm
          projectId={project.id}
          statuses={project.statuses || []}
          types={project.issue_types || []}
          members={members}
          categories={project.categories || []}
          onSubmit={handleSubmit}
          onCancel={() => router.push(`/projects/${projectKey}/issues`)}
        />
      </div>
    </div>
  )
}
