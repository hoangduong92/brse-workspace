# Issue Initing Workflow

Automatically creates 8 standard child issues for a parent issue in Backlog.

## Overview

This workflow streamlines the process of setting up a standard project workflow by automatically creating 8 child issues with predefined summaries. Perfect for initializing RPA projects or any standardized workflow.

## Standard Child Issues

The workflow creates the following 8 child issues in order:

1. **要件ヘアリング　-- Hearing yêu cầu** (Requirements Hearing)
2. **要件定義書作成　-- Làm file spec** (Create Specification Document)
3. **開発　-- Coding** (Development)
4. **テストケース作成  --  Tạo test case** (Create Test Cases)
5. **テスト実施 -- Thực thi test** (Execute Tests)
6. **UAT** (User Acceptance Testing)
7. **リリース判定 -- Release** (Release Decision)
8. **ユーザマニュアル作成 -- Làm user manual** (Create User Manual)

## Usage

### Basic Usage

Create child issues for a parent issue:

```bash
npm run issue:init -- HB21373-420
```

### Dry Run Mode (Preview)

Preview what will be created without making actual changes:

```bash
npm run issue:init -- HB21373-420 --dry-run
```

**Recommended:** Always run in dry-run mode first to verify the parent issue details.

### Show Help

Display usage information:

```bash
npm run issue:init -- --help
```

## Workflow Steps

When you run the command, the workflow:

1. **Validates Parent Issue**
   - Fetches the parent issue to ensure it exists
   - Displays parent issue details (key, summary, project, issue type, priority)

2. **Determines Issue Type**
   - Automatically finds the "Subtask" issue type for the project
   - Falls back to default issue type if Subtask is not available

3. **Creates Child Issues**
   - Creates 8 child issues with predefined summaries
   - Links each as a child of the parent issue
   - Uses same project and priority as parent
   - 200ms delay between API calls to avoid rate limiting

4. **Displays Summary**
   - Shows all created issues with their keys
   - Provides link to view parent issue in Backlog

## Example Session

```bash
$ npm run issue:init -- HB21373-420 --dry-run

🔍 Fetching parent issue: HB21373-420...

✅ Parent Issue Found:
   Key: HB21373-420
   Summary: New RPA Project for CS Department
   Project: 47358
   Issue Type: Task (ID: 203596)
   Priority: Normal (ID: 3)

🔍 [DRY RUN] Creating 8 child issues...

📋 Using issue type: Subtask (ID: 203777)

   1. Creating: 要件ヘアリング　-- Hearing yêu cầu...
      ✅ Created: DRY-RUN
   2. Creating: 要件定義書作成　-- Làm file spec...
      ✅ Created: DRY-RUN
   ... (6 more issues)

═══════════════════════════════════════════════════
📋 DRY RUN SUMMARY
═══════════════════════════════════════════════════

📦 Parent Issue: HB21373-420
   New RPA Project for CS Department

📝 Created 8 child issues:

   1. DRY-RUN - 要件ヘアリング　-- Hearing yêu cầu
   2. DRY-RUN - 要件定義書作成　-- Làm file spec
   ... (6 more)

═══════════════════════════════════════════════════

💡 Run without --dry-run flag to create issues
```

After verifying, run without `--dry-run` to create actual issues:

```bash
$ npm run issue:init -- HB21373-420

🔍 Fetching parent issue: HB21373-420...
✅ Parent Issue Found: ...

🚀 Creating 8 child issues...
   1. Creating: 要件ヘアリング　-- Hearing yêu cầu...
      ✅ Created: HB21373-421
   2. Creating: 要件定義書作成　-- Làm file spec...
      ✅ Created: HB21373-422
   ... (6 more issues)

═══════════════════════════════════════════════════
✅ SUCCESS SUMMARY
═══════════════════════════════════════════════════

📦 Parent Issue: HB21373-420
   New RPA Project for CS Department

📝 Created 8 child issues:

   1. HB21373-421 - 要件ヘアリング　-- Hearing yêu cầu
   2. HB21373-422 - 要件定義書作成　-- Làm file spec
   ... (6 more)

═══════════════════════════════════════════════════

🔗 View parent issue: https://hblab.backlogtool.com/view/HB21373-420
```

## Requirements

- Node.js with TypeScript support
- `.env` file with:
  - `BACKLOG_DOMAIN` (e.g., `hblab.backlogtool.com`)
  - `BACKLOG_API_KEY` (API key with write permissions)
- Parent issue must exist in Backlog
- API key must have permission to create issues in the project

## Error Handling

### Issue Not Found (404)
```
❌ Error: Issue HB21373-999 not found. Please check the issue key.
```
**Solution:** Verify the parent issue key exists in Backlog.

### Missing Environment Variables
```
❌ Error: Missing environment variables
Please ensure .env file contains:
  - BACKLOG_DOMAIN
  - BACKLOG_API_KEY
```
**Solution:** Check `.env` file has both required variables.

### Permission Denied (401/403)
```
❌ Failed to create issue: 403 Forbidden
```
**Solution:** Ensure API key has write permissions for the project.

### Rate Limiting (429)
The workflow includes 200ms delay between API calls to avoid rate limiting. If you still encounter rate limiting, the workflow will stop and report the error.

## Features

✅ **Safe Preview Mode** - Dry run shows what will be created without changes
✅ **Automatic Issue Type Detection** - Finds Subtask type automatically
✅ **Parent-Child Linking** - All issues linked as children of parent
✅ **Bilingual Summaries** - Vietnamese/English -- Japanese format
✅ **Rate Limiting Protection** - 200ms delay between API calls
✅ **Error Handling** - Clear error messages with solutions
✅ **Progress Display** - Shows each step in real-time

## Use Cases

1. **New RPA Project Setup**
   ```bash
   # Create parent issue first, then run:
   npm run issue:init -- HB21373-XXX
   ```

2. **Standardized Workflow Initialization**
   - Any project requiring the 8-step workflow
   - Consistent task structure across projects

3. **Quick Project Scaffolding**
   - Set up all child issues in seconds
   - No manual creation needed

## Customization

To modify the standard child issues, edit `workflow/issue-init.ts`:

```typescript
const CHILD_ISSUES_TEMPLATE = [
  { order: 1, summary: '要件ヘアリング　-- Hearing yêu cầu' },
  { order: 2, summary: '要件定義書作成　-- Làm file spec' },
  // ... modify or add more issues here
];
```

## Related Workflows

- **`npm run sync`** - Sync issue summaries to bilingual format
- **`npm run sheets:sync`** - Export issues to Google Sheets

## Technical Details

- **API Endpoint:** `POST /api/v2/issues`
- **Issue Type:** Automatically detects Subtask type
- **Priority:** Inherits from parent issue
- **Rate Limiting:** 200ms delay between requests
- **Execution Time:** ~2-3 seconds for 8 issues

## Troubleshooting

**Q: Child issues are created but not linked to parent?**
A: Check if the `parentIssueId` parameter is correctly set. Re-run in dry-run mode to verify.

**Q: Wrong issue type is being used?**
A: The workflow auto-detects "Subtask" type. If your project uses a different name, modify the `getSubtaskIssueTypeId` function.

**Q: Can I change the order of child issues?**
A: Yes, modify the `order` field in `CHILD_ISSUES_TEMPLATE` array.

## Support

For issues or questions:
1. Check error messages for specific solutions
2. Run in `--dry-run` mode first to diagnose
3. Verify `.env` configuration
4. Ensure API key has correct permissions
