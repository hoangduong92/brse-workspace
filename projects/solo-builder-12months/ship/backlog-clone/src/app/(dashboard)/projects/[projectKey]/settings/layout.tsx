'use client'

import { usePathname, useParams } from 'next/navigation'
import Link from 'next/link'

const settingsMenuItems = [
  { label: 'General', href: '' },
  { label: 'Statuses', href: '/statuses' },
  { label: 'Issue Types', href: '/types' },
  { label: 'Categories', href: '/categories' },
]

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const params = useParams()
  const pathname = usePathname()
  const projectKey = params.projectKey as string
  const basePath = `/projects/${projectKey}/settings`

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Project Settings</h1>
        <p className="text-gray-600 mt-1">Manage project configuration and custom fields</p>
      </div>

      <div className="flex gap-8">
        {/* Sidebar Navigation */}
        <nav className="w-56 flex-shrink-0">
          <div className="sticky top-8 space-y-1">
            {settingsMenuItems.map((item) => {
              const href = `${basePath}${item.href}`
              const isActive = pathname === href ||
                (item.href === '' && pathname === basePath)

              return (
                <Link
                  key={item.href}
                  href={href}
                  className={`block px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border-l-2 border-blue-600'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  {item.label}
                </Link>
              )
            })}
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 min-w-0">
          {children}
        </main>
      </div>
    </div>
  )
}
