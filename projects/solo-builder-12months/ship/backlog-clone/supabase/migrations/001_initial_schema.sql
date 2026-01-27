-- ============================================
-- BACKLOG CLONE MVP - INITIAL SCHEMA
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. ORGANIZATIONS
-- ============================================
CREATE TABLE organizations (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(100) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_organizations_slug ON organizations(slug);

-- ============================================
-- 2. PROFILES (extends auth.users)
-- ============================================
CREATE TABLE profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  org_id BIGINT REFERENCES organizations(id),
  email VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profiles_org ON profiles(org_id);

-- ============================================
-- 3. ROLES
-- ============================================
CREATE TABLE roles (
  id BIGSERIAL PRIMARY KEY,
  org_id BIGINT REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  permissions JSONB DEFAULT '{}',
  is_system BOOLEAN DEFAULT FALSE,  -- Admin, Member, Guest are system roles
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_roles_org ON roles(org_id);

-- Insert default roles (will be created per org via trigger)

-- ============================================
-- 4. PROJECTS
-- ============================================
CREATE TABLE projects (
  id BIGSERIAL PRIMARY KEY,
  org_id BIGINT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  key VARCHAR(10) NOT NULL,  -- e.g., "PROJ", "BACK"
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(org_id, key)
);

CREATE INDEX idx_projects_org ON projects(org_id);
CREATE INDEX idx_projects_key ON projects(org_id, key);

-- ============================================
-- 5. PROJECT_MEMBERS (Junction: Projects ↔ Users)
-- ============================================
CREATE TABLE project_members (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  role_id BIGINT REFERENCES roles(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(project_id, user_id)
);

CREATE INDEX idx_project_members_project ON project_members(project_id);
CREATE INDEX idx_project_members_user ON project_members(user_id);

-- ============================================
-- 6. STATUSES (Lookup - per project)
-- ============================================
CREATE TABLE statuses (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  color VARCHAR(7) DEFAULT '#6B7280',  -- Hex color
  display_order INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_statuses_project ON statuses(project_id);

-- ============================================
-- 7. ISSUE_TYPES (Lookup - per project)
-- ============================================
CREATE TABLE issue_types (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  color VARCHAR(7) DEFAULT '#3B82F6',
  icon VARCHAR(50),  -- Icon name/class
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_issue_types_project ON issue_types(project_id);

-- ============================================
-- 8. CATEGORIES (Lookup - per project, multi-select)
-- ============================================
CREATE TABLE categories (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  allow_multiple BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_categories_project ON categories(project_id);

-- ============================================
-- 9. ISSUES
-- ============================================
CREATE TABLE issues (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  issue_number INT NOT NULL,  -- Auto-increment per project
  title VARCHAR(500) NOT NULL,
  description TEXT,

  -- Relationships
  assignee_id UUID REFERENCES profiles(id),
  reporter_id UUID NOT NULL REFERENCES profiles(id),
  status_id BIGINT REFERENCES statuses(id),
  type_id BIGINT REFERENCES issue_types(id),

  -- Optional parent (for subtasks)
  parent_id BIGINT REFERENCES issues(id),

  -- Time tracking
  estimate_hours DECIMAL(10,2),
  actual_hours DECIMAL(10,2) DEFAULT 0,

  -- Dates
  due_date DATE,
  start_date DATE,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ,  -- Soft delete

  UNIQUE(project_id, issue_number)
);

CREATE INDEX idx_issues_project ON issues(project_id);
CREATE INDEX idx_issues_assignee ON issues(assignee_id);
CREATE INDEX idx_issues_status ON issues(status_id);
CREATE INDEX idx_issues_deleted ON issues(deleted_at) WHERE deleted_at IS NULL;

-- ============================================
-- 10. ISSUE_CATEGORIES (Junction: Issues ↔ Categories)
-- ============================================
CREATE TABLE issue_categories (
  id BIGSERIAL PRIMARY KEY,
  issue_id BIGINT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  category_id BIGINT NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(issue_id, category_id)
);

CREATE INDEX idx_issue_categories_issue ON issue_categories(issue_id);
CREATE INDEX idx_issue_categories_category ON issue_categories(category_id);

-- ============================================
-- 11. COMMENTS
-- ============================================
CREATE TABLE comments (
  id BIGSERIAL PRIMARY KEY,
  issue_id BIGINT NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES profiles(id),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_comments_issue ON comments(issue_id);
CREATE INDEX idx_comments_user ON comments(user_id);

-- ============================================
-- 12. DOCUMENTS (Wiki)
-- ============================================
CREATE TABLE documents (
  id BIGSERIAL PRIMARY KEY,
  project_id BIGINT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  author_id UUID NOT NULL REFERENCES profiles(id),
  title VARCHAR(500) NOT NULL,
  content TEXT,
  parent_id BIGINT REFERENCES documents(id),  -- For nested docs
  display_order INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_project ON documents(project_id);

-- ============================================
-- TRIGGERS: Auto-update updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_organizations_updated
  BEFORE UPDATE ON organizations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_profiles_updated
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_projects_updated
  BEFORE UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_issues_updated
  BEFORE UPDATE ON issues
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_comments_updated
  BEFORE UPDATE ON comments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER tr_documents_updated
  BEFORE UPDATE ON documents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================
-- TRIGGER: Auto-increment issue_number per project
-- ============================================
CREATE OR REPLACE FUNCTION set_issue_number()
RETURNS TRIGGER AS $$
BEGIN
  SELECT COALESCE(MAX(issue_number), 0) + 1
  INTO NEW.issue_number
  FROM issues
  WHERE project_id = NEW.project_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_issues_number
  BEFORE INSERT ON issues
  FOR EACH ROW EXECUTE FUNCTION set_issue_number();

-- ============================================
-- TRIGGER: Create default roles when org created
-- ============================================
CREATE OR REPLACE FUNCTION create_default_roles()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO roles (org_id, name, permissions, is_system) VALUES
    (NEW.id, 'Admin', '{"all": true}', TRUE),
    (NEW.id, 'Member', '{"read": true, "write": true, "delete": false}', TRUE),
    (NEW.id, 'Guest', '{"read": true, "write": false, "delete": false}', TRUE);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_org_default_roles
  AFTER INSERT ON organizations
  FOR EACH ROW EXECUTE FUNCTION create_default_roles();

-- ============================================
-- TRIGGER: Create default statuses when project created
-- ============================================
CREATE OR REPLACE FUNCTION create_default_statuses()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO statuses (project_id, name, color, display_order) VALUES
    (NEW.id, 'Open', '#6B7280', 1),
    (NEW.id, 'In Progress', '#3B82F6', 2),
    (NEW.id, 'Resolved', '#10B981', 3),
    (NEW.id, 'Closed', '#1F2937', 4);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_project_default_statuses
  AFTER INSERT ON projects
  FOR EACH ROW EXECUTE FUNCTION create_default_statuses();

-- ============================================
-- TRIGGER: Create default issue types when project created
-- ============================================
CREATE OR REPLACE FUNCTION create_default_issue_types()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO issue_types (project_id, name, color, icon) VALUES
    (NEW.id, 'Task', '#3B82F6', 'check-square'),
    (NEW.id, 'Bug', '#EF4444', 'bug'),
    (NEW.id, 'Feature', '#8B5CF6', 'star');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_project_default_types
  AFTER INSERT ON projects
  FOR EACH ROW EXECUTE FUNCTION create_default_issue_types();
