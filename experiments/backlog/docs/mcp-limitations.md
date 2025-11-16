# MCP Tools vs BacklogClient: Understanding the Limitation

## The Anthropic Article vs Our Reality

The [Anthropic article on code execution with MCP](https://www.anthropic.com/news/code-execution-mcp) describes an ideal architecture where:
- MCP tools are wrapped as importable TypeScript functions
- Generated code calls these wrappers
- Filtering happens in code execution environment
- Only filtered results enter LLM context

**This assumes an agent framework with a `callMCPTool` bridge function.**

## Claude Code's Current Architecture

Claude Code has **two separate execution contexts**:

### 1. Conversation Context (where Claude operates)
```typescript
// Claude can call MCP tools directly
const issues = await mcp__backlog__get_issues({projectId: [47358]});
// ✅ Works!
// ❌ But subject to 25K token response limit
```

### 2. Code Execution Context (`npx tsx script.ts`)
```typescript
// Generated code runs in separate Node.js process
const issues = await mcp__backlog__get_issues({...});
// ❌ ReferenceError: mcp__backlog__get_issues is not defined
// No access to Claude Code's MCP system
```

## Why `callMCPTool` Cannot Be Implemented (Currently)

**Requirements for the Anthropic pattern:**
1. MCP client server that code can communicate with
2. IPC/HTTP bridge between code execution and MCP system
3. Documented API for calling MCP tools from Node.js

**What Claude Code provides:**
- ✅ MCP tools in conversation context
- ✅ Code execution via `npx tsx`
- ❌ No documented bridge between them
- ❌ No official `callMCPTool` API

**Evidence:**
- `CLAUDE_CODE_SSE_PORT=51494` exists (internal server)
- But API format is undocumented
- Reverse-engineering would be fragile and unsupported

## Our Practical Solutions

### Solution 1: Hybrid Approach (Recommended)

Use the right tool for the job:

**Small queries (<25K tokens) → MCP in conversation**
```typescript
// Claude calls MCP directly in conversation
const projectList = await mcp__backlog__get_project_list({});
const issueTypes = await mcp__backlog__get_issue_types({projectId: 47358});
const count = await mcp__backlog__count_issues({projectId: [47358]});
```

**Large queries (>25K tokens) → BacklogClient in generated code**
```typescript
// Generate: fetch-issues.ts
import { BacklogClient } from './src/backlog-client.js';

const client = new BacklogClient({
  domain: process.env.BACKLOG_DOMAIN!,
  apiKey: process.env.BACKLOG_API_KEY!
});

const issues = await client.getIssuesFiltered({
  projectId: [47358],
  count: 100
});

console.table(issues); // Only minimal fields
```

### Solution 2: BacklogClient as "MCP Proxy"

Treat BacklogClient as a local implementation that mirrors MCP tools:

**MCP Tool Equivalents:**
```typescript
// MCP tool signature
mcp__backlog__get_issues(params) → 90K tokens (exceeds limit)

// BacklogClient equivalent
client.getIssuesFiltered(params) → 1K tokens (pre-filtered)
```

**Benefits:**
- ✅ Same Backlog API calls as MCP server
- ✅ Filtering happens before context
- ✅ No token limits

**Trade-offs:**
- ⚠️ Bypasses MCP (direct API calls)
- ⚠️ Must maintain two implementations (MCP + BacklogClient)

## Decision Matrix

| Scenario | Tool | Reason |
|----------|------|--------|
| Get project list | MCP in conversation | <100 tokens, metadata |
| Get issue types | MCP in conversation | <500 tokens, metadata |
| Count issues | MCP in conversation | <10 tokens, just a number |
| Get 5 issues | MCP in conversation | ~10K tokens, under limit |
| Get 50+ issues | BacklogClient in code | ~100K tokens, exceeds limit |
| Complex filtering | BacklogClient in code | Need loops, logic |
| Batch operations | BacklogClient in code | Multiple API calls |

## Future: If Claude Code Adds MCP Bridge

If Claude Code provides official `callMCPTool` support, we should:

1. Create wrapper functions:
```typescript
// src/mcp-bridge.ts (future)
export async function callMCPTool(toolName: string, params: any) {
  // Official Claude Code API here
  const response = await fetch(`http://localhost:${process.env.CLAUDE_CODE_SSE_PORT}/mcp`, {
    method: 'POST',
    body: JSON.stringify({ tool: toolName, params })
  });
  return response.json();
}

// src/backlog-mcp.ts (future)
import { callMCPTool } from './mcp-bridge.js';

export async function getIssues(params: any) {
  return callMCPTool('mcp__backlog__get_issues', params);
}
```

2. Update generated code to use wrappers:
```typescript
// fetch-issues.ts (future ideal version)
import { getIssues } from './src/backlog-mcp.js';

const raw = await getIssues({projectId: [47358]});
const filtered = raw.map(i => ({id: i.id, key: i.issueKey, summary: i.summary}));
console.table(filtered);
```

3. Achieve Anthropic's 98.7% token reduction pattern

## Conclusion

**Current state:**
- MCP tools work in conversation only
- BacklogClient works in generated code only
- Hybrid approach is practical and effective

**What we're missing:**
- Official `callMCPTool` bridge from Claude Code
- Until then, BacklogClient is a reasonable alternative

**Recommendation:**
- Document hybrid approach clearly
- Don't mislead users about MCP availability in generated code
- Consider BacklogClient as "MCP-equivalent for code execution"
