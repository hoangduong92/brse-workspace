export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[]

export interface Database {
  public: {
    Tables: {
      organizations: {
        Row: {
          id: number
          name: string
          slug: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          name: string
          slug: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          name?: string
          slug?: string
          created_at?: string
          updated_at?: string
        }
      }
      profiles: {
        Row: {
          id: string
          org_id: number | null
          email: string
          full_name: string | null
          avatar_url: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          org_id?: number | null
          email: string
          full_name?: string | null
          avatar_url?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          org_id?: number | null
          email?: string
          full_name?: string | null
          avatar_url?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      roles: {
        Row: {
          id: number
          org_id: number | null
          name: string
          permissions: Json
          is_system: boolean
          created_at: string
        }
        Insert: {
          id?: number
          org_id?: number | null
          name: string
          permissions?: Json
          is_system?: boolean
          created_at?: string
        }
        Update: {
          id?: number
          org_id?: number | null
          name?: string
          permissions?: Json
          is_system?: boolean
          created_at?: string
        }
      }
      projects: {
        Row: {
          id: number
          org_id: number
          name: string
          key: string
          description: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          org_id: number
          name: string
          key: string
          description?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          org_id?: number
          name?: string
          key?: string
          description?: string | null
          created_at?: string
          updated_at?: string
        }
      }
      project_members: {
        Row: {
          id: number
          project_id: number
          user_id: string
          role_id: number | null
          created_at: string
        }
        Insert: {
          id?: number
          project_id: number
          user_id: string
          role_id?: number | null
          created_at?: string
        }
        Update: {
          id?: number
          project_id?: number
          user_id?: string
          role_id?: number | null
          created_at?: string
        }
      }
      statuses: {
        Row: {
          id: number
          project_id: number
          name: string
          color: string
          display_order: number
          created_at: string
        }
        Insert: {
          id?: number
          project_id: number
          name: string
          color?: string
          display_order?: number
          created_at?: string
        }
        Update: {
          id?: number
          project_id?: number
          name?: string
          color?: string
          display_order?: number
          created_at?: string
        }
      }
      issue_types: {
        Row: {
          id: number
          project_id: number
          name: string
          color: string
          icon: string | null
          created_at: string
        }
        Insert: {
          id?: number
          project_id: number
          name: string
          color?: string
          icon?: string | null
          created_at?: string
        }
        Update: {
          id?: number
          project_id?: number
          name?: string
          color?: string
          icon?: string | null
          created_at?: string
        }
      }
      categories: {
        Row: {
          id: number
          project_id: number
          name: string
          allow_multiple: boolean
          created_at: string
        }
        Insert: {
          id?: number
          project_id: number
          name: string
          allow_multiple?: boolean
          created_at?: string
        }
        Update: {
          id?: number
          project_id?: number
          name?: string
          allow_multiple?: boolean
          created_at?: string
        }
      }
      issues: {
        Row: {
          id: number
          project_id: number
          issue_number: number
          title: string
          description: string | null
          assignee_id: string | null
          reporter_id: string
          status_id: number | null
          type_id: number | null
          parent_id: number | null
          estimate_hours: number | null
          actual_hours: number
          due_date: string | null
          start_date: string | null
          created_at: string
          updated_at: string
          deleted_at: string | null
        }
        Insert: {
          id?: number
          project_id: number
          issue_number?: number
          title: string
          description?: string | null
          assignee_id?: string | null
          reporter_id: string
          status_id?: number | null
          type_id?: number | null
          parent_id?: number | null
          estimate_hours?: number | null
          actual_hours?: number
          due_date?: string | null
          start_date?: string | null
          created_at?: string
          updated_at?: string
          deleted_at?: string | null
        }
        Update: {
          id?: number
          project_id?: number
          issue_number?: number
          title?: string
          description?: string | null
          assignee_id?: string | null
          reporter_id?: string
          status_id?: number | null
          type_id?: number | null
          parent_id?: number | null
          estimate_hours?: number | null
          actual_hours?: number
          due_date?: string | null
          start_date?: string | null
          created_at?: string
          updated_at?: string
          deleted_at?: string | null
        }
      }
      issue_categories: {
        Row: {
          id: number
          issue_id: number
          category_id: number
          created_at: string
        }
        Insert: {
          id?: number
          issue_id: number
          category_id: number
          created_at?: string
        }
        Update: {
          id?: number
          issue_id?: number
          category_id?: number
          created_at?: string
        }
      }
      comments: {
        Row: {
          id: number
          issue_id: number
          user_id: string
          content: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          issue_id: number
          user_id: string
          content: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          issue_id?: number
          user_id?: string
          content?: string
          created_at?: string
          updated_at?: string
        }
      }
      documents: {
        Row: {
          id: number
          project_id: number
          author_id: string
          title: string
          content: string | null
          parent_id: number | null
          display_order: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: number
          project_id: number
          author_id: string
          title: string
          content?: string | null
          parent_id?: number | null
          display_order?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: number
          project_id?: number
          author_id?: string
          title?: string
          content?: string | null
          parent_id?: number | null
          display_order?: number
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
