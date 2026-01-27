-- ============================================
-- BACKLOG CLONE MVP - ROW LEVEL SECURITY (RLS)
-- ============================================

-- ============================================
-- ENABLE RLS ON ALL TABLES
-- ============================================
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE statuses ENABLE ROW LEVEL SECURITY;
ALTER TABLE issue_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE issue_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Check if user is member of an organization
CREATE OR REPLACE FUNCTION is_org_member(p_org_id BIGINT)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM profiles
    WHERE id = auth.uid()
    AND org_id = p_org_id
  );
$$ LANGUAGE sql SECURITY DEFINER;

-- Check if user is admin of an organization
-- Admin = has Admin role in at least one project within the org
CREATE OR REPLACE FUNCTION is_org_admin(p_org_id BIGINT)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM project_members pm
    JOIN projects p ON p.id = pm.project_id
    JOIN roles r ON r.id = pm.role_id
    WHERE pm.user_id = auth.uid()
    AND p.org_id = p_org_id
    AND r.name = 'Admin'
    AND r.is_system = TRUE
  );
$$ LANGUAGE sql SECURITY DEFINER;

-- Check if user is member of a project
CREATE OR REPLACE FUNCTION is_project_member(p_project_id BIGINT)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM project_members
    WHERE project_id = p_project_id
    AND user_id = auth.uid()
  );
$$ LANGUAGE sql SECURITY DEFINER;

-- Check if user is admin of a project
CREATE OR REPLACE FUNCTION is_project_admin(p_project_id BIGINT)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM project_members pm
    JOIN roles r ON r.id = pm.role_id
    WHERE pm.project_id = p_project_id
    AND pm.user_id = auth.uid()
    AND r.name = 'Admin'
    AND r.is_system = TRUE
  );
$$ LANGUAGE sql SECURITY DEFINER;

-- Get user's organization ID
CREATE OR REPLACE FUNCTION get_user_org_id()
RETURNS BIGINT AS $$
  SELECT org_id FROM profiles WHERE id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER;

-- ============================================
-- 1. ORGANIZATIONS
-- ============================================

-- Members can read their own organization
CREATE POLICY "org_members_select"
ON organizations FOR SELECT
USING (is_org_member(id));

-- Authenticated users can create organizations (bootstrap)
-- After creation, user must link their profile to the org
CREATE POLICY "authenticated_users_insert_org"
ON organizations FOR INSERT
WITH CHECK (auth.uid() IS NOT NULL);

-- Only admins can update organizations
CREATE POLICY "org_admins_update"
ON organizations FOR UPDATE
USING (is_org_admin(id))
WITH CHECK (is_org_admin(id));

-- Only admins can delete organizations
CREATE POLICY "org_admins_delete"
ON organizations FOR DELETE
USING (is_org_admin(id));

-- ============================================
-- 2. PROFILES
-- ============================================

-- Users can read profiles from their organization
CREATE POLICY "profiles_select_same_org"
ON profiles FOR SELECT
USING (org_id = get_user_org_id());

-- Users can insert their own profile
CREATE POLICY "profiles_insert_self"
ON profiles FOR INSERT
WITH CHECK (id = auth.uid());

-- Users can update only their own profile
CREATE POLICY "profiles_update_self"
ON profiles FOR UPDATE
USING (id = auth.uid())
WITH CHECK (id = auth.uid());

-- ============================================
-- 3. ROLES
-- ============================================

-- Organization members can read roles
CREATE POLICY "roles_select_org_members"
ON roles FOR SELECT
USING (is_org_member(org_id));

-- Only admins can insert roles
CREATE POLICY "roles_insert_admins"
ON roles FOR INSERT
WITH CHECK (is_org_admin(org_id));

-- Only admins can update non-system roles
CREATE POLICY "roles_update_admins"
ON roles FOR UPDATE
USING (is_org_admin(org_id) AND is_system = FALSE)
WITH CHECK (is_org_admin(org_id) AND is_system = FALSE);

-- ============================================
-- 4. PROJECTS
-- ============================================

-- Project members can read projects
CREATE POLICY "projects_select_members"
ON projects FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM project_members
    WHERE project_id = projects.id
    AND user_id = auth.uid()
  )
);

-- Org members can insert projects (org admin or first project in new org)
-- Note: After creation, creator should be added as project admin via project_members
CREATE POLICY "projects_insert_members"
ON projects FOR INSERT
WITH CHECK (is_org_member(org_id));

-- Only org admins can update projects
CREATE POLICY "projects_update_admins"
ON projects FOR UPDATE
USING (is_org_admin(org_id))
WITH CHECK (is_org_admin(org_id));

-- Only org admins can delete projects
CREATE POLICY "projects_delete_admins"
ON projects FOR DELETE
USING (is_org_admin(org_id));

-- ============================================
-- 5. PROJECT_MEMBERS
-- ============================================

-- Project members can view other project members
CREATE POLICY "project_members_select"
ON project_members FOR SELECT
USING (is_project_member(project_id));

-- Only project admins can add members
CREATE POLICY "project_members_insert_admins"
ON project_members FOR INSERT
WITH CHECK (is_project_admin(project_id));

-- Only project admins can update members
CREATE POLICY "project_members_update_admins"
ON project_members FOR UPDATE
USING (is_project_admin(project_id))
WITH CHECK (is_project_admin(project_id));

-- Only project admins can remove members
CREATE POLICY "project_members_delete_admins"
ON project_members FOR DELETE
USING (is_project_admin(project_id));

-- ============================================
-- 6. STATUSES
-- ============================================

