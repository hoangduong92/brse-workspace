# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 Important: Read Documentation First

**Before working on Backlog queries, read:**
1. **`docs/mcp-limitations.md`** - Why we can't use Anthropic's ideal MCP pattern (yet)
2. **`lesson.md`** - Critical lessons learned from previous tasks
   - MCP tools vs BacklogClient - Understanding which to use when
   - Environment configuration - Required .env variables
   - Token optimization strategies - How to handle large datasets
   - Common pitfalls - Mistakes to avoid
3. **`workflow/CLAUDE.md`** - Automated workflow system for batch operations
   - When user asks to sync/update multiple issues to bilingual format
   - Commands: `npm run sync:dry`, `npm run sync:test`, `npm run sync`

**Key insight:** Claude Code currently lacks a `callMCPTool` bridge between conversation and code execution contexts. We use a **hybrid approach** instead.

## Project Overview

This is a TypeScript utility for filtering Backlog API responses to reduce token consumption when working with LLMs. The tool solves the problem of bloated API responses (~2000 tokens per issue) by filtering them down to essential fields (~20 tokens per issue), achieving 99% token reduction.

## IMPORTANT: Handling User Queries About Backlog Data

⚠️ **CRITICAL: Read `docs/mcp-limitations.md` first!** Understand why we use a hybrid approach.

When a user asks questions about Backlog data, use the **decision matrix** below to choose the right approach.

### 🔀 Hybrid Approach: MCP Tools + BacklogClient

**Two execution contexts require two different approaches:**

| Context | Tools Available | Use Case | Token Limit |
|---------|----------------|----------|-------------|
| **Conversation** | MCP tools | Small queries, metadata | 25K tokens |
| **Generated Code** | BacklogClient | Large queries, batch ops | No limit |

### Decision Matrix

| Query Type | Estimated Tokens | Approach | Tool |
|------------|-----------------|----------|------|
| Get project list | <100 | Call MCP in conversation | `mcp__backlog__get_project_list({})` |
| Get issue types | <500 | Call MCP in conversation | `mcp__backlog__get_issue_types({projectId})` |
| Count issues | <10 | Call MCP in conversation | `mcp__backlog__count_issues({...})` |
| Get 1-5 issues | <10K | Call MCP in conversation | `mcp__backlog__get_issues({count: 5})` |
| Get 10+ issues | >20K | Generate code with BacklogClient | See below |
| Complex filtering | Any | Generate code with BacklogClient | See below |
| Batch operations | Any | Generate code with BacklogClient | See below |

### Flow 1: Small Query (Use MCP in Conversation)

```
User: "What issue types exist in RPA project?"
    ↓
Estimate: <500 tokens
    ↓
Call MCP directly in conversation
    ↓
mcp__backlog__get_issue_types({projectId: 47358})
    ↓
Result: [{id: 203777, name: "Task"}, {id: 203596, name: "Subtask"}]
    ↓
Answer user immediately
```

**When to use:**
- ✅ Metadata queries (projects, issue types, categories)
- ✅ Counting (issue count, user count)
- ✅ Small datasets (<10 items)
- ✅ Quick lookups

### Flow 2: Large Query (Generate Code with BacklogClient)

```
User: "Get all 50 closed tasks from RPA project"
    ↓
Estimate: ~100K tokens (50 × 2K)
    ↓
Generate TypeScript file (.ts)
    ↓
Code uses BacklogClient (NOT MCP tools!)
    ↓
BacklogClient.getIssuesFiltered() calls Backlog API via fetch()
    ↓
Filter immediately in BacklogClient
    ↓
Return minimal data (id, issueKey, summary)
    ↓
Display results in table
    ↓
ONLY filtered result (~1K tokens) enters conversation
```

**When to use:**
- ✅ Large datasets (10+ issues)
- ✅ Complex filtering (loops, conditionals)
- ✅ Batch operations
- ✅ Data transformations

### Environment Setup Required

Ensure `.env` contains all three variables:
```env
BACKLOG_SPACE_KEY=hblab
BACKLOG_DOMAIN=hblab.backlogtool.com
BACKLOG_API_KEY=your_api_key_here
```

