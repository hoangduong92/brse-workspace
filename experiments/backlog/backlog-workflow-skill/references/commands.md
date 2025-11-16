# Command Reference

Complete reference for all available commands in the Backlog Workflow SKILL.

## Setup Commands

### Verify Setup
```bash
cd backlog/backlog-workflow-skill/scripts
npx tsx verify-setup.ts
```

**What it does:**
- Checks environment variables (.env)
- Validates user-config.json
- Tests Backlog API connection
- Verifies translation dictionary exists
- Confirms Google Sheets config (if configured)

**When to use:**
- After initial setup
- When troubleshooting issues
- After modifying configuration
- Before running workflows

## Bilingual Translation Sync Commands

### Dry Run (Preview Mode)
```bash
npm run sync:dry
```

**What it does:**
- Fetches issues from Backlog
- Shows before/after for each issue that needs translation
- Does NOT make any changes to Backlog
- Generates report showing what would change

**When to use:**
- First time running workflow
- Want to preview changes
- Testing filter configurations
- Before large batch updates

**Example output:**
```
📥 Fetching issues from Backlog...
✅ Fetched 43 issues

🔄 Processing issues...

📝 [HB21373-383]
   Before: Chốt Release
   After:  Chốt Release -- リリース確定

🔍 DRY RUN MODE - No actual updates will be made
📊 Would update: 32 issues
```

### Test Mode (Update 1 Issue)
```bash
npm run sync:test
```

**What it does:**
- Updates ONLY the first issue that needs translation
- Makes real changes to Backlog
- Useful for verification before full sync

**When to use:**
- After dry run looks good
- Want to verify one change in Backlog UI
- Testing after config changes
- Being extra cautious

**Example output:**
```
📥 Fetching issues from Backlog...
✅ Fetched 43 issues

🔄 Processing issues...
📝 [HB21373-383] Chốt Release → Chốt Release -- リリース確定
✅ Updated 1 issue (test mode)

Visit Backlog to verify: https://hblab.backlogtool.com/view/HB21373-383
```

### Production Sync (Update All)
```bash
npm run sync
```

**What it does:**
- Updates ALL issues that need translation
- Makes real changes to Backlog
- Processes entire filtered issue set

**When to use:**
- After dry run + test mode verification
- Confident about changes
- Recurring sync operations
- Batch updates

**Example output:**
```
📥 Fetching issues from Backlog...
✅ Fetched 43 issues

🔄 Processing issues... (32 need translation)

Progress: [████████████████] 32/32 (100%)

✅ Updated 32 issues
❌ Failed: 0
📊 Report: workflow/sync-report-1731571234567.json
```

## Google Sheets Sync Commands

### Manual Sync - Dry Run
```bash
npm run sheets:sync:dry
```

**What it does:**
- Fetches specified issues (from user-config.json)
- Shows what would be updated in Google Sheet
- Does NOT make changes to sheet

**When to use:**
- Preview sheet sync
- Verify issue keys are correct
- Check current sheet contents

### Manual Sync - Test Mode
```bash
npm run sheets:sync:test
```

**What it does:**
- Updates ONLY the first configured issue to the sheet
- Makes real changes to Google Sheets

**When to use:**
- Verify sheet permissions work
- Test sheet range is correct
- Check format in sheet

### Manual Sync - Production
```bash
npm run sheets:sync
```

**What it does:**
- Syncs all configured issues to Google Sheets
- Updates existing entries or adds new ones

**When to use:**
- Specific set of issues to sync
- Custom issue list maintained in config

**Configuration:**
Add issue keys to `workflow/user-config.json`:
```json
{
  "sheetsSync": {
    "issueKeys": ["HB21373-399", "HB21373-397", "HB21373-394"]
  }
}
```

### Auto Sync - Dry Run
```bash
npm run sheets:auto:dry
```

**What it does:**
- Fetches ALL issues from Backlog
- Evaluates which need syncing:
  - Has bilingual format?
  - Already in sheet?
  - Values match?
- Shows evaluation results
- Does NOT make changes

**When to use:**
- See what would be synced automatically
- Understand current sync state
- Check bilingual format coverage

**Example output:**
```
🔍 Evaluating issues...

✓ HB21373-399
   Status: Already synced and up to date
   Action: SKIP

🔄 HB21373-394
   Status: Sheet value differs from Backlog
   Action: UPDATE
   Old: HB21373-394 Monitoring RPA 2025/11/01
   New: HB21373-394 Monitoring RPA 2025/11 -- RPA監視

🔄 HB21373-389
   Status: Has bilingual format, needs to be added
   Action: ADD

📊 Evaluation Summary
  Total issues: 96
  Has bilingual format: 38
  Needs syncing: 9 (7 add, 2 update)
```

### Auto Sync - Production
```bash
npm run sheets:auto
```

**What it does:**
- Evaluates ALL issues
- Syncs only issues with bilingual format
- Automatically adds new issues
- Updates changed issues
- Skips issues without bilingual format

**When to use:**
- Daily/weekly sheet sync routine
- After running bilingual sync
- Want intelligent automatic sync
- Don't want to maintain issue key lists

**Advantages over manual sync:**
- ✅ No manual issue key configuration
- ✅ Automatic evaluation logic
- ✅ Only syncs relevant issues
- ✅ Scales to any number of issues

## Combined Workflows

