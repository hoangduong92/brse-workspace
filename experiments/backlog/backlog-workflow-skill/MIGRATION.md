# Migration Guide: Making Existing Scripts User-Config Compatible

This document explains how to modify existing workflow scripts to use `user-config.json` instead of hardcoded `config.json`.

## Overview

**Goal:** Make scripts read from `workflow/user-config.json` (user-specific) instead of `workflow/config.json` (hardcoded).

**Benefits:**
- Each user can have their own configuration
- No hardcoded project IDs or sheet IDs
- Reusable across different projects
- User configs are gitignored

## Files That Need Modification

### 1. backlog/workflow/backlog-sync.ts

**Current code:**
```typescript
// Load configuration
const config = JSON.parse(readFileSync('workflow/config.json', 'utf-8'));
```

**Change to:**
```typescript
// Load user-specific configuration
const configPath = 'workflow/user-config.json';
if (!existsSync(configPath)) {
  console.error('❌ user-config.json not found');
  console.error('Run interactive setup with Claude, or copy from backlog/backlog-workflow-skill/references/config-template.json');
  process.exit(1);
}
const config = JSON.parse(readFileSync(configPath, 'utf-8'));
```

**Also update translator initialization:**
```typescript
// OLD:
this.translator = new Translator(config.translation.enableCache);

// NEW: Pass language pair and custom dictionary
this.translator = new Translator(
  config.translation.enableCache,
  config.translation.languagePair,
  config.translation.customDictionary
);
```

### 2. backlog/workflow/translator.ts

**Current code:**
```typescript
export class Translator {
  private cache: TranslationCache = {};
  private cacheFile = 'workflow/translation-cache.json';

  constructor(enableCache: boolean = true) {
    if (enableCache && existsSync(this.cacheFile)) {
      // ...
    }
  }
}
```

**Change to:**
```typescript
export class Translator {
  private cache: TranslationCache = {};
  private cacheFile = 'workflow/translation-cache.json';
  private languagePair: string;
  private customDictionary: { [key: string]: string };
  private dictionaryPhrases: { [key: string]: string } = {};

  constructor(
    enableCache: boolean = true,
    languagePair: string = 'vi-ja',
    customDictionary: { [key: string]: string } = {}
  ) {
    this.languagePair = languagePair;
    this.customDictionary = customDictionary;

    // Load dictionary for language pair
    this.loadDictionary();

    // Load cache
    if (enableCache && existsSync(this.cacheFile)) {
      // ... existing cache loading code
    }
  }

  private loadDictionary() {
    const dictionaryPath = `backlog/backlog-workflow-skill/references/translation-dictionaries/${this.languagePair}.json`;

    if (existsSync(dictionaryPath)) {
      try {
        const dictionary = JSON.parse(readFileSync(dictionaryPath, 'utf-8'));
        this.dictionaryPhrases = dictionary.commonPhrases || {};
        console.log(`📚 Loaded ${Object.keys(this.dictionaryPhrases).length} phrases from ${this.languagePair} dictionary`);
      } catch (error) {
        console.warn(`⚠️  Failed to load dictionary: ${this.languagePair}`);
      }
    }

    // Merge custom dictionary (overrides)
    if (this.customDictionary && Object.keys(this.customDictionary).length > 0) {
      this.dictionaryPhrases = { ...this.dictionaryPhrases, ...this.customDictionary };
      console.log(`➕ Added ${Object.keys(this.customDictionary).length} custom translations`);
    }
  }

  private async performTranslation(text: string): Promise<string> {
    // Check dictionary first
    if (this.dictionaryPhrases[text]) {
      return this.dictionaryPhrases[text];
    }

    // Fallback: return with [要翻訳] prefix
    console.warn(`⚠️  No translation found for: "${text}"`);
    return `[要翻訳] ${text}`;
  }
}
```

### 3. backlog/workflow/backlog-to-sheets.ts

**Current code:**
```typescript
const config = JSON.parse(readFileSync('workflow/sheets-sync-config.json', 'utf-8'));
```

**Change to:**
```typescript
// Load user-specific configuration
const configPath = 'workflow/user-config.json';
if (!existsSync(configPath)) {
  console.error('❌ user-config.json not found');
  console.error('Run interactive setup with Claude');
  process.exit(1);
}
const config = JSON.parse(readFileSync(configPath, 'utf-8'));

// Get issue keys from config (if manual sync)
const issueKeys = config.sheetsSync?.issueKeys || [];
if (issueKeys.length === 0) {
  console.error('❌ No issue keys configured for manual sync');
  console.error('Add issueKeys to workflow/user-config.json:');
  console.error('{ "sheetsSync": { "issueKeys": ["HB21373-XXX", ...] } }');
  process.exit(1);
}
```

