# User Guidelines: How to Request Backlog Data from Claude Code

This guide shows you how to ask Claude Code to retrieve tasks and issues from Backlog efficiently.

## 🎯 Quick Start

### Basic Pattern

```
"Get all [status] [type] issues from [project] created between [date1] and [date2]"
```

### Real Examples

```
✅ "Get all closed Task issues from RPA project created from 2025-10-01 to 2025-11-09"

✅ "Show me open Subtasks in HB2_1373_RPA project"

✅ "Count how many issues are closed in RPA project"

✅ "List all high priority bugs that are still open"
```

---

## 📊 Query Types and How to Ask

### 1. Count Issues (Fast, No Token Cost)

**When to use:** You just want to know HOW MANY issues match your criteria

**How to ask:**
```
"How many closed issues are in RPA project?"
"Count open subtasks created this month"
"How many issues are assigned to me?"
```

**What Claude will do:**
- Use MCP tool directly in conversation (fast)
- Return just a number
- Tokens: <10

**Example result:**
```
There are 156 closed issues in the RPA project.
```

---

### 2. Get Small List (<10 issues)

**When to use:** You want to see a few issues with details

**How to ask:**
```
"Show me the 5 most recent closed issues"
"Get the latest 3 high priority bugs"
"List the first 10 open subtasks"
```

**What Claude will do:**
- Use MCP tool directly in conversation
- Filter to essential fields
- Display in a table
- Tokens: ~200-500

**Example result:**
```
Found 5 issues:

| ID      | Key         | Summary                                          |
|---------|-------------|--------------------------------------------------|
| 2854585 | HB21373-400 | RPA/要件定義/ヒアリング -- Hearing yêu cầu            |
| 2853725 | HB21373-396 | 【ー経財部001_資金繰り管理・報告】V-ONEのPR更新            |
...
```

---

### 3. Get Large List (>10 issues)

**When to use:** You need all issues matching your criteria

**How to ask:**
```
"Get ALL closed tasks from RPA project created from 2025-10-01 to 2025-11-09"
"Show me all open issues in the project"
"List all bugs reported this month"
```

**What Claude will do:**
- Generate a TypeScript file
- Use Anthropic pattern (`import * as backlog from './servers/backlog'`)
- Fetch and filter in code
- Display results
- Tokens: ~500-1000 (no matter how many issues!)

**Example result:**
```
✅ Generated file: fetch-closed-tasks.ts
   Running script...

Found 44 issues

+----------+-------------+--------------------------------------------+
| ID       | Key         | Summary                                    |
+----------+-------------+--------------------------------------------+
| 2854585  | HB21373-400 | RPA/要件定義/ヒアリング                          |
| 2853725  | HB21373-396 | 【ー経財部001_資金繰り管理・報告】V-ONEのPR更新      |
...
+----------+-------------+--------------------------------------------+

Token Analysis:
  Raw data: ~88,000 tokens
  Filtered data: ~880 tokens
  Savings: 99% reduction
```

---

## 🔍 Filtering Options

### By Status

```
"Get all [Open/In Progress/Resolved/Closed] issues"
"Show me issues that are NOT closed"
```

**Status IDs:**
- Open = 1
- In Progress = 2
- Resolved = 3
- Closed = 4

### By Type

```
"Get all [Task/Bug/Subtask] issues"
"Show me only subtasks"
```

**Type IDs (RPA project):**
- Task = 203777
- Subtask = 203596

### By Date

```
"Get issues created from 2025-10-01 to 2025-11-09"
"Show me issues created this month"
"List issues updated in the last 7 days"
```

**Date format:** YYYY-MM-DD

### By Priority

```
"Get all high priority issues"
"Show me critical bugs"
```

**Priority levels:**
- Low
- Normal
- High
- Highest

### By Assignee

```
"Get issues assigned to me"
"Show unassigned tasks"
"List issues assigned to user ID 12345"
```

### Combined Filters

```
"Get all OPEN high-priority BUGS created this month"
"Show me closed subtasks from last week that were assigned to me"
"List all overdue tasks that are still in progress"
```

---

## 📝 Request Templates

### Template 1: Simple Status Query
```
"Get all [status] issues from [project]"
```

Example:
```
"Get all closed issues from RPA project"
```

---

### Template 2: Type + Status
```
"Show me all [type] issues that are [status]"
```

Example:
```
"Show me all Subtask issues that are closed"
```

---

### Template 3: Date Range Query
```
"Get all [type] issues created from [start-date] to [end-date]"
```

Example:
```
"Get all Task issues created from 2025-10-01 to 2025-11-09"
```

---

### Template 4: Complex Filter
```
"Get all [status] [type] issues from [project]
created between [date1] and [date2]
with [priority] priority"
```

Example:
```
"Get all closed Task issues from RPA project
created between 2025-10-01 and 2025-11-09
with high priority"
```

---

## ✅ Best Practices

### DO ✅

1. **Specify the project name clearly**
   ```
   ✅ "Get issues from RPA project"
   ✅ "Get issues from HB2_1373_RPA"
   ```

2. **Use clear date formats**
   ```
   ✅ "created from 2025-10-01 to 2025-11-09"
   ✅ "created between October 1 and November 9, 2025"
   ```

3. **Be specific about status**
   ```
   ✅ "Get closed issues"
   ✅ "Show me open and in-progress tasks"
   ```

4. **Combine filters naturally**
   ```
   ✅ "Get all closed subtasks created this month"
   ```

### DON'T ❌

1. **Don't use ambiguous terms**
   ```
   ❌ "Get recent issues" (how recent?)
   ✅ "Get issues created in the last 7 days"
   ```

