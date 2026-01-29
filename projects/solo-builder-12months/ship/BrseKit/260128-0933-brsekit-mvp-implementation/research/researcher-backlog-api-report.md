# Research: Backlog Skill & Nulab Backlog API

## 1. Existing Backlog Skill Analysis

### Implemented Endpoints
- **GET /issues/{issueId}** - Fetch single issue with metadata
- **POST /issues** - Create new issue
- **POST /issues/{issueId}/comments** - Add comments
- **GET /projects/{projectId}** - Fetch project info
- **GET /issues/{issueId}/attachments** - List attachments
- **GET /issues/{issueId}/attachments/{attachmentId}** - Download file
- **POST /space/attachment** - Upload files
- **PATCH /issues/{issueId}** - Update issue (including attachments)

### Rate Limiting & Error Handling
- **Rate limiting**: 1 second minimum interval between requests
- **Retry logic**: 3 attempts with exponential backoff (2s base)
- **429 handling**: Rate limit response with automatic retry
- **Server errors (5xx)**: Retry with exponential backoff
- **Client errors (4xx)**: Specific error messages (401, 404, 400)
- **Timeout**: 30 seconds per request

### Data Models
- `Issue`: id, projectId, key, summary, description, issueTypeId, priorityId, statusId, assignee, parent, timestamps, attachments[]
- `Project`: id, projectKey, name
- `Comment`: id, content, created
- `Attachment`: id, name, size, created

### Limitations
❌ **Missing for PAA reports**:
- No GET /issues endpoint (list issues by project)
- No activity/timeline API (project history)
- No custom field querying
- No user/team querying
- No webhook support

## 2. Nulab Backlog API v2 Capabilities

### Available (Not Yet Implemented)
✅ **GET /projects/{projectId}/issues** - List all issues with filters
  - Params: statusId, assigneeId, createdUserId, issueTypeId, parentChild, sort, offset, count
  - Returns paginated Issue[] with full metadata

✅ **GET /issues/{issueId}/comments** - Fetch issue comments
  - Params: minId, maxId, count, order
  - Returns Comment[] with user info

✅ **GET /projects/{projectId}/activities** - Project activity/timeline
  - Params: activityTypeId, minId, maxId, count, order
  - Returns Activity[] with timestamps

✅ **GET /users** - List project members (for assignee info)

### API Docs
- **Base**: `https://{space_url}/api/v2`
- **Auth**: API key as query param `?apiKey={key}`
- **Response**: JSON with ISO8601 timestamps
- **Rate**: Backlog doesn't advertise limit, but safe with 1sec intervals

## 3. Reusable Components for PAA

### Can Reuse
1. `BacklogAPI` client class:
   - Rate limiting mechanism ✓
   - Error handling pattern ✓
   - Session management ✓
   - Retry logic ✓

2. `BacklogAPIError` exception class ✓

3. Data models:
   - Issue, Project, Comment ✓
   - Need to extend: Activity model (missing)

### Must Add
1. `get_issues_by_project()` method
2. `get_comments_for_issue()` method
3. `get_project_activities()` method
4. `Activity` dataclass for timeline data

## 4. Implementation Plan for PAA

### Phase 1: Extend BacklogAPI Client
- Add `get_issues_by_project(project_id, filters)` → Issue[]
- Add `get_comments_for_issue(issue_id)` → Comment[]
- Add `get_project_activities(project_id)` → Activity[]

### Phase 2: Extend Data Models
- Create `Activity` dataclass (id, type, created, user, content)

### Phase 3: Report Generation
- Fetch issues → Activity[] → Generate PDF/HTML report
- Filter by date range, assignee, issue type
- Include timeline, comments, issue history

## 5. Unresolved Questions

1. Does Backlog API support querying deleted issues or archived projects?
2. What's the max pagination limit for /issues endpoint?
3. Does /activities include comment history, or just issue state changes?
4. Should PAA cache activity data or fetch fresh each time?
5. Any custom fields we need to query beyond built-in properties?
