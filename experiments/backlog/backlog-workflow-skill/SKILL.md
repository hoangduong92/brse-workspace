---
name: backlog-workflow
description: Automated Backlog issue management with bilingual translation and Google Sheets sync. On first use, asks for project ID, Sheet ID, and language pair. Use when syncing issues to bilingual format, translating summaries, or keeping Backlog synchronized with Google Sheets. Supports multiple language pairs (VN-JA, EN-JA, custom).
---

# Backlog Workflow Automation

Intelligent automation for Backlog issue management - translate summaries to bilingual format, sync with Google Sheets, and maintain consistency across tools.

## ⚠️ FIRST-TIME SETUP (CRITICAL)

**On first use in this conversation, perform interactive setup:**

### Step 1: Verify Environment

Check if `.env` exists with required variables:
```env
BACKLOG_DOMAIN=your-space.backlogtool.com
BACKLOG_API_KEY=your_api_key_here
```

If missing, ask user to create `.env` file with these variables.

### Step 2: Check for User Configuration

Check if `workflow/user-config.json` exists.

**If it does NOT exist**, ask the user:

1. **"What's your Backlog project ID?"** (e.g., 47358)
   - Explain: "You can find this in your project URL or by listing projects"

2. **"What's your Backlog project key?"** (e.g., HB21373)
   - Explain: "This appears in issue keys like HB21373-123"

3. **"Do you want to sync with Google Sheets?"** (yes/no)
   - If yes, ask:
     - Spreadsheet ID (from URL)
     - Sheet name (e.g., "Schedule", "スケジュール")
     - Range (e.g., "E5:E100")

4. **"What language pair do you need?"**
   - Options: vi-ja (Vietnamese→Japanese), en-ja (English→Japanese), custom
   - Default: vi-ja

Then create `workflow/user-config.json`:
```json
{
  "backlog": {
    "projectId": <USER_PROVIDED>,
    "projectKey": "<USER_PROVIDED>"
  },
  "googleSheets": {
    "spreadsheetId": "<USER_PROVIDED or null>",
    "sheetName": "<USER_PROVIDED or null>",
    "range": "<USER_PROVIDED or 'E5:E100'>"
  },
  "translation": {
    "languagePair": "<USER_CHOICE or 'vi-ja'>",
    "format": "VN/EN -- JP",
    "enableCache": true
  },
  "execution": {
    "dryRun": false,
    "delayBetweenUpdates": 200,
    "testWithOneIssue": false
  },
  "filters": {
    "statusId": [1, 2, 3],
    "count": 100
  }
}
```

### Step 3: Verify Connection

After creating config, verify connection:
```bash
cd backlog/backlog-workflow-skill/scripts
npx tsx verify-setup.ts
```

If verification succeeds, proceed with workflows. If it fails, help user troubleshoot.

## When to Use This Skill

Use this skill when user asks to:
- "Sync issues to bilingual format"
- "Translate Backlog summaries to Japanese"
- "Update issues to VN -- JP format"
- "Sync Backlog to Google Sheets"
- "Keep issues bilingual"
- "Run the translation workflow"

## Available Workflows

### 1. Bilingual Translation Sync

**Purpose:** Update Backlog issue summaries to bilingual format (VN/EN -- JP)

**Commands:**
```bash
# Preview changes (safe, no updates)
npm run sync:dry

# Test with 1 issue (verify before full sync)
npm run sync:test

# Update all issues
npm run sync
```

**Decision tree:**
```
User asks to sync/translate issues
    │
    ├─ First time running? OR User wants preview?
    │  → Run: npm run sync:dry
    │  → Explain: "Shows what will change without making updates"
    │
    ├─ User wants to verify first?
    │  → Run: npm run sync:test
    │  → Explain: "Updates only 1 issue so you can check in Backlog"
    │
    └─ User is confident / has tested?
       → Run: npm run sync
       → Explain: "Updates all issues that need translation"
```

**What it does:**
1. Fetches issues from Backlog based on filters
2. Analyzes which summaries need translation
3. Translates to bilingual format using language pair
4. Updates issue summaries in Backlog
5. Generates detailed report

**Example output:**
```
📥 Fetching issues from Backlog...
✅ Fetched 43 issues

🔄 Processing issues...

📝 [HB21373-383]
   Before: Chốt Release
   After:  Chốt Release -- リリース確定

✅ Updated 32 issues
📊 Report saved to: workflow/sync-report-1234567890.json
```

### 2. Google Sheets Sync

**Purpose:** Sync Backlog issue summaries to Google Sheets

**Commands:**
```bash
# Preview sync (safe, no updates)
npm run sheets:sync:dry

# Test with 1 issue
npm run sheets:sync:test

# Sync all configured issues
npm run sheets:sync

# Auto-sync all bilingual issues (intelligent evaluation)
npm run sheets:auto
```

**Manual vs Auto Mode:**

**Manual mode** (`sheets:sync`):
- User specifies issue keys in config
- Syncs exactly those issues
- Use when: You know specific issues to sync

**Auto mode** (`sheets:auto`):
- Automatically evaluates ALL issues
- Intelligently decides what needs syncing
- Only syncs issues with bilingual format
- Use when: You want automatic evaluation

**What auto mode does:**
1. Fetches all issues from Backlog
2. Evaluates each issue:
   - Has bilingual format? (VN/EN -- JP)
   - Already in sheet?
   - Values match?
3. Syncs only what needs updating
4. Generates evaluation report

### 3. Combined Workflow

**Purpose:** Keep both Backlog and Google Sheets synchronized

```bash
# 1. Translate issues in Backlog to bilingual format
npm run sync:dry        # Preview
npm run sync            # Update Backlog

# 2. Auto-sync bilingual issues to Google Sheets
npm run sheets:auto:dry # Preview
npm run sheets:auto     # Sync to sheets
```

