import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import Card, { CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Button from '@/components/ui/button'
import Link from 'next/link'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  if (!user) {
    redirect('/login')
  }

  // Get user profile
  const { data } = await supabase
    .from('profiles')
    .select('org_id')
    .eq('id', user.id)
    .single()

  const profile = data as { org_id: number | null } | null

  // If no profile or no organization, redirect to onboarding
  if (!profile || !profile.org_id) {
    redirect('/dashboard/onboarding')
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-text-primary mb-6">Dashboard</h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Get Started</CardTitle>
            <CardDescription>Create your first project to begin tracking issues</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/projects/new">
              <Button variant="primary" fullWidth>
                Create Project
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Projects</CardTitle>
            <CardDescription>View and manage all your projects</CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/projects">
              <Button variant="outline" fullWidth>
                View Projects
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
