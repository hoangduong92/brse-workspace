/**
 * Admin diagnostic script - bypasses RLS to see actual data
 * Run: node scripts/diagnose-admin.mjs
 */

import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://hsdoyzzootrdjeysxrba.supabase.co'
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || ''

const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY)

async function diagnose() {
  console.log('=== ADMIN DIAGNOSTIC (RLS Bypassed) ===\n')

  // 1. Get all profiles
  console.log('1. PROFILES:')
  const { data: profiles } = await supabase.from('profiles').select('*')
  profiles?.forEach(p => {
    console.log(`   - ${p.email} (id=${p.id.slice(0,8)}..., org_id=${p.org_id})`)
  })
  console.log()

  // 2. Get all organizations
  console.log('2. ORGANIZATIONS:')
  const { data: orgs } = await supabase.from('organizations').select('*')
  orgs?.forEach(o => {
    console.log(`   - ${o.name} (id=${o.id}, slug=${o.slug})`)
  })
  console.log()

  // 3. Get all projects
  console.log('3. PROJECTS:')
  const { data: projects } = await supabase.from('projects').select('*')
  projects?.forEach(p => {
    console.log(`   - ${p.key}: ${p.name} (id=${p.id}, org_id=${p.org_id})`)
  })
  console.log()

  // 4. Get all project_members
  console.log('4. PROJECT_MEMBERS:')
  const { data: members } = await supabase
    .from('project_members')
    .select('*, project:projects(key), user:profiles(email), role:roles(name)')

  if (!members?.length) {
    console.log('   ❌ NO PROJECT MEMBERS FOUND!')
    console.log('   → This is the ROOT CAUSE - no one can see issues')
  } else {
    members?.forEach(m => {
      const proj = m.project
      const user = m.user
      const role = m.role
      console.log(`   - Project ${proj?.key}: ${user?.email} (role=${role?.name})`)
    })
  }
  console.log()

  // 5. Get all issues
  console.log('5. ISSUES:')
  const { data: issues } = await supabase
    .from('issues')
    .select('*, reporter:profiles!issues_reporter_id_fkey(email)')
    .is('deleted_at', null)

  if (!issues?.length) {
    console.log('   No issues found')
  } else {
    issues?.forEach(i => {
      console.log(`   - #${i.issue_number}: ${i.title} (project_id=${i.project_id}, reporter=${i.reporter?.email})`)
    })
  }
  console.log()

  // 6. Get roles
  console.log('6. ROLES:')
  const { data: roles } = await supabase.from('roles').select('*')
  roles?.forEach(r => {
    console.log(`   - ${r.name} (id=${r.id}, org_id=${r.org_id}, is_system=${r.is_system})`)
  })
  console.log()

  // 7. Cross-reference check
  console.log('=== DIAGNOSIS ===\n')

  const profileIds = new Set(profiles?.map(p => p.id) || [])
  const memberUserIds = new Set(members?.map(m => m.user_id) || [])
  const projectIds = new Set(projects?.map(p => p.id) || [])
  const memberProjectIds = new Set(members?.map(m => m.project_id) || [])

  // Check: profiles without membership
  const unmemberedProfiles = profiles?.filter(p => !memberUserIds.has(p.id)) || []
  if (unmemberedProfiles.length) {
    console.log('⚠️ Users WITHOUT project membership:')
    unmemberedProfiles.forEach(p => {
      console.log(`   - ${p.email} (id=${p.id.slice(0,8)}...)`)
    })
    console.log('   → These users CANNOT see any issues due to RLS\n')
  }

  // Check: projects without members
  const unmemberedProjects = projects?.filter(p => !memberProjectIds.has(p.id)) || []
  if (unmemberedProjects.length) {
    console.log('⚠️ Projects WITHOUT any members:')
    unmemberedProjects.forEach(p => {
      console.log(`   - ${p.key}: ${p.name}`)
    })
    console.log('   → No one can access these projects\n')
  }

  // Check: issues in projects without user membership
  if (issues?.length && members?.length) {
    const issueProjectIds = new Set(issues.map(i => i.project_id))
    const missingAccess = [...issueProjectIds].filter(pid => !memberProjectIds.has(pid))
    if (missingAccess.length) {
      console.log('⚠️ Issues exist in projects with no members:')
      missingAccess.forEach(pid => {
        const proj = projects?.find(p => p.id === pid)
        const issueCount = issues.filter(i => i.project_id === pid).length
        console.log(`   - Project ${proj?.key || pid}: ${issueCount} issue(s) orphaned`)
      })
      console.log()
    }
  }

  // Summary
  if (!members?.length) {
    console.log('❌ ROOT CAUSE: No project_members records exist!')
    console.log('\n📋 FIX: Run this SQL in Supabase Dashboard:\n')

    const profile = profiles?.[0]
    const project = projects?.[0]
    const adminRole = roles?.find(r => r.name === 'Admin' && r.is_system)

    if (profile && project && adminRole) {
      console.log(`INSERT INTO project_members (project_id, user_id, role_id)`)
      console.log(`VALUES (${project.id}, '${profile.id}', ${adminRole.id});`)
    }
  } else if (unmemberedProfiles.length) {
    console.log('❌ LIKELY CAUSE: User not in project_members')
    console.log('\n📋 FIX: Add user to project_members\n')

    const profile = unmemberedProfiles[0]
    const project = projects?.[0]
    const adminRole = roles?.find(r => r.name === 'Admin' && r.is_system)

    if (profile && project && adminRole) {
      console.log(`INSERT INTO project_members (project_id, user_id, role_id)`)
      console.log(`VALUES (${project.id}, '${profile.id}', ${adminRole.id});`)
    }
  } else {
    console.log('✅ Data looks correct - membership exists')
    console.log('   Check browser console for client-side errors')
  }
}

diagnose().catch(console.error)