### 4. backlog/workflow/backlog-to-sheets-auto.ts

**Current code:**
```typescript
const config = JSON.parse(readFileSync('workflow/sheets-sync-config.json', 'utf-8'));
```

**Change to:**
```typescript
// Load user-specific configuration
const configPath = 'workflow/user-config.json';
if (!existsSync(configPath)) {
  console.error('❌ user-config.json not found');
  console.error('Run interactive setup with Claude');
  process.exit(1);
}
const config = JSON.parse(readFileSync(configPath, 'utf-8'));

// Verify Google Sheets config
if (!config.googleSheets?.spreadsheetId || config.googleSheets.spreadsheetId.startsWith('<')) {
  console.error('❌ Google Sheets not configured');
  console.error('Add Google Sheets config to workflow/user-config.json');
  process.exit(1);
}
```

## New Config Structure

### workflow/user-config.json (NEW)

```json
{
  "backlog": {
    "projectId": 47358,
    "projectKey": "HB21373"
  },

  "googleSheets": {
    "spreadsheetId": "1f0dNgvBcLSbh2ckMkczWYQnwUi8zoj9mb42usR10Qfo",
    "sheetName": "スケジュール",
    "range": "E5:E100"
  },

  "translation": {
    "languagePair": "vi-ja",
    "format": "VN/EN -- JP",
    "enableCache": true,
    "customDictionary": {}
  },

  "execution": {
    "dryRun": false,
    "delayBetweenUpdates": 200,
    "testWithOneIssue": false
  },

  "filters": {
    "statusId": [1, 2, 3],
    "createdSince": "2025-10-01",
    "count": 100
  },

  "sheetsSync": {
    "issueKeys": ["HB21373-399", "HB21373-397"]
  }
}
```

### workflow/config.json (DEPRECATED)

This file should be:
1. Moved to `backlog-workflow-skill/references/config-template.json` as template
2. Deleted from workflow/
3. Replaced by user-config.json

## Migration Checklist

- [ ] Modify `backlog-sync.ts` to read `user-config.json`
- [ ] Modify `translator.ts` to support language pairs and dictionaries
- [ ] Modify `backlog-to-sheets.ts` to read `user-config.json`
- [ ] Modify `backlog-to-sheets-auto.ts` to read `user-config.json`
- [ ] Move `config.json` to `backlog-workflow-skill/references/config-template.json`
- [ ] Delete old `workflow/config.json` (after backup)
- [ ] Delete old `workflow/sheets-sync-config.json` (after backup)
- [ ] Test with user-config.json
- [ ] Update all existing reports/caches to new paths
- [ ] Commit template files, NOT user-config.json

## Testing Migration

### 1. Create User Config from Template

```bash
cp backlog/backlog-workflow-skill/references/config-template.json workflow/user-config.json
```

### 2. Edit User Config

Replace all `<YOUR_XXX>` placeholders with actual values.

### 3. Verify Setup

```bash
cd backlog/backlog-workflow-skill/scripts
npx tsx verify-setup.ts
```

### 4. Test Dry Run

```bash
npm run sync:dry
```

If this works, migration is successful!

## Rollback Plan

If migration causes issues:

1. Restore old config:
   ```bash
   git checkout workflow/config.json
   git checkout workflow/sheets-sync-config.json
   ```

2. Revert script changes:
   ```bash
   git checkout backlog/workflow/backlog-sync.ts
   git checkout backlog/workflow/translator.ts
   git checkout backlog/workflow/backlog-to-sheets.ts
   git checkout backlog/workflow/backlog-to-sheets-auto.ts
   ```

3. Continue using old approach until issues resolved

## Benefits After Migration

✅ **Reusable** - Share SKILL with colleagues
✅ **Portable** - Each user has their own config
✅ **Secure** - User configs are gitignored
✅ **Flexible** - Support multiple language pairs
✅ **Maintainable** - Template-based configuration
✅ **Extensible** - Easy to add new features

## Questions?

Refer to:
- SKILL.md - Main SKILL documentation
- setup-guide.md - Complete setup instructions
- README.md - Overview and quick start