### CORRECT APPROACH (ALWAYS DO THIS)

```typescript
// ✅ GOOD: Use BacklogClient in generated code
// File: fetch-issues.ts
import { BacklogClient } from './src/backlog-client.js';
import dotenv from 'dotenv';

dotenv.config();

const client = new BacklogClient({
  domain: process.env.BACKLOG_DOMAIN!,
  apiKey: process.env.BACKLOG_API_KEY!
});

// Fetch and filter in one step
const issues = await client.getIssuesFiltered({
  projectId: [47358],
  issueTypeId: [203777, 203596], // Task, Subtask
  statusId: [4], // Closed
  createdSince: '2025-10-01',
  createdUntil: '2025-11-09',
  count: 100
});

// Issues already filtered - only id, issueKey, summary
console.table(issues);
```

Then execute:
```bash
npx tsx fetch-issues.ts
```

### Examples

**Example 1: MCP in Conversation (Small Query)**
```typescript
// User asks: "How many closed issues in RPA project?"

// Step 1: Count issues using MCP
const count = await mcp__backlog__count_issues({
  projectId: [47358],
  statusId: [4] // Closed
});

// Step 2: Answer user
// "There are 156 closed issues in the RPA project."
```

**Example 2: BacklogClient in Generated Code (Large Query)**
```typescript
// User asks: "Get all 156 closed issues in RPA project"

// Generate file: fetch-closed-issues.ts
import { BacklogClient } from './src/backlog-client.js';
import dotenv from 'dotenv';

dotenv.config();

const client = new BacklogClient({
  domain: process.env.BACKLOG_DOMAIN!,
  apiKey: process.env.BACKLOG_API_KEY!
});

const issues = await client.getIssuesFiltered({
  projectId: [47358],
  statusId: [4], // Closed
  count: 200
});

console.log(`Found ${issues.length} closed issues`);
console.table(issues);

// Execute: npx tsx fetch-closed-issues.ts
// Output: Only id, issueKey, summary (~1K tokens)
```

### BacklogClient API Reference

**Constructor:**
```typescript
new BacklogClient({
  domain: string,  // e.g., "hblab.backlogtool.com"
  apiKey: string
})
```

**Methods:**
```typescript
// Get issues (auto-filtered to minimal fields)
getIssuesFiltered(params: {
  projectId: number[];
  issueTypeId?: number[];
  statusId?: number[];
  createdSince?: string;  // Format: 'YYYY-MM-DD'
  createdUntil?: string;  // Format: 'YYYY-MM-DD'
  count?: number;
  offset?: number;
}): Promise<BacklogIssue[]>

// Get issue count
getIssuesCount(params: {
  projectId: number[];
  issueTypeId?: number[];
  statusId?: number[];
}): Promise<number>
```

**Returns:**
```typescript
interface BacklogIssue {
  id: number;
  issueKey: string;
  summary: string;
}
```

### Backlog Status IDs (Constants)

```typescript
const STATUS_IDS = {
  OPEN: 1,
  IN_PROGRESS: 2,
  RESOLVED: 3,
  CLOSED: 4
};
```

### KEY PRINCIPLES

1. **Estimate tokens first** - Use decision matrix to choose approach
2. **Small queries** (<25K tokens) → Use MCP in conversation
3. **Large queries** (>25K tokens) → Generate code with BacklogClient
4. **MCP tools** only work in conversation context, NOT in generated code
5. **BacklogClient** only works in generated code via direct API calls
6. **Both achieve the same goal** - Token reduction through filtering

### Why Not Anthropic's Ideal Pattern?

