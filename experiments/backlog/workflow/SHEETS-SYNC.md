# Backlog to Google Sheets Sync Workflow

Automated workflow to sync Backlog issues to Google Sheets.

## Purpose

This workflow fetches specific issues from Backlog (project HB21373) and syncs them to a Google Sheet, keeping the sheet up to date with the latest issue summaries.

## Quick Start

### 1. Configure Issue Keys

Edit `workflow/sheets-sync-config.json` and add your issue keys:

```json
{
  "issueKeys": [
    "HB21373-399",
    "HB21373-397",
    "HB21373-394"
  ]
}
```

### 2. Preview Changes (Dry Run)

```bash
npm run sheets:sync:dry
```

This shows what will be updated without making changes.

### 3. Test with One Issue

```bash
npm run sheets:sync:test
```

This updates only the first issue so you can verify in Google Sheets.

### 4. Sync All Issues

```bash
npm run sheets:sync
```

This updates all configured issues in Google Sheets.

## Commands

| Command | Description | When to Use |
|---------|-------------|-------------|
| `npm run sheets:sync:dry` | Preview mode - no changes | First time, or to check what will change |
| `npm run sheets:sync:test` | Update 1 issue only | To verify before full sync |
| `npm run sheets:sync` | Update all issues | Production sync |

## Configuration

Edit `workflow/sheets-sync-config.json`:

### Required Settings

```json
{
  "backlog": {
    "projectId": 47358,
    "projectKey": "HB21373"
  },
  "googleSheets": {
    "spreadsheetId": "1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo",
    "sheetName": "スケジュール",
    "range": "E5:E100",
    "credentialsFile": "ggsheet-mcp-09921a7c3245.json"
  },
  "issueKeys": [
    "HB21373-xxx",
    "HB21373-yyy"
  ],
  "execution": {
    "dryRun": false,
    "testWithOneIssue": false
  }
}
```

### Configuration Options

**`issueKeys`** (required)
- Array of issue keys to sync
- Format: `["HB21373-399", "HB21373-397"]`
- Can include both HB21373-XXX and COE-XXX format

**`googleSheets.spreadsheetId`**
- The Google Sheets spreadsheet ID (from URL)
- Default: `1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo`

**`googleSheets.sheetName`**
- The sheet tab name
- Default: `スケジュール`

**`googleSheets.range`**
- Cell range to update (E.g., `E5:E100`)
- Default: `E5:E100`

**`googleSheets.credentialsFile`**
- Service account credentials file
- Default: `ggsheet-mcp-09921a7c3245.json`

## How It Works

### 1. Fetch from Backlog

The workflow fetches issues from Backlog using the issue keys:

```
Input: ["HB21373-399", "HB21373-397"]
  ↓
Backlog API
  ↓
Output:
  - HB21373-399: "Điều tra issue duplicate import vào V-ONE -- V-ONE2重インポートの原因調査"
  - HB21373-397: "Tạm dừng một phần flow quản lý và báo cáo dòng tiền -- COE-181【経財部001】..."
```

### 2. Match with Existing Rows

The workflow reads the Google Sheet and matches issue keys:

```
Sheet Row E24: "HB21373-342 Coding"
  ↓
Extract issue key: "HB21373-342"
  ↓
Match with Backlog data
  ↓
Update if changed, skip if same
```

### 3. Update Google Sheet

**For existing issues:**
- Finds the row with the issue key
- Updates with new summary
- Format: `{IssueKey} {Summary}`

**For new issues:**
- Finds next empty row
- Adds the issue
- Format: `{IssueKey} {Summary}`

## Output Format

Each cell in the sheet will have:

```
{IssueKey} {Summary}
```

Examples:
```
HB21373-399 Điều tra issue duplicate import vào V-ONE -- V-ONE2重インポートの原因調査
HB21373-397 Tạm dừng một phần flow quản lý và báo cáo dòng tiền -- COE-181【経財部001】...
HB21373-394 Monitoring RPA 2025/11/01 ~ 2025/11/30 -- RPA監視
```