## Configuration

User configuration is stored in `workflow/user-config.json` (created during first-use setup).

**To modify filters** (which issues to process):
```json
{
  "filters": {
    "statusId": [1, 2, 3],           // 1=Open, 2=In Progress, 3=Resolved, 4=Closed
    "createdSince": "2025-10-01",    // Only issues after this date
    "count": 100                      // Max issues to fetch
  }
}
```

**To modify translation settings:**
```json
{
  "translation": {
    "languagePair": "vi-ja",         // or "en-ja", "custom"
    "format": "VN/EN -- JP",
    "enableCache": true
  }
}
```

**To modify Google Sheets settings:**
```json
{
  "googleSheets": {
    "spreadsheetId": "your-sheet-id",
    "sheetName": "Schedule",
    "range": "E5:E100"
  }
}
```

## Translation System

The skill uses a two-layer translation system:

### 1. Dictionary Layer (Instant)

Common phrases are pre-translated based on language pair.

For `vi-ja` (Vietnamese→Japanese):
```
"Chốt Release" → "リリース確定"
"Làm user manual" → "ユーザーマニュアル作成"
"Viết test case" → "テストケース作成"
```

For `en-ja` (English→Japanese):
```
"UAT" → "UAT"
"Release" → "リリース"
"Create user manual" → "ユーザーマニュアル作成"
```

**See:** `references/translation-dictionaries/{language-pair}.json` for complete list.

### 2. Cache Layer (Automatic)

All translations are cached in `workflow/translation-cache.json`:
- Speeds up repeated runs
- Ensures consistency
- Avoids re-translating same text

**To clear cache:**
```bash
rm workflow/translation-cache.json
```

### Adding Custom Translations

Edit the appropriate dictionary file:
```json
// references/translation-dictionaries/vi-ja.json
{
  "languagePair": {"source": "vi", "target": "ja"},
  "commonPhrases": {
    "Your custom phrase": "カスタムフレーズ"
  }
}
```

Or add to user config for one-off translations:
```json
{
  "translation": {
    "customDictionary": {
      "Special term": "特別な用語"
    }
  }
}
```

## Reports

Each workflow run generates a timestamped report.

**Bilingual sync report:** `workflow/sync-report-{timestamp}.json`
```json
{
  "summary": {
    "total": 43,
    "needsTranslation": 32,
    "updated": 32,
    "failed": 0
  },
  "issues": [...]
}
```

**Sheets sync report:** `workflow/sheets-sync-report-{date}.json`
```json
{
  "summary": {
    "totalIssues": 96,
    "hasBilingualFormat": 38,
    "synced": 9,
    "added": 7,
    "updated": 2
  },
  "evaluations": [...]
}
```

## Common Patterns

### Pattern 1: Weekly Sync Routine

```bash
# Monday morning: Check what needs translation
npm run sync:dry

# If looks good, update
npm run sync

# Sync to Google Sheets
npm run sheets:auto
```

### Pattern 2: Single Issue Update

User asks: "Update issue HB21373-123 to bilingual format"

**Don't use workflow** - Generate one-off script instead:
```typescript
import { BacklogClient } from './backlog-workflow-skill/scripts/backlog-client.js';
import { Translator } from './backlog-workflow-skill/scripts/translator.js';

// Fetch specific issue, translate, update
```

### Pattern 3: Custom Filter

User asks: "Sync only closed issues from last month"

**Modify filters in user-config.json:**
```json
{
  "filters": {
    "statusId": [4],                 // Only closed
    "createdSince": "2025-10-01",
    "createdUntil": "2025-10-31",
    "count": 100
  }
}
```

Then run: `npm run sync:dry` → review → `npm run sync`

## Error Handling

### Error: "user-config.json not found"
**Fix:** Run first-time setup (see top of this document)

### Error: "Missing BACKLOG_API_KEY"
**Fix:** Create `.env` file with:
```env
BACKLOG_DOMAIN=your-space.backlogtool.com
BACKLOG_API_KEY=your_api_key_here
```

### Error: "No translation found for: XYZ"
**Fix:** Add custom translation to dictionary file or user config

### Error: "Permission denied on Google Sheets"
**Fix:** Ensure spreadsheet is shared with MCP service account

### Error: Rate limiting (429)
**Fix:** Increase delay in user-config.json:
```json
{
  "execution": {
    "delayBetweenUpdates": 500
  }
}
```

## Performance Metrics

- **Fetch**: ~1 second for 100 issues
- **Translation**: ~0.1s (cached), ~0.5s (new)
- **Update**: ~0.2s per issue (with rate limiting)
- **Total for 50 issues**: ~15-30 seconds

## Resources

### Setup Guide
**See:** `references/setup-guide.md` - Complete setup instructions for new users

### Command Reference
**See:** `references/commands.md` - Detailed command documentation

### Translation Dictionaries
**See:** `references/translation-dictionaries/` - All language pair dictionaries

### Workflow Patterns
**See:** `references/workflow-patterns.md` - Advanced workflow examples

## Success Criteria

After running workflows successfully:

✅ **Bilingual sync:** All issues have format `[VN/EN] -- [JP]`
   - Example: `Chốt Release -- リリース確定`

✅ **Sheets sync:** Google Sheet contains latest issue summaries
   - Format: `{IssueKey} {Summary}`
   - Example: `HB21373-399 Monitoring RPA -- RPA監視`

## Safety Features

1. **Dry run mode** - Preview all changes before applying
2. **Test mode** - Update only 1 issue first
3. **Error handling** - Continues on errors, reports at end
4. **Rate limiting** - Automatic delays between updates
5. **Detailed reports** - Full audit trail of all changes
6. **User-specific config** - Isolated configuration per user
