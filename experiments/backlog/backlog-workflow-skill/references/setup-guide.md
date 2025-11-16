# Setup Guide for New Users

**Complete step-by-step guide for first-time setup**

## Prerequisites

- [x] Node.js installed (v16 or higher)
- [x] Access to a Backlog project
- [x] Backlog API key with write permissions
- [x] (Optional) Access to Google Sheets for sync feature

## Step 1: Environment Setup

Create a `.env` file in the project root:

```env
BACKLOG_DOMAIN=your-space.backlogtool.com
BACKLOG_API_KEY=your_api_key_here
```

**How to get these values:**

### BACKLOG_DOMAIN
1. Visit your Backlog space (e.g., `https://hblab.backlogtool.com`)
2. Copy the domain part: `hblab.backlogtool.com`

### BACKLOG_API_KEY
1. Go to Backlog → Personal Settings → API
2. Click "Generate New Token"
3. Copy the generated token
4. **Important:** This token gives write access - keep it secure!

## Step 2: Interactive Setup (Automatic)

When you first use the SKILL, Claude will ask you for:

### 2.1. Backlog Project Information

**Project ID:**
- Find it in your project settings URL
- Example: `https://hblab.backlogtool.com/projects/47358` → ID is `47358`

**Project Key:**
- Find it in issue keys
- Example: Issue `HB21373-123` → Key is `HB21373`

**Quick way to find both:**
Ask Claude to run:
```bash
npx tsx -e "
import {BacklogClient} from './src/backlog-client.js';
import dotenv from 'dotenv';
dotenv.config();
const client = new BacklogClient({
  domain: process.env.BACKLOG_DOMAIN,
  apiKey: process.env.BACKLOG_API_KEY
});
const projects = await client.listProjects();
console.table(projects.projects.map(p => ({
  id: p.id,
  key: p.projectKey,
  name: p.name
})));
"
```

### 2.2. Google Sheets Information (Optional)

**Only needed if you want to sync with Google Sheets.**

**Spreadsheet ID:**
- From URL: `https://docs.google.com/spreadsheets/d/1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo/edit`
- ID is: `1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo`

**Sheet Name:**
- The tab name (e.g., "Schedule", "スケジュール")

**Range:**
- Where to put issue data (e.g., "E5:E100")

**Permissions:**
Ensure the spreadsheet is shared with:
```
mcp-sheets-service@ggsheet-mcp.iam.gserviceaccount.com
```
(Role: Editor)

### 2.3. Language Pair Selection

Choose based on your team's languages:

| Option | Use When | Example |
|--------|----------|---------|
| `vi-ja` | Vietnamese team → Japanese client | "Chốt Release -- リリース確定" |
| `en-ja` | English team → Japanese client | "Release freeze -- リリース確定" |
| `custom` | Other language combination | Create custom dictionary |

## Step 3: Verify Setup

After Claude creates `workflow/user-config.json`, verify it works:

```bash
cd backlog/backlog-workflow-skill/scripts
npx tsx verify-setup.ts
```

**Expected output:**
```
✅ Environment variables loaded
✅ User configuration found
✅ Connected to Backlog
✅ Found project: HB21373 (ID: 47358)
✅ Translation dictionary loaded: vi-ja
✅ Setup verification complete!
```

**If verification fails:**

### Error: "Missing BACKLOG_API_KEY"
- Check `.env` file exists and has correct variables
- Verify no typos in variable names
- Ensure API key is valid

### Error: "Cannot connect to Backlog"
- Check BACKLOG_DOMAIN is correct
- Verify API key has not expired
- Check network connection

### Error: "user-config.json not found"
- Let Claude run the interactive setup
- Or manually copy from `references/config-template.json`

## Step 4: Test with Dry Run

Run a safe preview to verify everything works:

```bash
npm run sync:dry
```

**Expected output:**
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

If this works, you're ready to use the SKILL!

## Step 5: First Real Update

Test with a single issue first:

```bash
npm run sync:test
```

This updates only 1 issue so you can verify in Backlog UI.

