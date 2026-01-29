# Backlog Skill Research Report

**Date:** 2026-01-28
**Focus:** Understanding Nulab Backlog API client and skill structure for bk-status implementation

---

## Key Files Overview

### Structure
- `SKILL.md` - Workflow instructions for ticket creation/translation
- `scripts/nulab_client.py` - Core API client (287 lines, ~30 methods)
- `scripts/models.py` - Data models (161 lines, 6 dataclasses)
- `scripts/main.py` - Entry point orchestrator
- Helper scripts - `fetch_ticket.py`, `create_ticket.py`, `create_subtask.py`, `add_comment.py`, `copy_attachments.py`, `prevent_delete.py`

---

## BacklogAPI Client Core Methods

### Authentication & Setup
```python
BacklogAPI(space_url: str, api_key: str)
```
- Rate limiting: 1 sec between requests (MIN_REQUEST_INTERVAL)
- Auto-retry: 3 attempts with exponential backoff
- API key validation on init

### Issue Operations
| Method | Purpose | Returns |
|--------|---------|---------|
| `get_issue(issue_id)` | Fetch by ID (e.g., 'HB21373-123') | Issue object |
| `create_issue(project_id, **kwargs)` | Create new issue | Issue object |
| `create_subtask(project_id, parent_id, **kwargs)` | Create subtask | Issue object |
| `add_comment(issue_id, content)` | Add issue comment | Comment object |

### Project Operations
| Method | Purpose | Returns |
|--------|---------|---------|
| `get_project(project_id)` | Fetch project by ID/key | Project object |

### Attachment Operations
| Method | Purpose |
|--------|---------|
| `get_attachments(issue_id)` | List attachments |
| `download_attachment(issue_id, attachment_id)` | Get file bytes |
| `add_attachment(issue_id, file_data, filename)` | Upload file |
| `copy_attachments(source, dest)` | Batch copy |

---

## Data Models

### Issue
```python
@dataclass
class Issue:
    id, project_id, key_id, summary, description
    issue_type_id, priority_id, status_id
    assignee_id, parent_issue_id (optional)
    created, updated, attachments[]
```

### Project
```python
@dataclass
class Project:
    id, project_key, name
```

### Attachment
```python
@dataclass
class Attachment:
    id, name, size, created
```

### Comment
```python
@dataclass
class Comment:
    id, content, created
```

---

## API Endpoints Used

Pattern: `https://{space_url}/api/v2{endpoint}?apiKey={key}`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/issues/{issue_id}` | Fetch issue details |
| POST | `/issues` | Create issue |
| POST | `/issues/{id}/comments` | Add comment |
| GET | `/projects/{id}` | Fetch project |
| GET | `/issues/{id}/attachments` | List attachments |

**Rate limiting:** Returns 429 when exceeded; client auto-backs-off

---

## Reusable Code for bk-status

### For Fetching Issues
```python
from scripts.nulab_client import BacklogAPI
from scripts.models import Issue

# Initialize
client = BacklogAPI(space_url, api_key)
issue = client.get_issue('HB21373-123')

# Access fields
print(issue.summary, issue.assignee_id, issue.status_id)
```

### For Project Analysis
```python
project = client.get_project('HB21373')
# Can list projects via API (not exposed as method - may need custom)
```

### Error Handling
```python
from scripts.nulab_client import BacklogAPIError

try:
    issue = client.get_issue(issue_id)
except BacklogAPIError as e:
    print(f"Error {e.status_code}: {e}")
```

---

## Gaps & Limitations for bk-status

1. **Missing list operations**: No `list_issues()`, `list_projects()`, or `list_members()` methods
   - Need custom implementation using pagination

2. **Missing member API**: No dedicated member/user endpoints
   - Issue/Project contain assignee_id, but member details unavailable
   - Need custom method: `get_members(project_id)` → GET `/projects/{id}/members`

3. **Missing status/priority lookup**: No methods to get available status/priority options
   - Hardcoded IDs in current skill
   - Need: `get_statuses()`, `get_priorities()`, `get_issue_types()`

4. **No bulk operations**: Must fetch/process issues individually with 1s rate limiting
   - For large projects, may be slow

5. **Environment config**: Expects .env with `NULAB_SPACE_URL`, `NULAB_API_KEY`, `NULAB_PROJECT_ID`
   - bk-status needs similar setup

---

## Recommended Approach for bk-status

1. **Extend BacklogAPI** with needed methods:
   - `get_members(project_id) → list[User]`
   - `list_issues(project_id, **filters) → list[Issue]`
   - `get_statuses() → dict` (for status name→id mapping)

2. **Reuse models** from `scripts/models.py`

3. **Reuse client initialization & error handling** pattern

4. **Create status-checking logic** as separate module:
   - Track late tasks (status not updated in X days)
   - Calculate member workload (assigned issues per user)
   - Summarize project progress (% by status)

---

## Unresolved Questions

- API pagination limits per endpoint (issue list, members)?
- Available status/priority/issue-type IDs for the space?
- Should bk-status fetch live or use cached data?
