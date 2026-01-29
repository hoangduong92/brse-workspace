# Phase 02: Backlog API Client

## Context Links
- [Backlog API Research](research/researcher-backlog-api.md)
- [Phase 01: Project Setup](phase-01-project-setup.md)

## Overview
- **Priority:** P1 (core functionality)
- **Status:** pending
- **Effort:** 1.5h
- **Description:** Implement Backlog API client for fetching and creating issues

## Key Insights
- API Key auth via query parameter `?apiKey=xxx`
- Issue creation requires: `projectId`, `summary`, `issueTypeId`, `priorityId`
- Subtasks use `parentIssueId` field
- Attachments: upload first → get ID → attach to issue
- Rate limits exist; implement exponential backoff

## Requirements

### Functional
- Fetch issue by key (e.g., HB21373-123)
- Create issue with description and assignee
- Create subtask (issue with parentIssueId)
- Download/upload attachments
- Get project issue types and users

### Non-Functional
- Retry failed requests with exponential backoff
- Type-safe responses
- Detailed error messages

## Architecture

```typescript
// BacklogClient class structure
class BacklogClient {
  constructor(space: string, apiKey: string)

  // Issues
  getIssue(issueKey: string): Promise<Issue>
  createIssue(data: CreateIssueInput): Promise<Issue>

  // Project metadata
  getProject(projectKey: string): Promise<Project>
  getProjectUsers(projectId: number): Promise<User[]>

  // Attachments
  downloadAttachment(issueId: number, attachmentId: number): Promise<Buffer>
  uploadAttachment(file: Buffer, filename: string): Promise<{id: number}>
}
```

## Related Code Files

### Create
- `experiments/backlog-sync-bot/src/backlog-client.ts`
- `experiments/backlog-sync-bot/src/types/backlog-types.ts`

### Modify
- `experiments/backlog-sync-bot/src/index.ts` (import client)

## Implementation Steps

1. Create types/backlog-types.ts
```typescript
export interface Issue {
  id: number;
  projectId: number;
  issueKey: string;
  summary: string;
  description: string;
  issueType: IssueType;
  priority: Priority;
  status: Status;
  assignee: User | null;
  attachments: Attachment[];
  created: string;
  updated: string;
}

export interface IssueType {
  id: number;
  name: string;
}

export interface Priority {
  id: number;
  name: string;
}

export interface Status {
  id: number;
  name: string;
}

export interface User {
  id: number;
  userId: string;
  name: string;
  mailAddress: string;
}

export interface Attachment {
  id: number;
  name: string;
  size: number;
}

export interface Project {
  id: number;
  projectKey: string;
  name: string;
  issueTypes: IssueType[];
}

export interface CreateIssueInput {
  projectId: number;
  summary: string;
  issueTypeId: number;
  priorityId: number;
  description?: string;
  assigneeId?: number;
  parentIssueId?: number;
  attachmentId?: number[];
}
```

2. Create backlog-client.ts
```typescript
import type {
  Issue,
  Project,
  User,
  CreateIssueInput,
} from "./types/backlog-types.js";

export class BacklogClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(space: string, apiKey: string) {
    this.baseUrl = `https://${space}.backlog.com/api/v2`;
    this.apiKey = apiKey;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    url.searchParams.set("apiKey", this.apiKey);

    const response = await this.fetchWithRetry(url.toString(), options);

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Backlog API error (${response.status}): ${error}`);
    }

    return response.json();
  }

  private async fetchWithRetry(
    url: string,
    options: RequestInit,
    maxRetries = 3
  ): Promise<Response> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(url, options);

        if (response.status === 429) {
          const retryAfter = response.headers.get("Retry-After") || "5";
          await this.delay(parseInt(retryAfter) * 1000);
          continue;
        }

        return response;
      } catch (error) {
        if (attempt === maxRetries) throw error;
        await this.delay(Math.pow(2, attempt) * 1000);
      }
    }
    throw new Error("Request failed after retries");
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  async getIssue(issueKey: string): Promise<Issue> {
    return this.request<Issue>(`/issues/${issueKey}`);
  }

  async createIssue(data: CreateIssueInput): Promise<Issue> {
    const body = new URLSearchParams();
    body.set("projectId", data.projectId.toString());
    body.set("summary", data.summary);
    body.set("issueTypeId", data.issueTypeId.toString());
    body.set("priorityId", data.priorityId.toString());

    if (data.description) body.set("description", data.description);
    if (data.assigneeId) body.set("assigneeId", data.assigneeId.toString());
    if (data.parentIssueId) body.set("parentIssueId", data.parentIssueId.toString());
    if (data.attachmentId) {
      data.attachmentId.forEach((id) => body.append("attachmentId[]", id.toString()));
    }

    return this.request<Issue>("/issues", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });
  }

  async getProject(projectKeyOrId: string | number): Promise<Project> {
    return this.request<Project>(`/projects/${projectKeyOrId}`);
  }

  async getProjectUsers(projectKeyOrId: string | number): Promise<User[]> {
    return this.request<User[]>(`/projects/${projectKeyOrId}/users`);
  }

  async downloadAttachment(
    issueIdOrKey: string | number,
    attachmentId: number
  ): Promise<ArrayBuffer> {
    const url = new URL(
      `${this.baseUrl}/issues/${issueIdOrKey}/attachments/${attachmentId}`
    );
    url.searchParams.set("apiKey", this.apiKey);

    const response = await this.fetchWithRetry(url.toString(), {});
    if (!response.ok) {
      throw new Error(`Failed to download attachment: ${response.status}`);
    }
    return response.arrayBuffer();
  }

  async uploadAttachment(
    file: ArrayBuffer,
    filename: string
  ): Promise<{ id: number }> {
    const formData = new FormData();
    formData.append("file", new Blob([file]), filename);

    const url = new URL(`${this.baseUrl}/space/attachment`);
    url.searchParams.set("apiKey", this.apiKey);

    const response = await this.fetchWithRetry(url.toString(), {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to upload attachment: ${response.status}`);
    }

    return response.json();
  }
}
```

3. Export from index
```typescript
// Add to index.ts or create barrel export
export { BacklogClient } from "./backlog-client.js";
```

## Todo List
- [ ] Create backlog-types.ts with all type definitions
- [ ] Create BacklogClient class
- [ ] Implement getIssue method
- [ ] Implement createIssue method
- [ ] Implement getProject and getProjectUsers
- [ ] Implement downloadAttachment
- [ ] Implement uploadAttachment
- [ ] Add retry logic with exponential backoff
- [ ] Test with real Backlog API

## Success Criteria
- Can fetch issue details by key
- Can create new issue with all required fields
- Can create subtask with parentIssueId
- Can download and upload attachments
- Handles rate limits gracefully
- TypeScript compiles without errors

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rate limit hit | Medium | Exponential backoff implemented |
| Invalid API key | High | Fail fast with clear error message |
| Network timeouts | Medium | Retry logic with 3 attempts |

## Security Considerations
- API key passed as query param (Backlog requirement)
- Never log API key
- Validate input before sending to API

## Next Steps
→ Proceed to Phase 03: Claude Translator
