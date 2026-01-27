# Backlog Clone - ER Diagram

## Entity Relationship Diagram

```mermaid
erDiagram
    organizations ||--o{ users : "has"
    organizations ||--o{ projects : "owns"
    organizations ||--o{ roles : "defines"

    projects ||--o{ issues : "contains"
    projects ||--o{ documents : "has"
    projects ||--o{ project_members : "has"
    projects ||--o{ statuses : "defines"
    projects ||--o{ issue_types : "defines"
    projects ||--o{ categories : "defines"

    users ||--o{ project_members : "joins"
    users ||--o{ issues : "assigned_to"
    users ||--o{ comments : "writes"

    roles ||--o{ project_members : "assigned_in"

    issues ||--o{ comments : "has"
    issues }o--|| statuses : "has"
    issues }o--|| issue_types : "has"
    issues }o--|| categories : "has"

    organizations {
        bigint id PK
        string name
        string slug
        timestamptz created_at
    }

    users {
        uuid id PK
        bigint org_id FK
        string email
        string name
        timestamptz created_at
    }

    projects {
        bigint id PK
        bigint org_id FK
        string name
        string key
        timestamptz created_at
    }

    project_members {
        bigint id PK
        bigint project_id FK
        uuid user_id FK
        bigint role_id FK
        timestamptz created_at
    }

    roles {
        bigint id PK
        bigint org_id FK
        string name
        jsonb permissions
    }

    issues {
        bigint id PK
        bigint project_id FK
        string title
        text description
        uuid assignee_id FK
        bigint status_id FK
        bigint type_id FK
        bigint category_id FK
        int estimate_hours
        int actual_hours
        timestamptz created_at
        timestamptz updated_at
        timestamptz deleted_at
    }

    comments {
        bigint id PK
        bigint issue_id FK
        uuid user_id FK
        text content
        timestamptz created_at
        timestamptz updated_at
    }

    statuses {
        bigint id PK
        bigint project_id FK
        string name
        int display_order
    }

    issue_types {
        bigint id PK
        bigint project_id FK
        string name
        string color
    }

    categories {
        bigint id PK
        bigint project_id FK
        string name
    }

    documents {
        bigint id PK
        bigint project_id FK
        uuid author_id FK
        string title
        text content
        timestamptz created_at
        timestamptz updated_at
    }
```

## Summary

| Type | Tables |
|------|--------|
| Entity | organizations, profiles, projects, issues, documents, comments |
| Junction | project_members, issue_categories |
| Lookup | roles, statuses, issue_types, categories |
| **Total** | **13 tables** |

## Implementation Plan

See: `plans/260125-1822-backlog-clone-mvp/`
