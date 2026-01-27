import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import Sidebar from '@/components/layout/sidebar'
import Navbar from '@/components/layout/navbar'

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  // Get user profile
  const { data: profile } = await supabase
    .from('profiles')
    .select('*, organizations(*)')
    .eq('id', user.id)
    .single()

  const organizationName = profile?.organizations?.name
  const userName = profile?.full_name
  const userEmail = user.email

  return (
    <div className="min-h-screen bg-bg-secondary">
      <Sidebar organizationName={organizationName} />

      <div className="md:ml-64 min-h-screen flex flex-col">
        <Navbar
          userName={userName}
          userEmail={userEmail}
        />

        <main className="flex-1 p-4 md:p-6 lg:p-8 mb-16 md:mb-0">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