**Verify in Backlog:**
1. Go to your Backlog project
2. Find the updated issue
3. Check that summary is in bilingual format
4. If looks good → proceed with full sync

## Step 6: Full Sync

Once verified, run the full sync:

```bash
npm run sync
```

**Monitor the output:**
- Check for errors
- Review the report file
- Verify issues in Backlog

## Configuration Customization

### Change Which Issues to Process

Edit `workflow/user-config.json`:

```json
{
  "filters": {
    "statusId": [1, 2, 3],           // Which statuses
    "createdSince": "2025-10-01",    // Date filter
    "count": 100                      // Max count
  }
}
```

**Status IDs:**
- `1` = Open
- `2` = In Progress
- `3` = Resolved
- `4` = Closed

### Add Custom Translations

Option 1: Edit dictionary file directly:
```bash
# Edit the file for your language pair
code backlog/backlog-workflow-skill/references/translation-dictionaries/vi-ja.json
```

Option 2: Add to user config:
```json
{
  "translation": {
    "customDictionary": {
      "Your custom phrase": "カスタムフレーズ",
      "Another phrase": "別のフレーズ"
    }
  }
}
```

### Change Translation Format

Default format is `VN/EN -- JP`, but you can customize:

```json
{
  "translation": {
    "format": "SOURCE | TARGET"  // e.g., "Chốt Release | リリース確定"
  }
}
```

## Troubleshooting

### Issue: Translations are incorrect

**Solution:**
1. Check which dictionary is being used
2. Add correct translations to the dictionary
3. Clear translation cache: `rm workflow/translation-cache.json`
4. Re-run sync

### Issue: Some issues not being processed

**Solution:**
1. Check filters in user-config.json
2. Verify issues match the filter criteria
3. Run with `--dry-run` to see what would be processed

### Issue: Google Sheets sync not working

**Solution:**
1. Verify spreadsheet is shared with MCP service account
2. Check spreadsheet ID is correct
3. Ensure sheet name matches exactly (case-sensitive)
4. Verify range is valid (e.g., "E5:E100")

### Issue: Rate limiting errors (429)

**Solution:**
Increase delay in user-config.json:
```json
{
  "execution": {
    "delayBetweenUpdates": 500  // Increase to 500ms or 1000ms
  }
}
```

## Best Practices

### 1. Always Preview First

```bash
npm run sync:dry  # See what will change
npm run sync:test # Test with 1 issue
npm run sync      # Full sync
```

### 2. Regular Backups

Before large batch updates:
```bash
# Export current issues to backup
npm run export:backup
```

### 3. Review Reports

After each sync, check the report:
```bash
cat workflow/sync-report-*.json | tail -1
```

### 4. Keep Dictionaries Updated

When you notice untranslated phrases:
1. Add them to the dictionary
2. Share with team
3. Keep dictionary files in version control

### 5. Use Version Control

**Commit to git:**
- ✅ Dictionary files
- ✅ Config template
- ✅ Scripts

**DO NOT commit:**
- ❌ user-config.json (personal configuration)
- ❌ .env (contains secrets)
- ❌ translation-cache.json (auto-generated)
- ❌ Report files (auto-generated)

## Next Steps

Once setup is complete:

1. **Read workflow patterns:** `references/workflow-patterns.md`
2. **Review commands:** `references/commands.md`
3. **Set up recurring sync:** Schedule weekly syncs
4. **Share with team:** Help teammates set up their own user-config.json

## Getting Help

If you encounter issues:

1. Check this setup guide
2. Review error messages in reports
3. Run verification: `npx tsx verify-setup.ts`
4. Check logs for detailed error information

## Sharing with Team Members

When a colleague wants to use the SKILL:

1. They import/clone the SKILL directory
2. They create their own `.env` file
3. They run interactive setup with Claude
4. They create their own `user-config.json`

**Each user has independent configuration!**

This allows:
- Different projects per user
- Different Google Sheets per user
- Different language pairs per user
- Isolated settings and preferences
