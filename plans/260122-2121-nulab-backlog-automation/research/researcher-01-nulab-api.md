# Nulab Backlog API Research Report
**Date:** 2026-01-22
**Focus:** Automation capabilities and REST API endpoints

## Authentication Methods

### 1. API Key (Simple)
```python
import requests

# API Key authentication
url = "https://your-space.backlog.com/api/v2/users/myself"
params = {"apiKey": "your_api_key_here"}
response = requests.get(url, params=params)
```

### 2. OAuth 2.0 (Recommended for apps)
```python
# OAuth 2.0 Authorization Code Grant
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN",
    "Content-Type": "application/json"
}
response = requests.get("https://your-space.backlog.com/api/v2/space", headers=headers)
```

**Key Points:**
- API key: Simple but limited to one user
- OAuth 2.0: More secure, supports user impersonation
- Access tokens expire in 1 hour (3600 seconds)
- Use refresh tokens to get new access tokens

## Core API Endpoints

### Issue/Task Operations

#### Create Issue
```python
url = "https://your-space.backlog.com/api/v2/issues"
data = {
    "projectId": 100,
    "summary": "New issue from automation",
    "issueTypeId": 1,
    "priorityId": 2,
    "description": "Issue description",
    "estimatedHours": 8.0,
    "assigneeId": 123
}
response = requests.post(url, data=data)
```

#### Create Subtask
```python
# Add parentIssueId to create a subtask
data = {
    "projectId": 100,
    "summary": "Subtask",
    "issueTypeId": 2,
    "priorityId": 2,
    "parentIssueId": 456  # Parent issue ID
}
```

#### Get Issue List
```python
url = "https://your-space.backlog.com/api/v2/issues"
params = {
    "projectId": 100,
    "statusId[]": [1, 2, 3],
    "assigneeId[]": [123, 456],
    "limit": 100,
    "offset": 0
}
response = requests.get(url, params=params)
```

### Comment Operations

#### Add Comment
```python
url = "https://your-space.backlog.com/api/v2/issues/BLG-100/comments"
data = {
    "content": "Automated comment",
    "notifiedUserId[]": [123, 456]
}
response = requests.post(url, data=data)
```

### File Attachments

#### Post Attachment File
```python
url = "https://your-space.backlog.com/api/v2/issues/addFile"
files = {'file': open('document.pdf', 'rb')}
data = {'projectId': 100}
response = requests.post(url, files=files, data=data)
attachment_id = response.json()['id']
```

#### Attach File to Issue
```python
# Use attachment ID in other operations
data = {
    "content": "Comment with attachment",
    "attachmentId[]": [789]
}
```

## Available Python Libraries

### Official
- **Backlog4J** (Java only)

### Community Python Libraries
- **PyBacklogPy** by kitadakyou
  - GitHub: Search for "PyBacklogPy"
  - Simple wrapper for Backlog API

### Alternative: Direct Requests
```python
# Install required packages
# pip install requests

import requests
import time

class BacklogAPI:
    def __init__(self, space_url, api_key=None, access_token=None):
        self.base_url = f"https://{space_url}.backlog.com/api/v2"
        self.session = requests.Session()

        if api_key:
            self.params = {"apiKey": api_key}
        elif access_token:
            self.headers = {"Authorization": f"Bearer {access_token}"}

    def create_issue(self, project_id, summary, **kwargs):
        url = f"{self.base_url}/issues"
        data = {"projectId": project_id, "summary": summary, **kwargs}
        return self.session.post(url, data=data, params=getattr(self, 'params', None))

    def get_issues(self, project_id, **params):
        url = f"{self.base_url}/issues"
        params.update({"projectId": project_id})
        return self.session.get(url, params=params, params=getattr(self, 'params', None))
```

## Rate Limits

### Free Plan Limits
- **Read requests:** 60 requests/minute
- **Update requests:** 60 requests/minute
- **Search requests:** 30 requests/minute
- **Icon requests:** 60 requests/minute

### Paid Plan Limits
- **Read requests:** 300 requests/minute
- **Update requests:** 300 requests/minute
- **Search requests:** 150 requests/minute
- **Icon requests:** 300 requests/minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 150      # Max requests per minute
X-RateLimit-Remaining: 142  # Remaining requests
X-RateLimit-Reset: 1605484860  # Reset time (UTC epoch)
```

### Best Practices
1. **Serial requests:** Make requests for single user serially, not concurrently
2. **Delay between requests:** Wait 1+ second between Update/Search/Icon requests
3. **Caching:** Cache responses to reduce API calls
4. **Conditional requests:** Use `updatedSince` parameter to limit data
5. **Exponential backoff:** Retry with delay after 429 errors

## Error Handling

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Authentication failed
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "errors": [
    {
      "message": "Project ID is invalid",
      "code": "invalid_project_id"
    }
  ]
}
```

## Webhook Support

Backlog supports webhooks for:
- Issue created/updated
- Comment added
- Wiki pages updated
- Files attached
- Git pushes
- SVN commits

Webhook URLs receive POST notifications with event data.

## Summary

Nulab Backlog API provides comprehensive REST endpoints for automation with:
- Simple API key and OAuth 2.0 authentication
- Full CRUD operations for issues, comments, and files
- Rate limiting with clear headers
- Community Python support via PyBacklogPy
- Webhook integration for real-time notifications

**Recommendation:** Use OAuth 2.0 for applications, API key for simple scripts, and implement rate limiting in your automation code.

## Sources
- [Backlog API Overview](https://developer.nulab.com/docs/backlog/)
- [Authentication & Authorization](https://developer.nulab.com/docs/backlog/auth/)
- [Libraries](https://developer.nulab.com/docs/backlog/libraries/)
- [Rate Limit](https://developer.nulab.com/docs/backlog/rate-limit/)