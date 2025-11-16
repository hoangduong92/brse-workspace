# Workflow Automation - Claude Instructions

This file provides guidance to Claude Code when working with the automated workflow system for syncing Backlog issue summaries to bilingual format.

> **Note:** This is AI-specific documentation. For detailed user documentation, see [README.md](./README.md).

## Purpose

The workflow automates the process of ensuring all Backlog issues have summaries in `[Vietnamese/English] -- [Japanese]` format, making them accessible to both Vietnamese and Japanese team members.

## When to Use This Workflow

**Proactively suggest this workflow when user asks:**

- "Sync all issues to bilingual format"
- "Update all RPA tickets with Japanese translations"
- "Make sure all issues have Japanese"
- "Keep issues in VN -- JP format"
- "Translate remaining issues"
- "Run the bilingual sync"
- "Update issue summaries to bilingual"

**Do NOT use workflow when:**
- User wants to update a single specific issue → Generate one-off script
- User needs custom format (not VN -- JP) → Modify translator.ts first, then suggest workflow
- User wants to query/read issues only → Use BacklogClient or MCP tools
- User needs complex custom logic → Write new specialized script

## Command Decision Tree

Follow this decision tree when user asks to sync issues:

```
User asks to sync/update issues to bilingual
    │
    ├─ First time running? OR User wants to preview?
    │  → Run: npm run sync:dry
    │  → Explain: "This shows what will change without making updates"
    │
    ├─ User wants to test/verify first?
    │  → Run: npm run sync:test
    │  → Explain: "This updates only 1 issue so you can verify in Backlog UI"
    │
    ├─ User is confident / has tested already?
    │  → Run: npm run sync
    │  → Explain: "This will update all issues that need translation"
    │
    └─ User wants custom filters or different project?
       → First: Edit workflow/config.json
       → Then: Run appropriate command above
```

## Available Commands

### 1. Dry Run (Safe Preview)
```bash
npm run sync:dry
```
**When to use:**
- First time running workflow
- User wants to see what will change
- User is uncertain about results
- Before running full sync

**What it does:**
- Fetches issues from Backlog
- Shows before/after for each issue
- Does NOT update anything in Backlog
- Generates report showing what would change

### 2. Test Mode (Update 1 Issue)
```bash
npm run sync:test
```
**When to use:**
- After dry run looks good
- User wants to verify one change
- Testing after config changes
- User is cautious

**What it does:**
- Updates ONLY the first issue that needs translation
- Makes real changes to Backlog
- User can verify in Backlog UI: https://hblab.backlogtool.com/view/HB21373-XXX
- Generates report for 1 issue

### 3. Production Sync (Update All)
```bash
npm run sync
```
**When to use:**
- After dry run + test mode verification
- User is confident about changes
- Recurring sync operations
- Batch updates

**What it does:**
- Updates ALL issues that need translation
- Makes real changes to Backlog
- Takes ~15-30 seconds for 50 issues
- Generates full report

## Configuration

The workflow is configured via `workflow/config.json`:

```json
{
  "backlog": {
    "projectId": 47358,        // Which project to sync
    "projectKey": "HB21373"    // Project key (for display)
  },
  "filters": {
    "statusId": [1, 2, 3],     // 1=Open, 2=In Progress, 3=Resolved, 4=Closed
    "createdSince": "2025-10-01",  // Only issues created after this date
    "count": 100               // Max issues to fetch
  },
  "translation": {
    "format": "VN/EN -- JP",   // Translation format
    "enableCache": true        // Use translation cache
  },
  "execution": {
    "dryRun": false,           // Override: preview mode
    "delayBetweenUpdates": 200,    // Rate limiting (ms)
    "testWithOneIssue": false  // Override: test mode
  }
}
```

### When to Modify Config

**User wants different project:**
```json
{
  "backlog": {
    "projectId": 12345,        // Change this
    "projectKey": "PROJ"       // Change this
  }
}
```

**User wants different statuses (e.g., only open issues):**
```json
{
  "filters": {
    "statusId": [1],           // Only status 1 (Open)
    "createdSince": "2025-10-01",
    "count": 100
  }
}
```

**User wants all issues (no date filter):**
```json
{
  "filters": {
    "statusId": [1, 2, 3],
    // Remove "createdSince" line completely
    "count": 100
  }
}
```

## Translation System

The workflow uses `workflow/translator.ts` with 2-layer translation:

### 1. Dictionary Layer (Instant)

Common phrases are pre-translated:

```typescript
'UAT' → 'UAT'
'Chốt Release' → 'リリース確定'
'Làm user manual' → 'ユーザーマニュアル作成'
'Viết test case' → 'テストケース作成'
'Coding' → 'コーディング'
```

### 2. Cache Layer (Automatic)

All translations are cached in `workflow/translation-cache.json`:

