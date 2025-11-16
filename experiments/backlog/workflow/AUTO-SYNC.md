# 🤖 Proactive Auto-Sync Workflow

**Intelligent, automated syncing** - No manual configuration needed!

## What Makes This "Proactive"?

Instead of manually specifying which issues to sync (like n8n hardcoded workflows), this workflow **automatically evaluates** and **intelligently decides** what needs syncing.

### Traditional Approach (Hardcoded) ❌
```json
{
  "issueKeys": ["HB21373-399", "HB21373-397"]  // Manual input required
}
```

### Proactive Approach (Automated) ✅
```bash
npm run sheets:auto
```
The workflow:
1. 📥 **Fetches ALL issues** from Backlog project automatically
2. 🔍 **Evaluates each issue**:
   - Does it have bilingual format? (VN/EN -- JP)
   - Is it already in the Google Sheet?
   - Does the sheet version match Backlog?
3. 🎯 **Automatically syncs only what needs updating**

## Quick Start

### 1. Preview What Needs Syncing

```bash
npm run sheets:auto:dry
```

**Output:**
```
🔍 Evaluating issues...

✓ HB21373-399
   Status: Already synced and up to date
   Action: SKIP

🔄 HB21373-394
   Status: Sheet value differs from Backlog
   Action: UPDATE
   Old: HB21373-394 Monitoring RPA 2025/11/01 ~ 2025/11/30
   New: HB21373-394 Monitoring RPA 2025/11 -- 2025/11 RPA監視

🔄 HB21373-389
   Status: Has bilingual format, needs to be added to sheet
   Action: ADD
   Value: HB21373-389 Update file spec và version control...

📊 Evaluation Summary
  Total issues: 96
  Has bilingual format: 38
  Already in sheet: 65
  Needs syncing: 9
    - To add: 7
    - To update: 2
```

### 2. Run Auto-Sync

```bash
npm run sheets:auto
```

The workflow syncs only the issues that need it!

## Intelligence Features

### 🎯 Smart Evaluation

For each issue, the workflow evaluates:

| Check | What It Means |
|-------|---------------|
| **Has bilingual format?** | Does it have `VN/EN -- JP` format? |
| **Exists in sheet?** | Is it already in Google Sheets? |
| **Values match?** | Does sheet value = Backlog value? |

### 🧠 Decision Logic

```
Issue HB21373-XXX
    │
    ├─ No bilingual format (VN -- JP)?
    │  → SKIP: "Missing bilingual format"
    │
    ├─ Has bilingual format + NOT in sheet?
    │  → ADD: "Has bilingual format, needs to be added"
    │
    ├─ In sheet but value differs?
    │  → UPDATE: "Sheet value differs from Backlog"
    │
    └─ In sheet and values match?
       → SKIP: "Already synced and up to date"
```

### 🎨 Visual Feedback

- ✅ **Green ✓** - Already correct, no action needed
- 🔄 **Yellow 🔄** - Needs syncing (add/update)

## Configuration

Edit `workflow/sheets-sync-config.json`:

```json
{
  "filters": {
    "statusId": [1, 2, 3, 4],      // Which statuses to scan
    "createdSince": "2025-10-01",  // Only issues after this date
    "count": 100                    // Max issues to fetch
  }
}
```

### Filter Options

| Filter | Values | Description |
|--------|--------|-------------|
| `statusId` | `[1, 2, 3, 4]` | 1=Open, 2=In Progress, 3=Resolved, 4=Closed |
| `createdSince` | `"2025-10-01"` | Only issues created after this date |
| `count` | `100` | Maximum number of issues to fetch |

## Comparison: Manual vs Auto

### Manual Workflow (sheets:sync)

```bash
# 1. Edit config - specify issue keys manually
code workflow/sheets-sync-config.json
# Add: ["HB21373-399", "HB21373-397", ...]

# 2. Run sync
npm run sheets:sync
```

**Use when:** You know exactly which issues to sync

### Auto Workflow (sheets:auto) ✨

```bash
# Just run it - no manual configuration!
npm run sheets:auto
```

**Use when:**
- You want to sync ALL issues that need it
- You don't want to manually maintain issue key lists
- You want automatic evaluation of what needs syncing

## What Gets Synced?

Only issues with **bilingual format** (`VN/EN -- JP`):

