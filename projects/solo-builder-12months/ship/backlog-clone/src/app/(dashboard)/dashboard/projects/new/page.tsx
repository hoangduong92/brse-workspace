import { CreateProjectForm } from '@/components/projects/create-project-form'
import Breadcrumbs from '@/components/layout/breadcrumbs'

export default function NewProjectPage() {
  return (
    <div>
      <Breadcrumbs
        items={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Projects', href: '/dashboard/projects' },
          { label: 'New Project' },
        ]}
        className="mb-6"
      />
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-text-primary">Create New Project</h1>
        <p className="text-text-secondary mt-1">Set up a new project for your team</p>
      </div>
      <CreateProjectForm />
    </div>
  )
}