-- Project members can view statuses
CREATE POLICY "statuses_select_members"
ON statuses FOR SELECT
USING (is_project_member(project_id));

-- Project admins can insert statuses
CREATE POLICY "statuses_insert_admins"
ON statuses FOR INSERT
WITH CHECK (is_project_admin(project_id));

-- Project admins can update statuses
CREATE POLICY "statuses_update_admins"
ON statuses FOR UPDATE
USING (is_project_admin(project_id))
WITH CHECK (is_project_admin(project_id));

-- Project admins can delete statuses
CREATE POLICY "statuses_delete_admins"
ON statuses FOR DELETE
USING (is_project_admin(project_id));

-- ============================================
-- 7. ISSUE_TYPES
-- ============================================

-- Project members can view issue types
CREATE POLICY "issue_types_select_members"
ON issue_types FOR SELECT
USING (is_project_member(project_id));

-- Project admins can insert issue types
CREATE POLICY "issue_types_insert_admins"
ON issue_types FOR INSERT
WITH CHECK (is_project_admin(project_id));

-- Project admins can update issue types
CREATE POLICY "issue_types_update_admins"
ON issue_types FOR UPDATE
USING (is_project_admin(project_id))
WITH CHECK (is_project_admin(project_id));

-- Project admins can delete issue types
CREATE POLICY "issue_types_delete_admins"
ON issue_types FOR DELETE
USING (is_project_admin(project_id));

-- ============================================
-- 8. CATEGORIES
-- ============================================

-- Project members can view categories
CREATE POLICY "categories_select_members"
ON categories FOR SELECT
USING (is_project_member(project_id));

-- Project admins can insert categories
CREATE POLICY "categories_insert_admins"
ON categories FOR INSERT
WITH CHECK (is_project_admin(project_id));

-- Project admins can update categories
CREATE POLICY "categories_update_admins"
ON categories FOR UPDATE
USING (is_project_admin(project_id))
WITH CHECK (is_project_admin(project_id));

-- Project admins can delete categories
CREATE POLICY "categories_delete_admins"
ON categories FOR DELETE
USING (is_project_admin(project_id));

-- ============================================
-- 9. ISSUES
-- ============================================

-- Project members can view issues
CREATE POLICY "issues_select_members"
ON issues FOR SELECT
USING (is_project_member(project_id));

-- Project members can insert issues
CREATE POLICY "issues_insert_members"
ON issues FOR INSERT
WITH CHECK (is_project_member(project_id));

-- Project members can update issues
CREATE POLICY "issues_update_members"
ON issues FOR UPDATE
USING (is_project_member(project_id))
WITH CHECK (is_project_member(project_id));

-- Only project admins can delete issues
CREATE POLICY "issues_delete_admins"
ON issues FOR DELETE
USING (is_project_admin(project_id));

-- ============================================
-- 10. ISSUE_CATEGORIES
-- ============================================

-- Project members can view issue categories
CREATE POLICY "issue_categories_select_members"
ON issue_categories FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM issues
    WHERE issues.id = issue_categories.issue_id
    AND is_project_member(issues.project_id)
  )
);

-- Project members can insert issue categories
CREATE POLICY "issue_categories_insert_members"
ON issue_categories FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM issues
    WHERE issues.id = issue_categories.issue_id
    AND is_project_member(issues.project_id)
  )
);

-- Project members can update issue categories
CREATE POLICY "issue_categories_update_members"
ON issue_categories FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM issues
    WHERE issues.id = issue_categories.issue_id
    AND is_project_member(issues.project_id)
  )
)
WITH CHECK (
  EXISTS (
    SELECT 1 FROM issues
    WHERE issues.id = issue_categories.issue_id
    AND is_project_member(issues.project_id)
  )
);

-- Project members can delete issue categories
CREATE POLICY "issue_categories_delete_members"
ON issue_categories FOR DELETE
USING (
  EXISTS (
    SELECT 1 FROM issues
    WHERE issues.id = issue_categories.issue_id
    AND is_project_member(issues.project_id)
  )
);

-- ============================================
-- 11. COMMENTS
-- ============================================

-- Project members can view comments on issues in their projects
CREATE POLICY "comments_select_members"
ON comments FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM issues
    WHERE issues.id = comments.issue_id
    AND is_project_member(issues.project_id)
  )
);

-- Project members can insert comments
CREATE POLICY "comments_insert_members"
ON comments FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM issues
    WHERE issues.id = comments.issue_id
    AND is_project_member(issues.project_id)
  )
  AND user_id = auth.uid()
);

-- Only comment authors can update their own comments
CREATE POLICY "comments_update_author"
ON comments FOR UPDATE
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- Only comment authors can delete their own comments
CREATE POLICY "comments_delete_author"
ON comments FOR DELETE
USING (user_id = auth.uid());

-- ============================================
-- 12. DOCUMENTS
-- ============================================

-- Project members can view documents
CREATE POLICY "documents_select_members"
ON documents FOR SELECT
USING (is_project_member(project_id));

-- Project members can insert documents
CREATE POLICY "documents_insert_members"
ON documents FOR INSERT
WITH CHECK (
  is_project_member(project_id)
  AND author_id = auth.uid()
);

-- Project members can update documents
CREATE POLICY "documents_update_members"
ON documents FOR UPDATE
USING (is_project_member(project_id))
WITH CHECK (is_project_member(project_id));

-- Only project admins can delete documents
CREATE POLICY "documents_delete_admins"
ON documents FOR DELETE
USING (is_project_admin(project_id));