✅ **Will be synced:**
```
Điều tra issue duplicate import -- V-ONE2重インポートの原因調査
Monitoring RPA 2025/11 -- 2025/11 RPA監視
Update file spec và version control -- ファイル仕様とバージョン管理を更新
```

❌ **Will NOT be synced** (skipped):
```
Monitoring RPA 2025/10/06 ~ 2025/10/31  (No Japanese)
仕様書作成  (Only Japanese)
Update spec  (No Japanese)
```

## Example Workflow

### Scenario: Keep Google Sheet Synced Daily

```bash
# Morning: Check what needs syncing
npm run sheets:auto:dry

# If evaluation looks good, run sync
npm run sheets:auto
```

### Scenario: After Batch Translation

```bash
# 1. Update Backlog issues to bilingual format
npm run sync

# 2. Auto-sync bilingual issues to Google Sheets
npm run sheets:auto
```

## Reports

Each run generates a detailed report:

**File:** `workflow/sheets-auto-sync-report-{date}.json`

```json
{
  "timestamp": "2025-11-14T08:00:00.000Z",
  "mode": "production",
  "summary": {
    "totalIssues": 96,
    "hasBilingualFormat": 38,
    "alreadyInSheet": 65,
    "synced": 9,
    "added": 7,
    "updated": 2
  },
  "evaluations": [
    {
      "issueKey": "HB21373-394",
      "summary": "Monitoring RPA 2025/11 -- 2025/11 RPA監視",
      "hasBilingualFormat": true,
      "existsInSheet": true,
      "sheetRow": 33,
      "sheetValue": "HB21373-394 Monitoring RPA 2025/11/01...",
      "needsSync": true,
      "reason": "Sheet value differs from Backlog",
      "action": "update"
    }
  ]
}
```

## Advanced: Customizing Evaluation Logic

The bilingual format check looks for:
- **Separator:** ` -- ` (space-dash-dash-space)
- **Pattern:** `[Vietnamese/English] -- [Japanese]`

This is defined in the `hasBilingualFormat()` method.

## Benefits Over Hardcoded Workflows

| Feature | Hardcoded (n8n style) | Proactive (Auto) |
|---------|----------------------|------------------|
| **Manual config** | ❌ Need to specify each issue | ✅ Automatic detection |
| **Scalability** | ❌ Grows with issue count | ✅ Handles any number |
| **Maintenance** | ❌ Update config constantly | ✅ Zero maintenance |
| **Intelligence** | ❌ No evaluation logic | ✅ Smart decision making |
| **Flexibility** | ❌ Fixed list | ✅ Dynamic based on filters |

## Commands Reference

```bash
# Auto-sync with evaluation
npm run sheets:auto           # Sync what needs updating
npm run sheets:auto:dry       # Preview evaluation only

# Manual sync (for specific issues)
npm run sheets:sync           # Sync hardcoded issue keys
npm run sheets:sync:dry       # Preview specific issues
```

## Troubleshooting

### "No issues found"

Check filters in config:
```json
{
  "filters": {
    "statusId": [1, 2, 3, 4],  // Include all statuses
    "createdSince": "2025-10-01"  // Adjust date
  }
}
```

### "Needs syncing: 0"

All issues are either:
- Already synced ✅
- Don't have bilingual format yet

Run bilingual sync first:
```bash
npm run sync  # Update Backlog to bilingual
npm run sheets:auto  # Then sync to sheets
```

## Integration with Other Workflows

### Complete Bilingual Workflow

```bash
# 1. Translate issues in Backlog to bilingual format
npm run sync:dry        # Preview
npm run sync            # Update Backlog

# 2. Auto-sync bilingual issues to Google Sheets
npm run sheets:auto:dry # Preview
npm run sheets:auto     # Sync to sheets
```

Now both Backlog AND Google Sheets have bilingual format! 🎉

## Why This Is Better

**Traditional n8n workflow:**
```
❌ Hardcode issue keys
❌ Manual trigger per issue
❌ No evaluation logic
❌ High maintenance
```

**Proactive auto-sync:**
```
✅ Automatic discovery
✅ Single command for all
✅ Intelligent evaluation
✅ Zero maintenance
```

## Summary

🚀 **One command** to keep Google Sheets synced:
```bash
npm run sheets:auto
```

The workflow automatically:
1. Fetches all issues from Backlog
2. Evaluates what needs syncing
3. Syncs only what changed
4. Generates detailed report

**No manual configuration. No hardcoded lists. Just intelligent automation.** 🤖
