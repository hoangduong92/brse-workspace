# Backlog Issue Summary Sync - Automated Workflow

**Automated workflow to fetch, translate, and update Backlog issue summaries to [VN/EN] -- [JP] format**

> **Note:** This is user documentation. If you're Claude Code, see [CLAUDE.md](./CLAUDE.md) for AI-specific instructions.

## 🚀 Quick Start

### 1. Configure (One-time setup)

Edit `workflow/config.json`:

```json
{
  "backlog": {
    "projectId": 47358,      // Your Backlog project ID
    "projectKey": "HB21373"  // Your Backlog project key
  },
  "filters": {
    "statusId": [1, 2, 3],   // 1=Open, 2=In Progress, 3=Resolved, 4=Closed
    "createdSince": "2025-10-01",
    "count": 100             // Max issues to fetch
  }
}
```

### 2. Run the Sync

```bash
# Production mode - Update all issues
npm run sync

# Dry run - Preview changes without updating
npm run sync:dry

# Test mode - Update only 1 issue to verify
npm run sync:test
```

## 📋 What It Does

1. **Fetch** - Gets issues from Backlog based on filters
2. **Analyze** - Detects which summaries need translation
3. **Translate** - Converts to [VN/EN] -- [JP] format
4. **Update** - Updates issue summaries in Backlog
5. **Report** - Generates detailed JSON report

## 🎯 Usage Examples

### Example 1: Preview Changes (Safe)

```bash
npm run sync:dry
```

Output:
```
📥 Fetching issues from Backlog...
✅ Fetched 43 issues

🔄 Processing issues...

📝 [HB21373-383]
   Before: Chốt Release
   After:  Chốt Release -- リリース確定

🔍 DRY RUN MODE - No actual updates will be made
```

### Example 2: Test with 1 Issue

```bash
npm run sync:test
```

This updates only the first issue that needs translation, perfect for verification.

### Example 3: Full Sync

```bash
npm run sync
```

Updates all issues that need translation.

## ⚙️ Configuration Options

### `workflow/config.json`

```json
{
  "backlog": {
    "projectId": 47358,       // Required: Your project ID
    "projectKey": "HB21373"   // Required: Your project key
  },

  "filters": {
    "statusId": [1, 2, 3],    // Filter by status (1-4)
    "createdSince": "2025-10-01",  // Filter by creation date
    "count": 100              // Max issues to fetch
  },

  "translation": {
    "format": "VN/EN -- JP",  // Translation format
    "enableCache": true       // Cache translations to avoid re-translating
  },

  "execution": {
    "dryRun": false,          // Set true to preview without updating
    "delayBetweenUpdates": 200,  // Milliseconds delay to avoid rate limiting
    "testWithOneIssue": false    // Set true to test with 1 issue only
  }
}
```

## 📊 Reports

Each run generates a timestamped report: `workflow/sync-report-{timestamp}.json`

Example report structure:
```json
{
  "timestamp": "2025-01-14T10:30:00.000Z",
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

## 🔧 Translation Cache

The workflow caches translations in `workflow/translation-cache.json` to:
- Speed up repeated runs
- Ensure consistency
- Avoid re-translating the same text

To clear cache:
```bash
rm workflow/translation-cache.json
```

## 📝 Common Translations

The workflow includes common phrase translations:

| Vietnamese/English | Japanese |
|-------------------|----------|
| UAT | UAT |
| Release | リリース |
| Chốt Release | リリース確定 |
| Coding | コーディング |
| Làm user manual | ユーザーマニュアル作成 |
| Viết test case | テストケース作成 |
| Test trên dev | 開発環境でテスト |
| Demo với KH | お客様向けデモ |

## 🛡️ Safety Features

1. **Dry Run Mode** - Preview all changes before applying
2. **Test Mode** - Update only 1 issue first
3. **Error Handling** - Continues on errors, reports at end
4. **Rate Limiting** - Automatic delays between updates
5. **Detailed Reports** - Full audit trail of all changes

## 🔄 Typical Workflow

```bash
# 1. Preview what will change
npm run sync:dry

# 2. Test with 1 issue
npm run sync:test

# 3. Verify the test issue in Backlog UI
# Visit: https://hblab.backlogtool.com/view/HB21373-XXX

# 4. Run full sync
npm run sync

# 5. Review the report
cat workflow/sync-report-*.json | tail -1
```

## ⚡ Performance

- **Fetching**: ~1 second for 100 issues
- **Translation**: ~0.1 seconds per issue (cached), ~0.5 seconds (new)
- **Updating**: ~0.2 seconds per issue (with rate limiting)

**Estimated time for 50 issues**: ~15-30 seconds

## 🐛 Troubleshooting

### Issue: "Authentication failure"
- Check `.env` file has correct `BACKLOG_API_KEY`
- Verify API key has write permissions

### Issue: "No translation found for: XYZ"
- Add custom translation to `workflow/translator.ts`
- Or add to `translation-cache.json` manually

### Issue: Updates failing with 400 error
- Check if summary contains special characters (tabs, newlines)
- Review the sync report for error details

## 📚 Files Structure

```
workflow/
├── config.json              # Configuration
├── backlog-sync.ts          # Main automation script
├── translator.ts            # Translation service
├── translation-cache.json   # Translation cache (auto-generated)
├── sync-report-*.json       # Reports (auto-generated)
└── README.md               # This file
```

## 🎉 Success Criteria

After running the sync, all issues should have summaries in this format:

✅ **[Vietnamese/English] -- [Japanese]**

Examples:
- `Chốt Release -- リリース確定`
- `Làm user manual -- ユーザーマニュアル作成`
- `Update 3 scenario liên quan đến Zendesk bảo mật 2 lớp -- Zendesk二段階認証に関連する3つのシナリオを更新`

---

**Need help?** Check the sync reports for detailed information about what happened during each run.
