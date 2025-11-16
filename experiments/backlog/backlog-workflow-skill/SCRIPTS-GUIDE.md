# Scripts Guide: Where the Real Work Happens

**Clear overview of which scripts do what and where to find them**

## 🎯 Quick Answer

**Q: Which scripts actually update Backlog and sync to Google Sheets?**

**A:** The scripts in `backlog/backlog-workflow-skill/scripts/` (user-config compatible versions)

## 📂 Script Locations

### ✅ NEW: User-Config Compatible Scripts (SKILL)

```
backlog/backlog-workflow-skill/scripts/
├── backlog-sync.ts              ← Updates Backlog issue names (MAIN WORKER) ✅
├── backlog-to-sheets.ts         ← Syncs to Google Sheets (manual) ✅
├── backlog-to-sheets-auto.ts    ← Auto-syncs to Google Sheets (intelligent) ✅
├── translator.ts                ← Translation service with language pairs ✅
└── verify-setup.ts              ← Connection test ✅
```

**These scripts:**
- ✅ Read from `workflow/user-config.json`
- ✅ Support multiple language pairs (vi-ja, en-ja, custom)
- ✅ Work with any user's project
- ✅ Fully extensible and reusable

### ⚠️ OLD: Hardcoded Scripts (Legacy)

```
backlog/workflow/
├── backlog-sync.ts              ← OLD: Uses config.json (hardcoded)
├── backlog-to-sheets.ts         ← OLD: Uses sheets-sync-config.json (hardcoded)
├── backlog-to-sheets-auto.ts    ← OLD: Uses sheets-sync-config.json (hardcoded)
├── translator.ts                ← OLD: Hardcoded Vietnamese only
├── config.json                  ← OLD: Hardcoded project IDs
└── sheets-sync-config.json      ← OLD: Hardcoded sheet IDs
```

**These scripts:**
- ❌ Read from `workflow/config.json` (hardcoded)
- ❌ Only support Vietnamese → Japanese
- ❌ Not reusable for other users
- ⚠️ **Keep as backup** but migrate to new scripts

## 🔧 What Each Script Does

### 1. backlog-sync.ts (Main Worker)

**Purpose:** Fetches Backlog issues, translates to bilingual format, updates Backlog

**Location:** `backlog/backlog-workflow-skill/scripts/backlog-sync.ts`

**What it does:**
1. Reads `workflow/user-config.json`
2. Fetches issues from Backlog (using projectId from config)
3. Loads translation dictionary (based on languagePair from config)
4. For each issue:
   - Checks if summary needs translation
   - Translates source language → Japanese
   - Updates issue in Backlog with bilingual format
5. Generates detailed report

**How to run:**
```bash
# Preview mode (no changes)
npx tsx backlog/backlog-workflow-skill/scripts/backlog-sync.ts --dry-run

# Test mode (update 1 issue)
npx tsx backlog/backlog-workflow-skill/scripts/backlog-sync.ts --test

# Production (update all)
npx tsx backlog/backlog-workflow-skill/scripts/backlog-sync.ts
```

**Example output:**
```
📥 Fetching issues from Backlog...
✅ Fetched 43 issues

📚 Loaded 80 phrases from vi-ja dictionary
📦 Loaded 15 cached translations

🔄 Processing issues...

📝 [HB21373-383]
   Before: Chốt Release
   After:  Chốt Release -- リリース確定

📝 [HB21373-384]
   Before: Làm user manual
   After:  Làm user manual -- ユーザーマニュアル作成

🚀 Updating 32 issue(s)...

✅ [HB21373-383] Updated
✅ [HB21373-384] Updated
...

📊 Summary
Total issues: 43
Needs translation: 32
Updated: 32
Failed: 0
Already correct: 11

📄 Report saved: workflow/sync-report-1731571234567.json
```

### 2. translator.ts (Translation Engine)

**Purpose:** Translates text from source language to Japanese using dictionaries

**Location:** `backlog/backlog-workflow-skill/scripts/translator.ts`

**What it does:**
1. Loads translation dictionary based on language pair
2. Merges custom translations from user config
3. Translates text using dictionary lookup
4. Caches translations for performance
5. Falls back to `[要翻訳]` prefix if no translation found

**Features:**
- ✅ Supports multiple language pairs
- ✅ Loads dictionaries from `references/translation-dictionaries/`
- ✅ Supports custom dictionary in user config
- ✅ Automatic caching
- ✅ Partial phrase matching

