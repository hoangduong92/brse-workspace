# Backlog API Quick Reference

## Endpoints Used by bk-status

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/projects/{id}` | Get project info |
| GET | `/projects/{id}/statuses` | List status definitions |
| GET | `/projects/{id}/users` | List project members |
| GET | `/issues?projectId[]={id}` | List issues (paginated) |

## Issue Filters

| Parameter | Type | Description |
|-----------|------|-------------|
| `statusId[]` | int[] | Filter by status |
| `assigneeId[]` | int[] | Filter by assignee |
| `dueDateUntil` | date | Due before (yyyy-MM-dd) |
| `dueDateSince` | date | Due after |
| `sort` | string | dueDate, created, updated |
| `order` | string | asc, desc |
| `count` | int | Results per page (max 100) |
| `offset` | int | Pagination offset |

## Rate Limits

- 1 request per second (enforced by client)
- Auto-retry on 429 with exponential backoff

## Response Formats

### Issue Object
```json
{
  "id": 123,
  "projectId": 1,
  "issueKey": "PROJ-45",
  "summary": "Task title",
  "status": {"id": 1, "name": "Open"},
  "assignee": {"id": 5, "name": "Tanaka"},
  "dueDate": "2026-01-28"
}
```

### Status Object
```json
{
  "id": 1,
  "projectId": 1,
  "name": "Open",
  "displayOrder": 1
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Invalid API key |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500+ | Server error (auto-retry) |
