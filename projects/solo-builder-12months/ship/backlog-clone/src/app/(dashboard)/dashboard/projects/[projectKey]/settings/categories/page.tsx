'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { getProject } from '@/lib/api/projects'
import { CategoryManager } from '@/components/settings/category-manager'
import { Database } from '@/types/database'

type Project = Database['public']['Tables']['projects']['Row']

export default function CategoriesSettingsPage() {
  const params = useParams()
  const projectKey = params.projectKey as string
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadProject() {
      try {
        const data = await getProject(projectKey)
        setProject(data)
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
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-600">{error || 'Project not found'}</p>
      </div>
    )
  }

  return (
    <div className="p-6 border border-gray-200 rounded-lg bg-white">
      <CategoryManager projectId={project.id} />
    </div>
  )
}
