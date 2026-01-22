# Phase 02: Nulab API Client Implementation

**Context**: Parent plan [../plan.md](plan.md)

## Overview

**Date**: 2026-01-22
**Description**: Implement Python wrapper for Nulab Backlog API with rate limiting, error handling, and retry logic
**Priority**: P1
**Status**: pending
**Effort**: 3h

## Context Links

- Research: [../research/researcher-01-nulab-api.md](research/researcher-01-nulab-api.md)
- Depends on: [Phase 01: Project Setup](phase-01-project-setup.md)

## Key Insights

- API Key authentication is simplest for local automation
- Rate limit: 100 req/min (free), 300 req/min (paid)
- Use exponential backoff for 429 errors
- Cache project metadata to reduce API calls
- **[VALIDATED]** Must copy attachments from source to destination

## Requirements

### Functional
- Fetch issue by ID from source project
- Create issue in destination project
- Create subtasks with parent issue reference
- **[VALIDATED]** Copy attachments from source to destination issue
- Add comments to issues

### Non-Functional
- Rate limiting with automatic retry
- Error handling for all HTTP codes
- Request logging for debugging
- < 1s response time for cached operations

## Architecture

```python
class BacklogAPI:
    def __init__(space_url, api_key)
    def get_issue(issue_id) -> Issue
    def create_issue(project_id, data) -> Issue
    def add_comment(issue_id, content) -> Comment
    def get_project(project_id) -> Project
    # [VALIDATED] Attachment methods
    def get_attachments(issue_id) -> list[Attachment]
    def download_attachment(attachment) -> bytes
    def add_attachment(issue_id, file_data, filename) -> Attachment
    def _request(method, endpoint, **kwargs) -> Response
    def _rate_limit_wait(response) -> None

class Issue:
    id, project_id, summary, description,
    issue_type, priority, assignee, status,
    parent_issue_id, created, updated,
    attachments: list[Attachment]

class Attachment:
    id, name, content_url, size, created

class Project:
    id, name, issue_types, priorities, users
```

## Related Code Files

### Modify
- `.claude/skills/backlog/scripts/nulab_client.py`

### Create
- `.claude/skills/backlog/scripts/models.py`
- `.claude/skills/backlog/tests/test_nulab_client.py`

### Reference
- Research report: `research/researcher-01-nulab-api.md`

## Implementation Steps

1. **Create data models** (`models.py`)
   - `Issue` dataclass with all fields
   - `Project` dataclass with metadata
   - `Comment` dataclass

2. **Implement base API client** (`nulab_client.py`)
   ```python
   class BacklogAPI:
       BASE_URL = "https://{space}.backlogtool.com/api/v2"

       def __init__(self, space_url: str, api_key: str):
           self.space_url = space_url
           self.api_key = api_key
           self.session = requests.Session()
           self.last_request_time = 0

       def _request(self, method: str, endpoint: str, **kwargs):
           # Add apiKey to params
           # Implement rate limiting
           # Handle errors
           # Return response
   ```

3. **Implement rate limiting**
   ```python
   MIN_REQUEST_INTERVAL = 1.0  # 1 second between requests

       def _rate_limit_wait(self):
           elapsed = time.time() - self.last_request_time
           if elapsed < self.MIN_REQUEST_INTERVAL:
               time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
           self.last_request_time = time.time()
   ```

4. **Implement get_issue**
   ```python
   def get_issue(self, issue_id: str) -> Issue:
       self._rate_limit_wait()
       response = self._request("GET", f"/issues/{issue_id}")
       return Issue.from_dict(response.json())
   ```

5. **Implement create_issue**
   ```python
   def create_issue(self, project_id: int, data: dict) -> Issue:
       self._rate_limit_wait()
       response = self._request("POST", "/issues", data=data)
       return Issue.from_dict(response.json())
   ```

6. **Implement create_subtask**
   ```python
   def create_subtask(self, project_id: int, parent_id: int, data: dict) -> Issue:
       data["parentIssueId"] = parent_id
       return self.create_issue(project_id, data)
   ```

7. **[VALIDATED] Implement attachment methods**
   ```python
   def get_attachments(self, issue_id: str) -> list[Attachment]:
       """Get list of attachments for an issue"""
       self._rate_limit_wait()
       response = self._request("GET", f"/issues/{issue_id}/attachments")
       return [Attachment.from_dict(a) for a in response.json()]

   def download_attachment(self, attachment: Attachment) -> bytes:
       """Download attachment content"""
       self._rate_limit_wait()
       response = requests.get(attachment.content_url, params={"apiKey": self.api_key})
       response.raise_for_status()
       return response.content

   def add_attachment(self, issue_id: str, file_data: bytes, filename: str) -> Attachment:
       """Upload attachment to issue"""
       self._rate_limit_wait()
       files = {"file": (filename, file_data)}
       response = self._request("POST", f"/issues/{issue_id}/attachments", files=files)
       return Attachment.from_dict(response.json()[0])
   ```

8. **Add error handling**
   - 400: Bad Request - log error, raise exception
   - 401: Unauthorized - check API key
   - 404: Not Found - invalid issue ID
   - 429: Rate limit - exponential backoff
   - 500: Server error - retry up to 3 times

9. **Add logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)

   # Log all requests
   logger.info(f"GET /issues/{issue_id}")
   logger.debug(f"Response: {response.status_code}")
   ```

10. **[VALIDATED] Add attachment copying helper**
    ```python
    def copy_attachments(self, source_issue_id: str, dest_issue_id: str) -> list[Attachment]:
        """Copy all attachments from source to destination issue"""
        attachments = self.get_attachments(source_issue_id)
        copied = []
        for attachment in attachments:
            file_data = self.download_attachment(attachment)
            new_attachment = self.add_attachment(dest_issue_id, file_data, attachment.name)
            copied.append(new_attachment)
        return copied
    ```

11. **Write tests**
   - Mock requests for unit tests
   - Test rate limiting logic
   - Test error scenarios
   - Test data model parsing

## Todo List

- [ ] Create data models in models.py (Issue, Project, Comment, **[VALIDATED] Attachment**)
- [ ] Implement base BacklogAPI class
- [ ] Add rate limiting with wait timer
- [ ] Implement get_issue method
- [ ] Implement create_issue method
- [ ] Implement create_subtask method
- [ ] **[VALIDATED] Implement get_attachments method**
- [ ] **[VALIDATED] Implement download_attachment method**
- [ ] **[VALIDATED] Implement add_attachment method**
- [ ] **[VALIDATED] Implement copy_attachments helper**
- [ ] Add comprehensive error handling
- [ ] Add request/response logging
- [ ] Write unit tests with mocks
- [ ] Test with real API (use test issue)

## Success Criteria

- [ ] Can fetch issue from HB21373
- [ ] Can create issue in same project
- [ ] Can create subtask with parent reference
- [ ] **[VALIDATED] Can copy attachments from source to destination**
- [ ] Rate limiting prevents 429 errors
- [ ] All unit tests passing
- [ ] Error handling covers all HTTP codes

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | Medium | Implement 1s delay between requests |
| Network failures | Medium | Retry with exponential backoff |
| Invalid API key | High | Validate on init, test with simple call |
| Malformed response | Low | Use dataclasses with validation |

## Security Considerations

- Never log API keys
- Use environment variables for credentials
- Validate API key format on initialization
- Sanitize error messages before logging

## Next Steps

Proceed to [Phase 03: Claude Translation Service](phase-03-claude-translation.md) after API client tests pass.

---

**Dependencies**: Phase 01 must be complete
**Blocks**: Phase 05 (needs working API client)
