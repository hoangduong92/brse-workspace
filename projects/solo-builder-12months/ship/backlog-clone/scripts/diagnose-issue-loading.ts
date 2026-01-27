/**
 * Diagnostic script for issue loading problem
 * Run: npx tsx scripts/diagnose-issue-loading.ts
 */

import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://hsdoyzzootrdjeysxrba.supabase.co'
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

async function diagnose() {
  console.log('=== Issue Loading Diagnostic ===\n')

  if (!SUPABASE_ANON_KEY) {
    console.error('ERROR: NEXT_PUBLIC_SUPABASE_ANON_KEY not set')
    console.log('Run: $env:NEXT_PUBLIC_SUPABASE_ANON_KEY="your-anon-key"')
    process.exit(1)
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

  // 1. Check current user
  console.log('1. Checking authentication...')
  const { data: { user }, error: authError } = await supabase.auth.getUser()
  if (authError || !user) {
    console.log('   ❌ Not authenticated')
    console.log('   → You need to be logged in to test RLS policies')
    console.log('   → Run this after logging in via the app\n')

    // Try to get data without auth (should fail with RLS)
    console.log('2. Testing RLS without auth...')
    const { data: projects, error: projErr } = await supabase.from('projects').select('*')
    console.log(`   Projects query: ${projErr ? 'Blocked (expected)' : `${projects?.length || 0} found`}`)

    const { data: issues, error: issErr } = await supabase.from('issues').select('*')
    console.log(`   Issues query: ${issErr ? 'Blocked (expected)' : `${issues?.length || 0} found`}`)

    return
  }

  console.log(`   ✅ Logged in as: ${user.email} (${user.id})\n`)

  // 2. Check profile
  console.log('2. Checking user profile...')
  const { data: profile, error: profileErr } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', user.id)
    .single()

  if (profileErr || !profile) {
    console.log('   ❌ Profile not found or blocked by RLS')
    console.log(`   Error: ${profileErr?.message || 'No data'}`)
    return
  }
  console.log(`   ✅ Profile found: org_id=${profile.org_id}\n`)

  // 3. Check projects
  console.log('3. Checking projects...')
  const { data: projects, error: projectsErr } = await supabase
    .from('projects')
    .select('*')

  if (projectsErr) {
    console.log(`   ❌ Error: ${projectsErr.message}`)
  } else if (!projects?.length) {
    console.log('   ⚠️ No projects visible (RLS may be blocking)')
  } else {
    console.log(`   ✅ ${projects.length} project(s) visible:`)
    projects.forEach(p => console.log(`      - ${p.key}: ${p.name} (id=${p.id})`))
  }
  console.log()

  // 4. Check project_members
  console.log('4. Checking project membership...')
  const { data: memberships, error: memberErr } = await supabase
    .from('project_members')
    .select(`
      *,
      project:projects(id, key, name),
      role:roles(id, name)
    `)
    .eq('user_id', user.id)

  if (memberErr) {
    console.log(`   ❌ Error: ${memberErr.message}`)
  } else if (!memberships?.length) {
    console.log('   ❌ NOT a member of any project!')
    console.log('   → This is likely the ROOT CAUSE')
    console.log('   → RLS policy requires project_members record')
  } else {
    console.log(`   ✅ Member of ${memberships.length} project(s):`)
    memberships.forEach(m => {
      const proj = m.project as any
      const role = m.role as any
      console.log(`      - ${proj?.key || 'unknown'}: role=${role?.name || 'unknown'}`)
    })
  }
  console.log()

  // 5. Check issues
  console.log('5. Checking issues...')
  const { data: issues, error: issuesErr } = await supabase
    .from('issues')
    .select(`
      id,
      project_id,
      issue_number,
      title,
      reporter_id,
      deleted_at
    `)
    .is('deleted_at', null)

  if (issuesErr) {
    console.log(`   ❌ Error: ${issuesErr.message}`)
  } else if (!issues?.length) {
    console.log('   ⚠️ No issues visible')
    console.log('   → Either no issues exist or RLS is blocking')
  } else {
    console.log(`   ✅ ${issues.length} issue(s) visible:`)
    issues.forEach(i => {
      const isReporter = i.reporter_id === user.id
      console.log(`      - #${i.issue_number}: ${i.title} ${isReporter ? '(you reported)' : ''}`)
    })
  }
  console.log()

  // 6. Summary & recommendations
  console.log('=== SUMMARY ===\n')

  const hasProfile = !!profile
  const hasProjects = (projects?.length || 0) > 0
  const hasMemberships = (memberships?.length || 0) > 0
  const hasIssues = (issues?.length || 0) > 0

  if (!hasProfile) {
    console.log('❌ PROBLEM: User profile missing or blocked')
    console.log('   FIX: Ensure profile record exists with correct org_id')
  }

  if (!hasMemberships) {
    console.log('❌ PROBLEM: User is not a project member')
    console.log('   FIX: Add user to project_members table')
    console.log('   SQL: INSERT INTO project_members (project_id, user_id, role_id)')
    console.log('        VALUES (<project_id>, \'' + user.id + '\', <admin_role_id>);')
  }

  if (hasMemberships && !hasIssues) {
    console.log('⚠️ POSSIBLE ISSUE: Member but no issues visible')
    console.log('   CHECK: Issues may be in different project')
    console.log('   CHECK: Issues may have deleted_at set')
  }

  if (hasProfile && hasMemberships && hasIssues) {
    console.log('✅ All checks passed - issue should be loading')
    console.log('   If still not working, check browser console for errors')
  }
}

diagnose().catch(console.error)
