'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getProject, updateProject, deleteProject } from '@/lib/api/projects'
import { MemberList } from '@/components/projects/member-list'
import { Database } from '@/types/database'

type Project = Database['public']['Tables']['projects']['Row']

export default function ProjectSettingsPage() {
  const params = useParams()
  const router = useRouter()
  const projectKey = params.projectKey as string
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
  })

  useEffect(() => {
    async function loadProject() {
      try {
        const data = await getProject(projectKey)
        setProject(data)
        setFormData({
          name: data.name,
          description: data.description || '',
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load project')
      } finally {
        setLoading(false)
      }
    }

    loadProject()
  }, [projectKey])

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!project) return

    setSaving(true)
    setError(null)

    try {
      const updated = await updateProject(project.id, {
        name: formData.name,
        description: formData.description || undefined,
      })
      setProject(updated)
      alert('Project updated successfully')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update project')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!project) return
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return
    }

    try {
      await deleteProject(project.id)
      router.push('/projects')
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete project')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-gray-500">Loading settings...</div>
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
    <div className="space-y-6">
      <div className="p-6 border border-gray-200 rounded-lg bg-white">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">General Settings</h2>
        <form onSubmit={handleUpdate} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              id="name"
              required
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Key
            </label>
            <input
              type="text"
              value={project.key}
              disabled
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600 cursor-not-allowed"
            />
            <p className="text-xs text-gray-500 mt-1">Project key cannot be changed</p>
          </div>

          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>

      <div className="p-6 border border-gray-200 rounded-lg bg-white">
        <MemberList projectId={project.id} />
      </div>

      <div className="p-6 border border-red-200 rounded-lg bg-red-50">
        <h2 className="text-lg font-semibold text-red-900 mb-2">Danger Zone</h2>
        <p className="text-sm text-red-700 mb-4">
          Once you delete a project, there is no going back. Please be certain.
        </p>
        <button
          onClick={handleDelete}
          className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Delete Project
        </button>
      </div>
    </div>
  )
}