The [Anthropic MCP article](https://www.anthropic.com/news/code-execution-mcp) describes calling MCP tools from generated code via `callMCPTool`.

**We can't do this because:**
- ❌ Claude Code lacks a documented `callMCPTool` bridge
- ❌ MCP tools not accessible from `npx tsx` processes
- ❌ No official API to communicate with MCP from generated code

**Our hybrid approach achieves the same benefits:**
- ✅ Token reduction (98%+)
- ✅ Progressive disclosure (load only needed data)
- ✅ Context-efficient filtering
- ✅ No token limits on large datasets

**Read `docs/mcp-limitations.md` for detailed technical explanation.**

### Strategy: 80/20 Filter Pattern

**80% Common Queries**: Use predefined filters in the wrapper
**20% Rare Cases**: Use custom filter functions for complex logic

### Step-by-Step Process

1. **ANALYZE** the user's query intent
   - Identify keywords: status, assignee, priority, due date, etc.
   - Determine if it's a common pattern (80%) or custom logic (20%)

2. **GENERATE** code using BacklogWrapper
   - Import from `./src/backlog-wrapper.js`
   - Use `getIssues()` with appropriate filters
   - Select minimal fields unless user requests details

3. **EXECUTE** the code
   - Code runs in sandbox with access to Backlog API
   - Only filtered results enter conversation context
   - Target: <500 tokens per response (95%+ reduction)

4. **DISPLAY** results
   - Use `displayIssues()` for table output
   - Show token savings to user

### Common Query Patterns (80%)

#### Pattern 1: Status Queries
```typescript
// User: "Show me open issues"
import { getIssues, displayIssues } from './src/backlog-wrapper.js';

const issues = await getIssues({
  projectId: 47358,
  filters: {
    status: ['Open', 'In Progress']
  }
});

displayIssues(issues);
```

#### Pattern 2: Assignment Queries
```typescript
// User: "My open tasks"
const issues = await getIssues({
  projectId: 47358,
  filters: {
    assignee: 'me',
    status: ['Open', 'In Progress']
  }
});

displayIssues(issues);
```

#### Pattern 3: Time-Based Queries
```typescript
// User: "Overdue issues"
const issues = await getIssues({
  projectId: 47358,
  filters: {
    isOverdue: true,
    status: ['Open', 'In Progress']
  }
});

displayIssues(issues);

// User: "Due this week"
const today = new Date();
const nextWeek = new Date(today);
nextWeek.setDate(today.getDate() + 7);

const issues = await getIssues({
  projectId: 47358,
  filters: {
    dueDate: {
      after: today,
      before: nextWeek
    }
  }
});

displayIssues(issues);
```

#### Pattern 4: Priority Queries
```typescript
// User: "High priority issues"
const issues = await getIssues({
  projectId: 47358,
  filters: {
    priority: ['High', 'Highest']
  }
});

displayIssues(issues);
```

#### Pattern 5: Combined Filters
```typescript
// User: "My overdue high priority tasks"
const issues = await getIssues({
  projectId: 47358,
  filters: {
    assignee: 'me',
    isOverdue: true,
    priority: ['High', 'Highest'],
    status: ['Open', 'In Progress']
  }
});

displayIssues(issues);
```

### Custom Query Patterns (20%)

For complex logic that doesn't fit predefined filters:

```typescript
// User: "Issues with more than 5 comments"
const issues = await getIssues({
  projectId: 47358,
  custom: {
    customFilter: (issue) => {
      return issue.comments && issue.comments.length > 5;
    }
  },
  select: ['id', 'key', 'summary', 'comments']
});

displayIssues(issues);
```

```typescript
// User: "Stale issues (no updates in 30 days, still open)"
const thirtyDaysAgo = new Date();
thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

const issues = await getIssues({
  projectId: 47358,
  custom: {
    customFilter: (issue) => {
      if (issue.status?.name === 'Closed') return false;
      const updated = new Date(issue.updated);
      return updated < thirtyDaysAgo;
    }
  },
  select: ['id', 'key', 'summary', 'updated', 'status']
});

displayIssues(issues);
```

### Field Selection Strategy

Choose the appropriate field selection based on user needs:

- **`minimal`** (default): `id`, `key`, `summary` only (~20 tokens/issue)
  - Use when user wants a quick list or overview

- **`standard`**: + `status`, `priority`, `assignee` (~40 tokens/issue)
  - Use when user wants basic status information

- **`extended`**: All fields including description (~100 tokens/issue)
  - Use when user explicitly asks for "details" or "full information"

- **Custom array**: Specific fields only
  - Use when user requests specific fields

```typescript
// User: "Just list issue keys and summaries"
const issues = await getIssues({
  projectId: 47358,
  filters: { status: ['Open'] },
  select: 'minimal'
});

// User: "Show me open issues with assignees"
const issues = await getIssues({
  projectId: 47358,
  filters: { status: ['Open'] },
  select: 'standard'
});

// User: "Show full details of overdue issues"
const issues = await getIssues({
  projectId: 47358,
  filters: { isOverdue: true },
  select: 'extended'
});

// User: "Show issue key, summary, and due date"
const issues = await getIssues({
  projectId: 47358,
  filters: { status: ['Open'] },
  select: ['id', 'key', 'summary', 'dueDate']
});
```

### Available Filters (Quick Reference)

| Filter | Type | Example Values | Use Case |
|--------|------|----------------|----------|
| `status` | `string[]` | `['Open', 'In Progress', 'Resolved', 'Closed']` | Filter by issue status |
| `assignee` | `'me' \| 'unassigned' \| number` | `'me'`, `'unassigned'`, `12345` | Filter by assignee |
| `priority` | `string[]` | `['Low', 'Normal', 'High', 'Highest']` | Filter by priority |
| `isOverdue` | `boolean` | `true`, `false` | Filter overdue issues |
| `dueDate` | `{before?: Date, after?: Date}` | `{before: new Date()}` | Filter by due date range |
| `issueType` | `string[]` | `['Bug', 'Task', 'Subtask']` | Filter by issue type |
| `createdDate` | `{before?: Date, after?: Date}` | `{after: startOfMonth}` | Filter by creation date |
| `updatedDate` | `{before?: Date, after?: Date}` | `{before: yesterday}` | Filter by update date |
| `category` | `string[]` | `['Frontend', 'Backend']` | Filter by category |
| `milestone` | `string[]` | `['v1.0', 'v2.0']` | Filter by milestone |

### Decision Tree

```
User Query
    │
    ├─ Contains "status/open/closed/in progress"?
    │  → Use filters.status
    │
    ├─ Contains "my/assigned/unassigned"?
    │  → Use filters.assignee
    │
    ├─ Contains "overdue/past due"?
    │  → Use filters.isOverdue = true
    │
    ├─ Contains "due this week/month/date"?
    │  → Use filters.dueDate with calculated dates
    │
    ├─ Contains "priority/high/critical"?
    │  → Use filters.priority
    │
    ├─ Contains "created/updated + time reference"?
    │  → Use filters.createdDate or filters.updatedDate
    │
    ├─ Multiple conditions combined?
    │  → Combine multiple filters in single getIssues() call
    │
    └─ Complex logic (">5 comments", "stale", calculations)?
       → Use custom.customFilter with JavaScript function
```

### CRITICAL Rules

1. **NEVER** call MCP tools directly for data queries - always use BacklogWrapper
2. **ALWAYS** start with minimal field selection unless user requests more
3. **PREFER** predefined filters (80%) over custom filters when possible
4. **ESTIMATE** and show token savings to user after displaying results
5. **TARGET**: Keep response under 500 tokens (95%+ reduction from raw data)

### Example: Complete User Interaction

```
User: "Show me my overdue high priority tasks"

Claude generates and executes:
─────────────────────────────────────────────
import { getIssues, displayIssues } from './src/backlog-wrapper.js';

const issues = await getIssues({
  projectId: 47358,
  filters: {
    assignee: 'me',
    isOverdue: true,
    priority: ['High', 'Highest'],
    status: ['Open', 'In Progress']
  },
  select: 'standard'  // Include status, priority, assignee
});

displayIssues(issues);
─────────────────────────────────────────────

Result:
- 5 issues found
- ~200 tokens (vs. ~10,000 tokens if using raw MCP data)
- 98% token reduction
```

### More Examples

See `examples/query-patterns.ts` for comprehensive examples of:
- All common filter patterns
- Custom filter examples
- Field selection strategies
- Analytics queries
- Pagination patterns
