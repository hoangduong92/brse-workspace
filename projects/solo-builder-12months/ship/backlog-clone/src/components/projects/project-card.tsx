'use client'

import Link from 'next/link'
import { Database } from '@/types/database'

type Project = Database['public']['Tables']['projects']['Row']

interface ProjectCardProps {
  project: Project
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link
      href={`/projects/${project.key}`}
      className="block p-6 border border-gray-200 rounded-lg hover:border-blue-500 transition-colors bg-white"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded flex items-center justify-center">
            <span className="text-sm font-semibold text-blue-600">
              {project.key}
            </span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{project.name}</h3>
            <p className="text-sm text-gray-500">{project.key}</p>
          </div>
        </div>
      </div>
      {project.description && (
        <p className="text-sm text-gray-600 mt-2 line-clamp-2">
          {project.description}
        </p>
      )}
    </Link>
  )
}
