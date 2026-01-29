# Backlog API v2 Status & Workload Tracking Research

## Executive Summary
Nulab Backlog API v2 provides comprehensive issue filtering and project data access. Key capabilities for bk-status skill: status-based filtering, assignee tracking, due date queries, and user list enumeration. API supports batch operations and webhook integration.

## Key Endpoints

### Issue Listing & Filtering
**Endpoint:** `GET /api/v2/issues`

**Critical Parameters:**
- `statusId[]` - Filter by issue status ID (array)
- `assigneeId[]` - Filter issues assigned to user(s)
- `dueDateSince` (yyyy-MM-dd) - Issues due on/after date
- `dueDateUntil` (yyyy-MM-dd) - Issues due before date
- `hasDueDate` (boolean) - Include/exclude items without due date
- `projectId[]` - Scope to specific project(s)
- `sort` - Support "status", "assignee", "dueDate", "created", "updated"
- `order` - "asc" or "desc"

**Pagination:** `offset`, `limit` (default 20, max 100)

### Project Status List
**Endpoint:** `GET /api/v2/projects/{projectIdOrKey}/statuses`

Returns all custom statuses for a project. Essential for mapping status IDs to names and identifying completion states.

### User Management
**Endpoint:** `GET /api/v2/projects/{projectIdOrKey}/users`

Lists all project members. Use this to:
- Build assignee mapping (ID → name)
- Enumerate members for workload calculation
- Validate assignee IDs

## Late Task Identification

Query pattern for overdue tasks:
```
GET /api/v2/issues?
  projectId[]=PROJECT_ID&
  dueDateUntil=TODAY_DATE&
  statusId[]=ACTIVE_STATUS_ID&
  limit=100&
  offset=0
```

**Logic:**
1. Get list of "active" statuses (exclude "Closed", "Done", "Cancelled")
2. Query issues where `dueDateUntil < today` AND status is active
3. Sort by dueDate ascending to show most overdue first
4. Calculate days overdue: `today - dueDate`

## Workload Calculation

**Approach:** Count open issues per assignee

```javascript
// Pseudocode
const workload = {}
const activeStatuses = [1, 2, 3] // Exclude closed statuses
const issues = await getIssues({ statusId: activeStatuses })

issues.forEach(issue => {
  if (issue.assignee) {
    workload[issue.assignee.id] =
      (workload[issue.assignee.id] || 0) + 1
  }
})

// Calculate per-user metrics
const members = await getProjectUsers()
const workloadMetrics = members.map(m => ({
  id: m.id,
  name: m.name,
  openCount: workload[m.id] || 0,
  utilization: (workload[m.id] || 0) / avgOpenPerMember
}))
```

**Alternative:** Weight by priority if needed
```javascript
const priorityWeights = {
  1: 5,  // Highest
  2: 3,  // High
  3: 2,  // Normal
  4: 1   // Low
}
// Sum weights instead of count
```

## Rate Limits & Best Practices

### Rate Limiting
- **Standard:** ~1000 requests/hour (not officially documented, typical for SaaS APIs)
- **Strategy:**
  - Cache project statuses & users (stable data, ~1-5 min TTL)
  - Batch fetch issues with `limit=100` to minimize calls
  - Use `updatedSince` for incremental updates

### Authentication
- **Method:** API Key (bearer token in Authorization header)
- **Header:** `Authorization: Bearer API_KEY`
- **Secure:** Store in environment variables, never commit

### Implementation Best Practices

1. **Pagination Loop** - Handle max 100 results per request
   ```javascript
   let offset = 0, allIssues = []
   while (true) {
     const batch = await getIssues({ offset, limit: 100 })
     allIssues.push(...batch)
     if (batch.length < 100) break
     offset += 100
   }
   ```

2. **Error Handling** - Catch 429 (rate limit), 401 (auth), 404 (not found)

3. **Caching Strategy**
   - Statuses: Cache 5 min
   - Users: Cache 10 min
   - Issues: Cache 1 min (or on-demand)

4. **Filtering Optimization**
   - Always use `projectId[]` to limit scope
   - Use `statusId[]` to exclude closed items early
   - Combine date filters to reduce result set

## Unresolved Questions

1. Exact rate limit thresholds (Backlog docs may have this in detailed API auth section)
2. Whether custom status ordering matters for "active" status detection
3. Estimated/actual hours tracking in issue data (if available for weighted workload)
4. Webhook availability for real-time updates vs polling approach trade-offs

## References
- API Overview: https://developer.nulab.com/docs/backlog/
- Issue List Endpoint: https://developer.nulab.com/docs/backlog/api/2/get-issue-list/