**Example usage:**
```typescript
const translator = new Translator(
  true,           // enableCache
  'vi-ja',        // languagePair
  {               // customDictionary
    "My custom phrase": "カスタムフレーズ"
  }
);

const result = await translator.translate("Chốt Release");
// Returns: "リリース確定"
```

### 3. verify-setup.ts (Setup Checker)

**Purpose:** Verifies environment and configuration are correct

**Location:** `backlog/backlog-workflow-skill/scripts/verify-setup.ts`

**What it does:**
1. Checks `.env` has required variables
2. Validates `user-config.json` exists and has correct format
3. Tests connection to Backlog API
4. Verifies project exists
5. Checks translation dictionary is available

**How to run:**
```bash
cd backlog/backlog-workflow-skill/scripts
npx tsx verify-setup.ts
```

**Example output:**
```
🔍 Verifying Backlog Workflow SKILL setup...

Step 1: Checking environment variables...
✅ Environment variables loaded

Step 2: Checking user configuration...
✅ User configuration found

Step 3: Validating configuration fields...
✅ All required fields present

Step 4: Testing Backlog connection...
✅ Connected to Backlog
✅ Found project: HB21373 (ID: 47358)

Step 5: Checking translation dictionary...
✅ Translation dictionary loaded: vi-ja
   Contains 80 pre-translated phrases

============================================================
📊 Verification Summary

✅ Success: 5
❌ Errors: 0
⚠️  Warnings: 0

✅ Setup verification complete! Ready to use the SKILL.
```

### 4. backlog-to-sheets.ts (Manual Sheets Sync)

**Purpose:** Syncs specific issues (from config) to Google Sheets

**Location:** `backlog/backlog-workflow-skill/scripts/backlog-to-sheets.ts`

**What it does:**
1. Reads issue keys from `user-config.json` (sheetsSync.issueKeys)
2. Fetches those specific issues from Backlog
3. Reads current Google Sheet data
4. Updates or adds issues to the sheet
5. Generates sync report

**How to run:**
```bash
# Preview mode (no changes)
npx tsx backlog/backlog-workflow-skill/scripts/backlog-to-sheets.ts --dry-run

# Test mode (update 1 issue)
npx tsx backlog/backlog-workflow-skill/scripts/backlog-to-sheets.ts --test

# Production (update all configured issues)
npx tsx backlog/backlog-workflow-skill/scripts/backlog-to-sheets.ts
```

**Configuration required:**
```json
// In user-config.json
{
  "googleSheets": {
    "spreadsheetId": "your-sheet-id",
    "sheetName": "Sheet1",
    "range": "E5:E100",
    "credentialsFile": "path/to/credentials.json"
  },
  "sheetsSync": {
    "issueKeys": ["HB21373-399", "HB21373-397", "HB21373-394"]
  }
}
```

### 5. backlog-to-sheets-auto.ts (Auto Sheets Sync)

**Purpose:** Intelligently evaluates ALL issues and syncs only what needs updating

**Location:** `backlog/backlog-workflow-skill/scripts/backlog-to-sheets-auto.ts`

**What it does:**
1. Fetches ALL issues from Backlog (based on filters)
2. Evaluates each issue:
   - Has bilingual format? (VN/EN -- JP)
   - Already in sheet?
   - Values match?
3. Syncs only issues that need updating
4. Generates detailed evaluation report

**How to run:**
```bash
# Preview evaluation (no changes)
npx tsx backlog/backlog-workflow-skill/scripts/backlog-to-sheets-auto.ts --dry-run

# Production auto-sync
npx tsx backlog/backlog-workflow-skill/scripts/backlog-to-sheets-auto.ts
```

**Example output:**
```
📥 Fetching ALL issues from Backlog project...
  ✓ Fetched 96 issues

📖 Reading current Google Sheet data...
  ✓ Read 65 non-empty cells

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
   Value: HB21373-389 Update file spec -- 仕様書更新

============================================================
📊 Evaluation Summary

Total issues: 96
Has bilingual format: 38
Already in sheet: 65
Needs syncing: 9
  - To add: 7
  - To update: 2

🚀 Syncing to Google Sheets...
  ✓ [HB21373-394] Updated at row 33
  ✓ [HB21373-389] Added at row 72
  ...

✅ Synced 9 issue(s) to Google Sheets
```

**Advantages over manual sync:**
- ✅ No manual issue key configuration
- ✅ Automatic evaluation logic
- ✅ Only syncs relevant issues (with bilingual format)
- ✅ Detects and updates changed summaries
- ✅ Scales to any number of issues

## 🆚 Old vs New Comparison

### Key Differences