2. **Don't mix up project names**
   ```
   ❌ "Get issues from project 47358" (use name instead)
   ✅ "Get issues from RPA project"
   ```

3. **Don't request too many details unnecessarily**
   ```
   ❌ "Get all issues with full description and all comments"
   ✅ "Get all issues" (gets essential fields by default)
   ```

4. **Don't forget to specify status if you don't want ALL statuses**
   ```
   ❌ "Get tasks from RPA" (gets ALL statuses)
   ✅ "Get open tasks from RPA"
   ```

---

## 🎨 Advanced Queries

### Query with Custom Logic

```
"Get all issues where the summary contains 'urgent' and status is not closed"
```

Claude will generate:
```typescript
import * as backlog from './servers/backlog/index.js';

const issues = await backlog.getIssues({
  projectId: [47358],
  count: 100
});

const filtered = issues.filter(i =>
  i.summary.toLowerCase().includes('urgent') &&
  i.status !== 'Closed'
);

console.table(filtered);
```

---

### Batch Processing

```
"Get all closed issues from last month and group them by assignee"
```

Claude will generate code that:
1. Fetches all closed issues
2. Filters by date
3. Groups by assignee
4. Displays summary

---

### Export to File

```
"Get all closed issues and save to CSV file"
```

Claude will generate code that:
1. Fetches issues
2. Converts to CSV format
3. Writes to file

---

## 🔧 Project-Specific Information

### RPA Project Details

- **Project ID:** 47358
- **Project Key:** HB21373
- **Full Name:** HB2_1373_RPA

### Issue Type IDs

- **Task:** 203777
- **Subtask:** 203596

### Common Queries for RPA

```
"Get all closed subtasks from RPA project created this month"
"Show me open tasks in RPA that are overdue"
"Count how many issues were resolved in RPA this week"
"List all high-priority bugs in RPA"
```

---

## 📊 What You'll Get Back

### For Counts
```
Found 44 closed issues in RPA project.
```

### For Small Lists (MCP in conversation)
```
Found 5 issues:

| ID      | Key         | Summary          |
|---------|-------------|------------------|
| 123     | HB21373-400 | Task summary...  |
...

Token savings: 98%
```

### For Large Lists (Generated code)
```
✅ Generated: fetch-issues.ts
   Executing...

Found 156 issues

[Table with results]

Token Analysis:
  Raw data: ~312,000 tokens
  Filtered data: ~3,120 tokens
  Savings: 99% reduction
```

---

## 🚀 Quick Reference

| What You Want | How to Ask | What Happens |
|---------------|------------|--------------|
| Just a count | "How many...?" | MCP in conversation (~10 tokens) |
| 1-10 issues | "Show me 5..." | MCP in conversation (~200 tokens) |
| 10+ issues | "Get all..." | Generated code (~500 tokens) |
| Complex filter | "Get...where..." | Generated code with logic |
| Custom logic | "Filter by...and..." | Generated code with custom filter |

---

## 💡 Pro Tips

### 1. Start with Count
```
First: "How many closed issues in RPA?"
Then: "Get all of them"
```
This helps Claude decide the best approach.

### 2. Be Specific About Fields
```
Instead of: "Get issues"
Say: "Get issue keys and summaries for closed tasks"
```

### 3. Use Date Ranges
```
✅ "Get issues from 2025-10-01 to 2025-11-09"
Better than: "Get issues from last month"
```

### 4. Combine Related Queries
```
Instead of multiple requests:
  "How many closed issues?"
  "Show me those issues"

Say:
  "Get all closed issues from RPA and show me the count"
```

### 5. Request Iteration
```
Start: "Get closed tasks from RPA"
Then: "Now filter those to only show high priority ones"
Claude will modify the generated code
```

---

## 🆘 Troubleshooting

### "No issues found"
- ✅ Check project name is correct
- ✅ Verify date range includes issues
- ✅ Check if status filter is too restrictive

### "Too many tokens" error
- ✅ Ask for a count first
- ✅ Add more filters to reduce result set
- ✅ Request pagination: "Get first 100 issues"

### "Project not found"
- ✅ Use correct project name (RPA or HB2_1373_RPA)
- ✅ Check project key: HB21373

---

## 📚 Examples Library

### Example 1: Monthly Report
```
"Get all issues closed in RPA during October 2025 and group by type"
```

### Example 2: My Tasks
```
"Show me all tasks assigned to me that are open or in progress"
```

### Example 3: Overdue Items
```
"Get all overdue issues in RPA that are not closed"
```

### Example 4: Sprint Report
```
"Get all tasks completed between 2025-10-15 and 2025-10-31"
```

### Example 5: Quality Check
```
"Get all bugs reported this month and show their status"
```

---

## 🎓 Learning Path

### Beginner: Simple Queries
1. Start with counts: "How many closed issues?"
2. Get small lists: "Show me 5 recent issues"
3. Add filters: "Get closed tasks"

### Intermediate: Complex Filters
1. Combine filters: "Get closed high-priority bugs"
2. Use date ranges: "Get issues from last month"
3. Request specific fields: "Show issue keys and assignees"

### Advanced: Custom Logic
1. Custom filters: "Get issues where summary contains 'urgent'"
2. Batch processing: "Process all issues in batches of 50"
3. Export data: "Save results to CSV"

---

## 📞 Need Help?

If you're not getting the results you expect:

1. **Start simple** - Begin with "Get all issues from RPA"
2. **Add filters gradually** - Add one filter at a time
3. **Check the data** - Verify project name, dates, status IDs
4. **Ask Claude** - "Can you show me what filters are available?"

Claude Code will guide you through the process and generate the right code for your query!
