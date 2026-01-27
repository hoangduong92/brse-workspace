/**
 * Test RLS query as authenticated user
 */

import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://hsdoyzzootrdjeysxrba.supabase.co'
const ANON_KEY = 'sb_publishable_OwCwzfHnBIFO4BfC2yscFw_ASGnGNSI'

const supabase = createClient(SUPABASE_URL, ANON_KEY)

async function testAsUser() {
  console.log('=== TEST RLS AS AUTHENTICATED USER ===\n')

  // Get current session (should be none if not logged in)
  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    console.log('❌ No active session')
    console.log('\nTo test RLS, login first:\n')
    console.log('1. Run the Next.js app: npm run dev')
    console.log('2. Login at http://localhost:3000/login')
    console.log('3. Open browser DevTools > Application > Local Storage')
    console.log('4. Find sb-*-auth-token and copy the access_token\n')
    return
  }

  console.log(`✅ Logged in as: ${session.user.email}\n`)

  // Test project query
  console.log('Testing projects query...')
  const { data: projects, error: projErr } = await supabase
    .from('projects')
    .select('*')

  if (projErr) {
    console.log(`   ❌ Error: ${projErr.message}`)
  } else {
    console.log(`   ✅ ${projects?.length || 0} projects visible`)
  }

  // Test issues query for project SBP
  console.log('\nTesting issues query for project SBP...')
  const { data: project } = await supabase
    .from('projects')
    .select('id')
    .eq('key', 'SBP')
    .single()

  if (!project) {
    console.log('   ❌ Project SBP not found or blocked by RLS')
    return
  }

  const { data: issues, error: issErr } = await supabase
    .from('issues')
    .select(`
      *,
      status:statuses(*),
      type:issue_types(*),
      assignee:profiles(*),
      categories:issue_categories(category:categories(*))
    `)
    .eq('project_id', project.id)
    .is('deleted_at', null)
    .order('issue_number', { ascending: false })

  if (issErr) {
    console.log(`   ❌ Error: ${issErr.message}`)
    console.log(`   Code: ${issErr.code}`)
    console.log(`   Details: ${issErr.details}`)
  } else {
    console.log(`   ✅ ${issues?.length || 0} issues returned`)
    issues?.forEach(i => {
      console.log(`      - #${i.issue_number}: ${i.title}`)
    })
  }
}

testAsUser().catch(console.error)
