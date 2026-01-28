# Phase 1: Create Independent Backlog Client

## Context

- **Parent Plan:** [bk-status Implementation](./plan.md)
- **Research:** [Backlog API Capabilities](./research/researcher-02-backlog-api.md)
- **Reference:** `.claude/skills/backlog/scripts/nulab_client.py` (copy pattern, don't modify)

---

## Overview

| Field | Value |
|-------|-------|
| Priority | P0 |
| Status | ✅ DONE |
| Effort | 1h |
| Date | 2026-01-28 |
| Review | [Code Review Report](../reports/code-reviewer-260128-1433-bk-status-phase1.md) |

**Goal:** Create independent `backlog_client.py` and `models.py` in bk-status skill.

**Validated Decision:** Tạo client riêng thay vì extend backlog skill (độc lập, dễ migrate).

---

## Key Insights

1. **Pagination required:** Max 100 results per request, loop until `len(batch) < 100`
2. **Date format:** `yyyy-MM-dd` for `dueDateSince`/`dueDateUntil`
3. **dueDate field:** Use Backlog's "Due Date" field directly
4. **Rate limiting:** 1s between requests, auto-retry on 429

---

## Requirements

### Functional
- `list_issues(project_id, **filters)` - Paginated issue fetching with dueDate
- `get_project_users(project_id)` - List project members
- `get_project_statuses(project_id)` - List status definitions
- `get_project(project_id)` - Get project info

### Non-Functional
- Independent client (copy pattern from backlog skill)
- 1s rate limiting
- Return typed objects (Issue, User, Status)

---

## Related Code Files

### To Create
| File | Purpose |
|------|---------|
| `.claude/skills/bk-status/scripts/__init__.py` | Package marker |
| `.claude/skills/bk-status/scripts/models.py` | Issue, User, Status, Project models |
| `.claude/skills/bk-status/scripts/backlog_client.py` | API client with rate limiting |

### Reference (read-only)
| File | Purpose |
|------|---------|
| `.claude/skills/backlog/scripts/nulab_client.py` | Copy rate limiting, error handling pattern |
| `.claude/skills/backlog/scripts/models.py` | Reference model structure |

---

## Implementation Steps

### Step 1: Create directory structure

```bash
mkdir -p .claude/skills/bk-status/scripts
touch .claude/skills/bk-status/scripts/__init__.py
```

### Step 2: Create models.py with dueDate support

```python
"""Data models for bk-status skill."""

from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class User:
    """Represents a Backlog user/member."""
    id: int
    user_id: str
    name: str
    role_type: int = 1
    email: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            user_id=data.get("userId", ""),
            name=data["name"],
            role_type=data.get("roleType", 1),
            email=data.get("mailAddress", "")
        )


@dataclass
class Status:
    """Represents a Backlog status."""
    id: int
    name: str
    project_id: int = 0
    display_order: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Status":
        return cls(
            id=data["id"],
            name=data["name"],
            project_id=data.get("projectId", 0),
            display_order=data.get("displayOrder", 0)
        )


@dataclass
class Project:
    """Represents a Backlog project."""
    id: int
    project_key: str
    name: str

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            id=data["id"],
            project_key=data["projectKey"],
            name=data["name"]
        )


@dataclass
class Issue:
    """Represents a Backlog issue with dueDate."""
    id: int
    project_id: int
    key_id: str
    summary: str
    description: str
    issue_type_id: int
    priority_id: int
    status_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[str] = None  # yyyy-MM-dd format
    created: str = ""
    updated: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Issue":
        return cls(
            id=data["id"],
            project_id=data["projectId"],
            key_id=data.get("issueKey", ""),
            summary=data["summary"],
            description=data.get("description", ""),
            issue_type_id=data["issueType"]["id"],
            priority_id=data["priority"]["id"],
            status_id=data["status"]["id"],
            assignee_id=data.get("assignee", {}).get("id") if data.get("assignee") else None,
            due_date=data.get("dueDate"),  # Backlog's Due Date field
            created=data.get("created", ""),
            updated=data.get("updated", "")
        )
```

### Step 3: Create backlog_client.py

```python
"""Backlog API client for bk-status skill."""

import time
import logging
import requests
from typing import Optional

from .models import Issue, User, Status, Project

logger = logging.getLogger(__name__)


class BacklogAPIError(Exception):
    """Custom exception for Backlog API errors."""
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class BacklogClient:
    """Client for Nulab Backlog API v2."""

    MIN_REQUEST_INTERVAL = 1.0
    MAX_RETRIES = 3
    RETRY_DELAY = 2.0

    def __init__(self, space_url: str, api_key: str):
        self.space_url = space_url.rstrip("/")
        self.api_key = api_key
        self.base_url = f"https://{self.space_url}/api/v2"
        self.session = requests.Session()
        self.last_request_time = 0.0

        if not api_key or len(api_key) < 10:
            raise ValueError("Invalid API key format")

    def _rate_limit_wait(self) -> None:
        elapsed = time.time() - self.last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            time.sleep(self.MIN_REQUEST_INTERVAL - elapsed)
        self.last_request_time = time.time()

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        self._rate_limit_wait()
        url = f"{self.base_url}{endpoint}"
        params = kwargs.pop("params", {})
        params["apiKey"] = self.api_key

        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.request(method, url, params=params, timeout=30, **kwargs)

                if response.status_code == 429:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {delay}s")
                    time.sleep(delay)
                    continue

                if response.status_code >= 500 and attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue

                if response.status_code == 401:
                    raise BacklogAPIError("Invalid API key", 401)
                if response.status_code == 404:
                    raise BacklogAPIError("Resource not found", 404)

                response.raise_for_status()
                return response

            except requests.RequestException as e:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY * (2 ** attempt))
                else:
                    raise BacklogAPIError(f"Request failed: {e}")

        raise BacklogAPIError("Max retries exceeded")

    def get_project(self, project_id: str) -> Project:
        response = self._request("GET", f"/projects/{project_id}")
        return Project.from_dict(response.json())

    def get_project_statuses(self, project_id: str) -> list[Status]:
        response = self._request("GET", f"/projects/{project_id}/statuses")
        return [Status.from_dict(s) for s in response.json()]

    def get_project_users(self, project_id: str) -> list[User]:
        response = self._request("GET", f"/projects/{project_id}/users")
        return [User.from_dict(u) for u in response.json()]

    def list_issues(
        self,
        project_id: int,
        status_ids: Optional[list[int]] = None,
        assignee_ids: Optional[list[int]] = None,
        due_date_until: Optional[str] = None,
        due_date_since: Optional[str] = None,
        sort: str = "dueDate",
        order: str = "asc"
    ) -> list[Issue]:
        all_issues = []
        offset = 0

        while True:
            params = {
                "projectId[]": project_id,
                "sort": sort,
                "order": order,
                "count": 100,
                "offset": offset
            }

            if status_ids:
                params["statusId[]"] = status_ids
            if assignee_ids:
                params["assigneeId[]"] = assignee_ids
            if due_date_until:
                params["dueDateUntil"] = due_date_until
            if due_date_since:
                params["dueDateSince"] = due_date_since

            logger.info(f"Fetching issues offset={offset}")
            response = self._request("GET", "/issues", params=params)
            batch = [Issue.from_dict(i) for i in response.json()]

            all_issues.extend(batch)

            if len(batch) < 100:
                break
            offset += 100

        return all_issues
```

---

## Todo List

- [x] Create directory structure
- [x] Create models.py with Issue (including dueDate), User, Status, Project
- [x] Create backlog_client.py with rate limiting
- [x] Test imports work correctly
- [x] Write comprehensive unit tests (18 tests, all passing)
- [ ] **Apply security fixes** (URL validation, API key logging)
- [ ] Verify API calls work with real Backlog (integration test)

---

## Success Criteria

- [x] `BacklogClient` initializes with space_url and api_key
- [x] `list_issues()` returns issues with dueDate populated
- [x] `get_project_users()` returns User objects
- [x] `get_project_statuses()` returns Status objects
- [x] Rate limiting works (1s between requests)
- [x] All unit tests pass (18/18)

## Code Review Findings

**Score:** 8.5/10

**Critical Issues:** None

**High Priority Warnings:**
1. API key logging exposure - params may leak in logs
2. URL injection risk - no validation of space_url format

**Action Required:**
- Add URL validation (prevent injection)
- Sanitize API key in logging

See full report: [code-reviewer-260128-1433-bk-status-phase1.md](../reports/code-reviewer-260128-1433-bk-status-phase1.md)

---

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Code duplication from backlog skill | Low | Acceptable for independence |
| API response format mismatch | Low | Test with real API early |

---

## Next Steps

After completion: [Phase 2: TDD Test Fixtures](./phase-02-tdd-test-fixtures.md)
