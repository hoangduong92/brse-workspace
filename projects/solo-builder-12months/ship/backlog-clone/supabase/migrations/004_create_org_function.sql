-- ============================================
-- Function: Create Organization with Profile Link
-- Purpose: Atomically create org and link user's profile
-- Bypasses RLS during bootstrap (new user creating first org)
-- ============================================

CREATE OR REPLACE FUNCTION create_organization_with_profile(
  p_name VARCHAR(255),
  p_slug VARCHAR(100),
  p_user_id UUID
)
RETURNS JSON AS $$
DECLARE
  v_org_id BIGINT;
  v_admin_role_id BIGINT;
BEGIN
  -- 1. Create organization
  INSERT INTO organizations (name, slug)
  VALUES (p_name, p_slug)
  RETURNING id INTO v_org_id;

  -- 2. Update user's profile with org_id
  UPDATE profiles
  SET org_id = v_org_id
  WHERE id = p_user_id;

  -- 3. Get admin role (created by trigger)
  SELECT id INTO v_admin_role_id
  FROM roles
  WHERE org_id = v_org_id AND name = 'Admin';

  -- Return organization data
  RETURN json_build_object(
    'org', json_build_object(
      'id', v_org_id,
      'name', p_name,
      'slug', p_slug
    ),
    'adminRole', json_build_object(
      'id', v_admin_role_id
    )
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION create_organization_with_profile TO authenticated;

-- ============================================
-- Function: Create Project with Member
-- Purpose: Atomically create project and add creator as Admin
-- Bypasses RLS during project creation
-- ============================================

CREATE OR REPLACE FUNCTION create_project_with_member(
  p_org_id BIGINT,
  p_name VARCHAR(255),
  p_key VARCHAR(10),
  p_description TEXT,
  p_user_id UUID
)
RETURNS JSON AS $$
DECLARE
  v_project_id BIGINT;
  v_admin_role_id BIGINT;
BEGIN
  -- 1. Create project
  INSERT INTO projects (org_id, name, key, description)
  VALUES (p_org_id, p_name, UPPER(p_key), p_description)
  RETURNING id INTO v_project_id;

  -- 2. Get admin role for this org
  SELECT id INTO v_admin_role_id
  FROM roles
  WHERE org_id = p_org_id AND name = 'Admin' AND is_system = TRUE;

  -- 3. Add creator as project member with Admin role
  INSERT INTO project_members (project_id, user_id, role_id)
  VALUES (v_project_id, p_user_id, v_admin_role_id);

  -- Return project data
  RETURN json_build_object(
    'id', v_project_id,
    'org_id', p_org_id,
    'name', p_name,
    'key', UPPER(p_key),
    'description', p_description
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION create_project_with_member TO authenticated;

-- ============================================
-- FIX: Update RLS policies to use SECURITY DEFINER functions
-- The original inline subqueries cause circular RLS issues
-- ============================================

-- Drop problematic policies
DROP POLICY IF EXISTS "projects_select_members" ON projects;

-- Recreate with helper function (SECURITY DEFINER bypasses RLS)
CREATE POLICY "projects_select_members"
ON projects FOR SELECT
USING (is_project_member(id));

-- Also fix profile reading for users without org (onboarding)
DROP POLICY IF EXISTS "profiles_select_same_org" ON profiles;

CREATE POLICY "profiles_select_same_org"
ON profiles FOR SELECT
USING (
  id = auth.uid() -- Can always read own profile
  OR org_id = get_user_org_id() -- Can read profiles in same org
);