## Reports

Each run generates a report: `workflow/sheets-sync-report-{date}.json`

Example report:
```json
{
  "timestamp": "2025-11-14T07:30:00.000Z",
  "mode": "production",
  "summary": {
    "total": 10,
    "added": 3,
    "updated": 5,
    "skipped": 2,
    "failed": 0
  },
  "results": [
    {
      "issueKey": "HB21373-399",
      "summary": "Điều tra issue duplicate import vào V-ONE -- V-ONE2重インポートの原因調査",
      "action": "updated",
      "row": 90
    }
  ]
}
```

## Common Workflows

### Workflow 1: Sync New Issues

```bash
# 1. Edit config and add new issue keys
nano workflow/sheets-sync-config.json

# 2. Preview changes
npm run sheets:sync:dry

# 3. Test with one issue
npm run sheets:sync:test

# 4. Sync all
npm run sheets:sync
```

### Workflow 2: Update Existing Issues

The workflow automatically detects if an issue already exists in the sheet and updates it.

```bash
# Run sync - it will update existing rows
npm run sheets:sync
```

### Workflow 3: Verify Changes

```bash
# 1. Run dry mode to see what will change
npm run sheets:sync:dry

# 2. Check the report
cat workflow/sheets-sync-report-*.json
```

## Troubleshooting

### Error: "Permission denied"

**Solution:** Make sure the spreadsheet is shared with the service account:
```
mcp-sheets-service@ggsheet-mcp.iam.gserviceaccount.com
```

### Error: "Issue not found"

**Solution:** Check that the issue key exists in Backlog project HB21373:
```
https://hblab.backlogtool.com/view/{ISSUE_KEY}
```

### Error: "Sheet not found"

**Solution:** Verify the sheet name in config matches the actual sheet tab name.

### Issues not updating

**Solution:**
1. Run dry mode to see what's detected
2. Check the issue key format in the sheet
3. Ensure issue keys are at the start of the cell

## Authentication

The workflow uses:
- **Backlog API Key** from `.env` (`BACKLOG_API_KEY`)
- **Google Service Account** from `ggsheet-mcp-09921a7c3245.json`

Make sure both are configured correctly.

## Best Practices

1. **Always run dry mode first** when syncing new issues
2. **Use test mode** when unsure about changes
3. **Review reports** after each sync to verify results
4. **Keep issue keys updated** in config as new issues are created
5. **Share the spreadsheet** with the service account before syncing

## Integration with Other Workflows

This workflow is separate from but complementary to:

- **Backlog Sync** (`npm run sync`) - Updates Backlog issue summaries to bilingual format
- **Manual Scripts** - For one-off updates or custom operations

**Typical flow:**
1. Update issues in Backlog using `npm run sync`
2. Sync to Google Sheets using `npm run sheets:sync`

## File Structure

```
workflow/
├── backlog-to-sheets.ts         # Main sync script
├── sheets-sync-config.json      # Configuration file
├── SHEETS-SYNC.md              # This documentation
└── sheets-sync-report-*.json   # Auto-generated reports
```

## Example: Complete Sync Process

```bash
# Step 1: Edit config with issue keys you want to sync
nano workflow/sheets-sync-config.json
# Add: ["HB21373-399", "HB21373-397", "HB21373-394"]

# Step 2: Preview what will happen
npm run sheets:sync:dry
# Output: Shows 3 issues will be added/updated

# Step 3: Test with first issue
npm run sheets:sync:test
# Check Google Sheets to verify it looks correct

# Step 4: Sync all issues
npm run sheets:sync
# Output: Updated 3 cells successfully

# Step 5: Verify in Google Sheets
# Open: https://docs.google.com/spreadsheets/d/1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo/edit

# Step 6: Check report
cat workflow/sheets-sync-report-*.json | jq .summary
```

## Notes

- Issue keys must start with `HB21373-` or `COE-`
- Summaries can be in any format (Vietnamese, Japanese, bilingual)
- The workflow preserves issue keys in cells
- Empty rows are automatically filled with new issues
