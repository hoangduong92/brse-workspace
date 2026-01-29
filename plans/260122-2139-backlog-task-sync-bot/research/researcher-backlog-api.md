# Nulab Backlog REST API Research Report

**Date:** 2026-01-22 | **Status:** Complete

## 1. Authentication Methods

### API Key Authentication (Recommended for sync bot)
- **Method:** Query parameter `apiKey` appended to requests
- **Format:** `https://{space}.backlog.com/api/v2/{endpoint}?apiKey={your-key}`
- **Generation:** User Settings → Personal Settings → API Settings
- **Security:** Not affected by 2FA; list all keys via API settings
- **Token Lifetime:** Persistent until manually revoked

### OAuth 2.0 (Alternative)
- Available but more complex; API key preferred for bot automation

## 2. Fetch Issue Details

**Endpoint:** `GET /api/v2/issues/:issueIdOrKey`

**Response Fields:**
- Core: `id`, `projectId`, `issueKey`, `summary`, `description`
- Relations: `issueType`, `priority`, `status`, `assignee`
- Collections: `category[]`, `versions[]`, `milestone[]`, `attachments[]`
- Metadata: `created`, `updated`, `createdUser`, `updatedUser`
- Custom Fields: `customFields[]`

**Code Example:**
```bash
curl "https://{space}.backlog.com/api/v2/issues/PRJ-1?apiKey={key}"
```

## 3. Create/Update Issues

**Create:** `POST /api/v2/issues` → **HTTP 201**

**Required Fields:**
- `projectId` (number)
- `summary` (string, max length varies)
- `issueTypeId` (number)
- `priorityId` (number, e.g., 1-5)

**Key Optional Fields:**
- `parentIssueId` (number) — for subtasks
- `description` (string, supports markdown)
- `startDate`, `dueDate` (yyyy-MM-dd)
- `estimatedHours`, `actualHours` (number)
- `assigneeId` (number)
- `categoryId[]`, `versionId[]`, `milestoneId[]` (arrays)
- `customField_{id}` (custom fields support)
- `attachmentId[]` (pre-uploaded attachments)

**Request Format:** `Content-Type: application/x-www-form-urlencoded`

## 4. Subtasks/Child Issues

**Implementation:**
- Set `parentIssueId` field when creating issue via POST
- Parent issues have `subtaskingEnabled` property
- Child issues include `parentIssueId` field in responses
- No separate endpoint; use standard create with `parentIssueId`

## 5. Attachments

**Upload:** `POST /api/v2/attachments`
- Returns attachment `id`
- File auto-deleted after 1 hour if not attached to issue
- Include `attachmentId[]` in issue creation/update

**Download:** Included in issue response as `attachments[]` with download URLs

**Integration Pattern:**
1. Upload file → get ID
2. Create/update issue with `attachmentId[]` array
3. File persists with issue

## 6. User/Assignee Lookup

**Get Current User:** `GET /api/v2/users/myself?apiKey={key}`

**Available Fields:**
- `id`, `userId`, `name`, `mailAddress`, `roleType`, `nulabAccount`

**Lookup by Username:**
- No direct "search by name" endpoint documented
- Typically retrieve user from `/api/v2/projects/{id}/users` or issue's `assignee` object
- Store user IDs in sync mapping for performance

## 7. Issue Types & Custom Fields

**Issue Types:**
- Project-specific; fetch via `GET /api/v2/projects/{id}`
- Returns `issueTypes[]` with `id`, `name`, `templateSummary`
- Always use correct `issueTypeId` per project

**Custom Fields:**
- Format: `customField_{id}` in requests
- Format: `customField_{id}_otherValue` for multiple values
- Fetch via `GET /api/v2/projects/{id}`
- Returns `customFields[]` with type (`text`, `select`, `radio`, etc.)

## 8. Rate Limits & Best Practices

**Rate Limits:**
- Standard HTTP 429 Too Many Requests on limit
- Exact limit not documented; use exponential backoff
- Daily limits vary by subscription tier

**Best Practices:**
1. Batch operations where possible
2. Cache project metadata (issue types, custom fields, users)
3. Use issue key (e.g., PRJ-123) not ID for human-readable logs
4. Implement retry logic with exponential backoff
5. Store API keys securely (environment variables)
6. Check response `Location` header on 201 for created resource URL

## Implementation Checklist

- [ ] Store API key in `.env` (never commit)
- [ ] Build request builder with query param encoding
- [ ] Implement 201/429 response handling
- [ ] Cache issue types & custom fields by project
- [ ] Map external user IDs to Backlog user IDs
- [ ] Support attachment upload before issue creation
- [ ] Add retry logic with exponential backoff
- [ ] Log all API calls for debugging

## Unresolved Questions

1. Maximum attachment file size limit?
2. Exact rate limit per subscription tier?
3. Bulk issue creation endpoint available?
4. Webhook support for issue updates?
5. Activity/comment API endpoint details needed for full sync?

---

**Sources:**
- [Backlog Developer API Authentication](https://developer.nulab.com/docs/backlog/auth/)
- [Get Issue Endpoint](https://developer.nulab.com/docs/backlog/api/2/get-issue/)
- [Add Issue Endpoint](https://developer.nulab.com/docs/backlog/api/2/add-issue/)
- [Attachment Upload](https://developer.nulab.com/docs/backlog/api/2/post-attachment-file/)
- [API Key Management Guide](https://support.nulab.com/hc/en-us/articles/8783772200217-How-to-register-SSH-public-and-API-keys-in-Backlog)
