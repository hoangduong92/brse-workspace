'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { getProject } from '@/lib/api/projects'
import { Database } from '@/types/database'

type Project = Database['public']['Tables']['projects']['Row'] & {
  statuses: Database['public']['Tables']['statuses']['Row'][]
  issue_types: Database['public']['Tables']['issue_types']['Row'][]
  categories: Database['public']['Tables']['categories']['Row'][]
}

export default function ProjectDashboardPage() {
  const params = useParams()
  const projectKey = params.projectKey as string
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadProject() {
      try {
        const data = await getProject(projectKey)
        setProject(data as Project)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load project')
      } finally {
        setLoading(false)
      }
    }

    loadProject()
  }, [projectKey])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-500">Loading project...</div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">{error || 'Project not found'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-100 rounded flex items-center justify-center">
              <span className="text-lg font-semibold text-blue-600">
                {project.key}
              </span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
              <p className="text-gray-600">{project.key}</p>
            </div>
          </div>
          <Link
            href={`/projects/${project.key}/settings`}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Settings
          </Link>
        </div>
        {project.description && (
          <p className="text-gray-700">{project.description}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 border border-gray-200 rounded-lg bg-white">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Statuses</h2>
          <div className="space-y-2">
            {project.statuses.length > 0 ? (
              project.statuses.map((status) => (
                <div key={status.id} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: status.color }}
                  />
                  <span className="text-sm text-gray-700">{status.name}</span>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">No statuses configured</p>
            )}
          </div>
        </div>

        <div className="p-6 border border-gray-200 rounded-lg bg-white">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Issue Types</h2>
          <div className="space-y-2">
            {project.issue_types.length > 0 ? (
              project.issue_types.map((type) => (
                <div key={type.id} className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: type.color }}
                  />
                  <span className="text-sm text-gray-700">{type.name}</span>
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">No issue types configured</p>
            )}
          </div>
        </div>

        <div className="p-6 border border-gray-200 rounded-lg bg-white">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Categories</h2>
          <div className="space-y-2">
            {project.categories.length > 0 ? (
              project.categories.map((category) => (
                <div key={category.id} className="text-sm text-gray-700">
                  {category.name}
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500">No categories configured</p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-8 p-6 border border-gray-200 rounded-lg bg-white">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="flex gap-3">
          <Link
            href={`/projects/${project.key}/issues/new`}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Issue
          </Link>
          <Link
            href={`/projects/${project.key}/issues`}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            View Issues
          </Link>
        </div>
      </div>
    </div>
  )
}