```json
{
  "Monitoring RPA": "RPA監視",
  "Update file spec": "仕様書更新",
  "Review với team": "チームレビュー"
}
```

**Cache benefits:**
- Speeds up repeated runs
- Ensures consistency
- Avoids re-translating same text

**To clear cache:**
```bash
rm workflow/translation-cache.json
```

### When Translation Fails

If translator doesn't know a phrase, it returns:
```
[要翻訳] Original Text
```

**What to do:**
1. Add translation to `workflow/translator.ts` in the `commonTranslations` dictionary
2. Re-run the workflow
3. Cache will remember the new translation

## Reports

Each run generates: `workflow/sync-report-{timestamp}.json`

**Report structure:**
```json
{
  "timestamp": "2025-11-14T03:20:00.000Z",
  "summary": {
    "total": 43,
    "needsTranslation": 32,
    "updated": 32,
    "failed": 0,
    "alreadyCorrect": 11
  },
  "issues": [
    {
      "issueKey": "HB21373-383",
      "originalSummary": "Chốt Release",
      "formattedSummary": "Chốt Release -- リリース確定",
      "needsTranslation": true,
      "updated": true
    }
  ]
}
```

**How to use reports:**
- Check `summary.failed` - If >0, investigate errors
- Review `issues` array to see what changed
- Share with user if they ask "what was updated?"

## Typical Workflow (Claude's Actions)

### Scenario 1: User's First Time

```
User: "Can you sync all RPA issues to bilingual format?"

Claude's response:
1. Explain what the workflow does
2. Run: npm run sync:dry
3. Show preview of changes from output
4. Ask: "This will update X issues. Should I proceed with test mode (1 issue) or full sync?"
5. Wait for user confirmation
6. Run: npm run sync:test OR npm run sync
7. Show results and report location
```

### Scenario 2: User Knows the Workflow

```
User: "Run the sync"

Claude's response:
1. Run: npm run sync
2. Show progress output
3. Show summary at end
4. Mention report file location
```

### Scenario 3: User Wants Custom Filters

```
User: "Sync only closed issues from last week"

Claude's response:
1. Edit workflow/config.json:
   - Change statusId to [4]
   - Change createdSince to last week's date
2. Run: npm run sync:dry
3. Show preview
4. Ask user to confirm
5. Run: npm run sync if confirmed
```

## Error Handling

### Error: "Authentication failure"
**Fix:** Check `.env` file has correct `BACKLOG_API_KEY`

### Error: "No translation found for: XYZ"
**Fix:** Add translation to `workflow/translator.ts` in `commonTranslations` object

### Error: Updates failing with 400 error
**Fix:** Check sync report for error details. Usually special characters in summary.

### Error: Rate limiting (429)
**Fix:** Increase `delayBetweenUpdates` in config.json to 500 or 1000

## Performance Metrics

- **Fetch**: ~1 second for 100 issues
- **Translation**: ~0.1s cached, ~0.5s new
- **Update**: ~0.2s per issue (with rate limiting)
- **Total for 50 issues**: ~15-30 seconds

## File Structure Reference

```
workflow/
├── CLAUDE.md                  # This file - Instructions for Claude
├── README.md                  # Human documentation
├── config.json                # Configuration settings
├── backlog-sync.ts            # Main automation script
├── translator.ts              # Translation service
├── translation-cache.json     # Auto-generated cache
└── sync-report-*.json         # Auto-generated reports
```

## Relationship with Other Tools

**This workflow is built on top of:**
- `src/backlog-client.ts` - Token-efficient API client
- MCP tools (indirectly) - For small metadata queries
- BacklogClient.getIssuesFiltered() - For fetching issues

**When to use each:**
| Tool | Use Case |
|------|----------|
| **Workflow** (`npm run sync`) | Batch update all issues to bilingual format |
| **BacklogClient** (one-off scripts) | Custom queries, data analysis, one-time operations |
| **MCP tools** (conversation) | Quick lookups, counts, metadata queries |

## Key Success Criteria

After running workflow successfully:

✅ All issues have format: `[Vietnamese/English] -- [Japanese]`

Examples:
- `Chốt Release -- リリース確定`
- `Làm user manual -- ユーザーマニュアル作成`
- `Update 3 scenario liên quan đến Zendesk -- Zendesk関連の3つのシナリオを更新`

❌ Issues that would still need attention:
- Issues with only Japanese (rare, workflow skips these with warning)
- Issues with special characters causing API errors (reported in sync report)

## Communication Tips

**When explaining to user:**
- Mention token optimization: "This fetches and filters efficiently, ~99% token reduction"
- Show before/after examples from dry run output
- Explain safety: "We can preview first, then test with 1 issue, then run full sync"
- Reference report: "Full details saved to workflow/sync-report-XXX.json"

**What NOT to say:**
- Don't say "I'll update all issues" without offering dry run first
- Don't modify translator.ts without explaining what you're adding
- Don't change config.json without showing user the changes
