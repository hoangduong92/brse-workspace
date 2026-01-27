import Link from 'next/link'
import { ProjectList } from '@/components/projects/project-list'
import Button from '@/components/ui/button'

export default function ProjectsPage() {
  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">Projects</h1>
          <p className="text-text-secondary mt-1">Manage your organization&apos;s projects</p>
        </div>
        <Link href="/dashboard/projects/new">
          <Button variant="primary">
            New Project
          </Button>
        </Link>
      </div>
      <ProjectList />
    </div>
  )
}