### Complete Bilingual Workflow
```bash
# 1. Preview Backlog translation
npm run sync:dry

# 2. Update Backlog to bilingual format
npm run sync

# 3. Preview sheet sync
npm run sheets:auto:dry

# 4. Sync to Google Sheets
npm run sheets:auto
```

### Safe Progressive Workflow
```bash
# 1. Preview
npm run sync:dry

# 2. Test with 1 issue
npm run sync:test

# 3. Verify in Backlog UI
# Visit: https://hblab.backlogtool.com/view/HB21373-XXX

# 4. If good → Full sync
npm run sync

# 5. Sync to sheets
npm run sheets:auto
```

## Configuration Commands

### View Current Configuration
```bash
cat workflow/user-config.json | jq '.'
```

### Edit Configuration
```bash
code workflow/user-config.json
```

### Reset Translation Cache
```bash
rm workflow/translation-cache.json
```

**When to use:**
- Translations are incorrect
- Dictionary was updated
- Start fresh with translations

### View Latest Report
```bash
# Bilingual sync report
ls -lt workflow/sync-report-*.json | head -1 | xargs cat | jq '.'

# Sheets sync report
ls -lt workflow/sheets-sync-report-*.json | head -1 | xargs cat | jq '.'

# Auto sync report
ls -lt workflow/sheets-auto-sync-report-*.json | head -1 | xargs cat | jq '.'
```

## Advanced Commands

### Custom Filter Sync
Modify filters in user-config.json, then:
```bash
npm run sync:dry   # Preview with new filters
npm run sync        # Apply with new filters
```

**Example filters:**
```json
{
  "filters": {
    "statusId": [4],                      // Only closed issues
    "createdSince": "2025-10-01",
    "createdUntil": "2025-10-31",        // October only
    "count": 200                          // Increase limit
  }
}
```

### Export Current State
```bash
# Export all issues to JSON for backup
npx tsx -e "
import {BacklogClient} from './src/backlog-client.js';
import {writeFileSync} from 'fs';
import dotenv from 'dotenv';
dotenv.config();

const client = new BacklogClient({
  domain: process.env.BACKLOG_DOMAIN,
  apiKey: process.env.BACKLOG_API_KEY
});

const issues = await client.getIssuesFiltered({
  projectId: [47358],
  count: 200
});

writeFileSync('backup-issues.json', JSON.stringify(issues, null, 2));
console.log(\`Exported \${issues.length} issues to backup-issues.json\`);
"
```

## Command Options Summary

| Command | Mode | Changes Backlog? | Changes Sheets? | Use Case |
|---------|------|------------------|-----------------|----------|
| `sync:dry` | Preview | ❌ No | ❌ No | Preview translation |
| `sync:test` | Test | ✅ Yes (1 issue) | ❌ No | Verify translation |
| `sync` | Production | ✅ Yes (all) | ❌ No | Full translation sync |
| `sheets:sync:dry` | Preview | ❌ No | ❌ No | Preview manual sheet sync |
| `sheets:sync:test` | Test | ❌ No | ✅ Yes (1 issue) | Verify sheet sync |
| `sheets:sync` | Production | ❌ No | ✅ Yes (configured) | Manual sheet sync |
| `sheets:auto:dry` | Preview | ❌ No | ❌ No | Preview auto evaluation |
| `sheets:auto` | Production | ❌ No | ✅ Yes (evaluated) | Auto sheet sync |

## Tips and Best Practices

### 1. Always Preview First
```bash
npm run sync:dry        # See what will change
npm run sync:test       # Test with 1 issue
npm run sync            # Full sync
```

### 2. Check Reports After Each Run
```bash
cat workflow/sync-report-*.json | tail -1 | jq '.summary'
```

### 3. Use Auto Sync for Sheets
Prefer `sheets:auto` over `sheets:sync` for easier maintenance:
```bash
npm run sheets:auto     # Intelligent evaluation
# vs
npm run sheets:sync     # Manual issue key list
```

### 4. Regular Verification
```bash
# Before important syncs
npx tsx backlog/backlog-workflow-skill/scripts/verify-setup.ts
```

### 5. Backup Before Large Changes
```bash
# Export current state before major sync
# (see "Export Current State" above)
```

## Troubleshooting Commands

### Check Environment
```bash
cat .env
```

### Verify Config Syntax
```bash
cat workflow/user-config.json | jq '.'
# If output shows JSON → valid
# If error → fix syntax
```

### Test Backlog Connection
```bash
npx tsx backlog/backlog-workflow-skill/scripts/verify-setup.ts
```

### View All Reports
```bash
ls -lh workflow/*-report-*.json
```

### Clear All Cache and Reports
```bash
rm workflow/translation-cache.json
rm workflow/*-report-*.json
```

## NPM Script Reference

All commands are defined in `package.json`:

```json
{
  "scripts": {
    "sync": "tsx backlog/workflow/backlog-sync.ts",
    "sync:dry": "tsx backlog/workflow/backlog-sync.ts --dry-run",
    "sync:test": "tsx backlog/workflow/backlog-sync.ts --test",
    "sheets:sync": "tsx backlog/workflow/backlog-to-sheets.ts",
    "sheets:sync:dry": "tsx backlog/workflow/backlog-to-sheets.ts --dry-run",
    "sheets:sync:test": "tsx backlog/workflow/backlog-to-sheets.ts --test",
    "sheets:auto": "tsx backlog/workflow/backlog-to-sheets-auto.ts",
    "sheets:auto:dry": "tsx backlog/workflow/backlog-to-sheets-auto.ts --dry-run"
  }
}
```
