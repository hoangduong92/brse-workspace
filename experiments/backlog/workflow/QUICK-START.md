# Quick Start: Backlog to Google Sheets Sync

## 🚀 3-Step Workflow

### Step 1: Edit Config

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

### Step 2: Preview Changes

```bash
npm run sheets:sync:dry
```

This shows what will be updated without making any changes.

### Step 3: Run Sync

```bash
npm run sheets:sync
```

This updates the Google Sheet with the issue summaries from Backlog.

## ✅ What It Does

1. **Fetches** issues from Backlog using the issue keys you provide
2. **Matches** them with existing rows in the Google Sheet
3. **Updates** the sheet with the latest summaries
4. **Adds** new issues to empty rows if they don't exist yet

## 📋 Output Format

Each cell will have:
```
{IssueKey} {Summary}
```

Example:
```
HB21373-399 Điều tra issue duplicate import vào V-ONE -- V-ONE2重インポートの原因調査
```

## 🔧 Available Commands

| Command | What It Does |
|---------|--------------|
| `npm run sheets:sync:dry` | **Preview mode** - See what will change |
| `npm run sheets:sync:test` | **Test mode** - Update only 1 issue |
| `npm run sheets:sync` | **Production** - Update all issues |

## 🎯 Example Workflow

```bash
# 1. Add issue keys to config
code workflow/sheets-sync-config.json

# 2. Preview changes
npm run sheets:sync:dry

# 3. Test with 1 issue
npm run sheets:sync:test

# 4. Sync all
npm run sheets:sync
```

## 📊 Reports

Each run creates a report:
```
workflow/sheets-sync-report-{date}.json
```

Check it to see exactly what was updated.

## ⚙️ Configuration File

Location: `workflow/sheets-sync-config.json`

**What you need to change:**
```json
{
  "issueKeys": [
    "HB21373-xxx",    // ← Add your issue keys here
    "HB21373-yyy"
  ]
}
```

**What you usually don't need to change:**
```json
{
  "googleSheets": {
    "spreadsheetId": "1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo",
    "sheetName": "スケジュール",
    "range": "E5:E100"
  }
}
```

## 🔍 How It Works

```
Config: issueKeys
    ↓
Fetch from Backlog
    ↓
Read Google Sheet
    ↓
Match by issue key
    ↓
Update/Add to sheet
```

## ✨ Smart Features

- ✅ **Detects existing issues** - Updates them instead of duplicating
- ✅ **Finds empty rows** - Adds new issues automatically
- ✅ **Preserves issue keys** - Keeps the `HB21373-XXX` prefix
- ✅ **Dry run mode** - Preview before making changes
- ✅ **Test mode** - Verify with 1 issue first

## 🆘 Troubleshooting

**No issues found?**
- Check that issue keys exist in Backlog
- Verify `.env` has `BACKLOG_API_KEY`

**Permission denied on Google Sheets?**
- Make sure spreadsheet is shared with:
  ```
  mcp-sheets-service@ggsheet-mcp.iam.gserviceaccount.com
  ```

**Issues not updating?**
- Run dry mode first: `npm run sheets:sync:dry`
- Check the report file for errors

## 📖 Full Documentation

See [SHEETS-SYNC.md](./SHEETS-SYNC.md) for complete documentation.