| Aspect | OLD Scripts (`workflow/`) | NEW Scripts (`SKILL/scripts/`) |
|--------|---------------------------|--------------------------------|
| **Config file** | `config.json`, `sheets-sync-config.json` | `user-config.json` (unified) |
| **Language support** | Vietnamese only | Multiple (vi-ja, en-ja, custom) |
| **Dictionary** | Hardcoded in translator.ts | External files in `references/` |
| **Reusability** | ❌ Not reusable | ✅ Fully reusable |
| **Extensibility** | ❌ Fixed | ✅ Extensible |
| **User isolation** | ❌ Shared config | ✅ Isolated per user |
| **Google Sheets** | ✅ Works | ✅ Works (same API) |

### Migration Path

**Option 1: Use New Scripts (Recommended)**

```bash
# Create your user-config.json
cp backlog/backlog-workflow-skill/references/config-template.json workflow/user-config.json

# Edit with your values
code workflow/user-config.json

# Use new scripts
npx tsx backlog/backlog-workflow-skill/scripts/backlog-sync.ts
```

**Option 2: Keep Using Old Scripts**

Keep using `backlog/workflow/backlog-sync.ts` if:
- You're the only user
- You don't need multiple language pairs
- You don't want to change anything

**Option 3: Migrate Old Scripts**

Follow `MIGRATION.md` to update old scripts to use user-config.json

## 🚀 How to Use (Complete Workflow)

### Step 1: Setup

```bash
# Verify setup is correct
cd backlog/backlog-workflow-skill/scripts
npx tsx verify-setup.ts
```

### Step 2: Preview Changes

```bash
# See what would be changed
npx tsx backlog-workflow-skill/scripts/backlog-sync.ts --dry-run
```

### Step 3: Test with 1 Issue

```bash
# Update only 1 issue to verify
npx tsx backlog-workflow-skill/scripts/backlog-sync.ts --test
```

### Step 4: Check in Backlog

Visit: `https://your-space.backlogtool.com/view/YOUR-KEY-123`

Verify the issue summary looks correct.

### Step 5: Full Sync

```bash
# Update all issues
npx tsx backlog-workflow-skill/scripts/backlog-sync.ts
```

### Step 6: Review Report

```bash
# View the generated report
cat workflow/sync-report-*.json | tail -1 | jq '.'
```

## 📝 NPM Scripts (Optional)

You can add these to `package.json` for convenience:

```json
{
  "scripts": {
    "skill:verify": "tsx backlog/backlog-workflow-skill/scripts/verify-setup.ts",
    "skill:sync:dry": "tsx backlog/backlog-workflow-skill/scripts/backlog-sync.ts --dry-run",
    "skill:sync:test": "tsx backlog/backlog-workflow-skill/scripts/backlog-sync.ts --test",
    "skill:sync": "tsx backlog/backlog-workflow-skill/scripts/backlog-sync.ts"
  }
}
```

Then use:
```bash
npm run skill:verify
npm run skill:sync:dry
npm run skill:sync:test
npm run skill:sync
```

## 🔍 Troubleshooting

### Script fails with "user-config.json not found"

**Solution:**
```bash
cp backlog/backlog-workflow-skill/references/config-template.json workflow/user-config.json
# Then edit workflow/user-config.json with your values
```

### Script fails with "Missing BACKLOG_API_KEY"

**Solution:**
```bash
# Create .env file
echo "BACKLOG_DOMAIN=your-space.backlogtool.com" > .env
echo "BACKLOG_API_KEY=your_api_key_here" >> .env
```

### No translation found for phrases

**Solution:**

Add custom translations to `workflow/user-config.json`:
```json
{
  "translation": {
    "customDictionary": {
      "Your phrase": "日本語訳"
    }
  }
}
```

Or add to the language pair dictionary:
```bash
code backlog/backlog-workflow-skill/references/translation-dictionaries/vi-ja.json
```

## 📊 Summary

**Real working scripts:** `backlog/backlog-workflow-skill/scripts/`

| Script | Purpose | Usage |
|--------|---------|-------|
| `backlog-sync.ts` | Update Backlog issue names | `npx tsx backlog-sync.ts` |
| `translator.ts` | Translate to Japanese | Used by backlog-sync.ts |
| `verify-setup.ts` | Verify configuration | `npx tsx verify-setup.ts` |

**These are the scripts that:**
- ✅ Update your Backlog issues
- ✅ Translate to bilingual format
- ✅ Work with any user's project
- ✅ Support multiple languages

**Old scripts in `backlog/workflow/`:**
- ⚠️ Still work but are hardcoded
- ⚠️ Keep as backup
- 🔄 Migrate to new scripts when ready
