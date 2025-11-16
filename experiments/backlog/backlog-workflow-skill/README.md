# Backlog Workflow SKILL

**Extensible, reusable automation for Backlog issue management**

Transform Backlog issue summaries to bilingual format and sync with Google Sheets - with zero hardcoded configuration.

## 🌟 Key Features

- ✅ **Extensible** - Supports multiple language pairs (VN-JA, EN-JA, custom)
- ✅ **Reusable** - Template-based configuration, not hardcoded values
- ✅ **Replicable** - Interactive setup wizard for easy onboarding
- ✅ **Portable** - User-specific configuration (gitignored)
- ✅ **Intelligent** - Auto-evaluation and smart syncing

## 🚀 Quick Start for New Users

### 1. Prerequisites

- Node.js (v16+)
- Access to Backlog project
- Backlog API key

### 2. First-Time Setup

When you first use this SKILL with Claude, it will interactively ask you for:

1. Backlog project ID and key
2. Google Sheets details (optional)
3. Preferred language pair (vi-ja, en-ja, custom)

Then it creates your personal `workflow/user-config.json` automatically.

### 3. Verify Setup

```bash
cd backlog/backlog-workflow-skill/scripts
npx tsx verify-setup.ts
```

### 4. Start Using

```bash
npm run sync:dry        # Preview bilingual translation
npm run sync            # Update Backlog issues
npm run sheets:auto     # Sync to Google Sheets
```

**That's it!** No manual configuration files to edit.

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [SKILL.md](SKILL.md) | Main SKILL instructions for Claude |
| [**Architecture & Security**](ARCHITECTURE-AND-SECURITY.md) | **How it works, who creates what, where credentials are stored** |
| [Setup Guide](references/setup-guide.md) | Complete setup instructions |
| [Scripts Guide](SCRIPTS-GUIDE.md) | What each script does |
| [Commands](references/commands.md) | All available commands |
| [Config Template](references/config-template.json) | Configuration template |
| [Translation Dictionaries](references/translation-dictionaries/) | Language pair dictionaries |

## 🎯 Usage Examples

### Example 1: Weekly Bilingual Sync

```bash
# Preview what needs translation
npm run sync:dry

# Update Backlog to bilingual format
npm run sync

# Sync to Google Sheets
npm run sheets:auto
```

### Example 2: Safe Testing

```bash
# Preview
npm run sync:dry

# Test with 1 issue
npm run sync:test

# Verify in Backlog UI
# If good → full sync
npm run sync
```

### Example 3: Custom Filters

Edit `workflow/user-config.json`:
```json
{
  "filters": {
    "statusId": [4],                 // Only closed issues
    "createdSince": "2025-10-01",
    "count": 200
  }
}
```

Then run:
```bash
npm run sync
```

## 🌍 Supported Language Pairs

- **vi-ja**: Vietnamese → Japanese
- **en-ja**: English → Japanese
- **custom**: Define your own translations

## 🔧 Configuration

### User Configuration

Your personal config: `workflow/user-config.json` (created during setup)

**DO NOT commit this file!** It's gitignored and user-specific.

### Translation Dictionaries

Pre-built dictionaries in `references/translation-dictionaries/`:
- `vi-ja.json` - Vietnamese → Japanese (80+ phrases)
- `en-ja.json` - English → Japanese (60+ phrases)
- `custom-template.json` - Template for custom pairs

## 📊 Reports

Each workflow run generates detailed reports:

- `workflow/sync-report-{timestamp}.json` - Bilingual sync results
- `workflow/sheets-sync-report-{date}.json` - Manual sheet sync results
- `workflow/sheets-auto-sync-report-{date}.json` - Auto sheet sync results

## 🔒 Security & Privacy

### What's Committed to Git

✅ **Committed:**
- SKILL.md and documentation
- Translation dictionaries
- Config templates
- Scripts

❌ **NOT Committed (gitignored):**
- `user-config.json` - Your personal configuration
- `.env` - Your API keys
- `translation-cache.json` - Auto-generated cache
- `*-report-*.json` - Auto-generated reports

### Sharing with Team

When sharing this SKILL:

1. ✅ Commit SKILL files to git
2. ✅ Share translation dictionaries
3. ❌ DO NOT share user-config.json
4. ❌ DO NOT share .env files

Each team member creates their own configuration through interactive setup.

## 🤝 Multi-User Support

**This SKILL is designed for multi-user reusability:**

| User | Project | Sheet | Language Pair | Config |
|------|---------|-------|---------------|--------|
| Alice | Project A (ID: 12345) | Sheet A | vi-ja | user-config.json |
| Bob | Project B (ID: 67890) | Sheet B | en-ja | user-config.json |
| Charlie | Project C (ID: 11111) | Sheet C | custom | user-config.json |

**Each user:**
- Imports the same SKILL
- Runs interactive setup
- Gets their own user-config.json
- Works with their own projects/sheets

## 🏗️ Architecture

```
backlog-workflow-skill/
├── SKILL.md                          # Main SKILL definition
├── README.md                         # This file
├── references/
│   ├── setup-guide.md                # New user guide
│   ├── commands.md                   # Command reference
│   ├── config-template.json          # Config template
│   └── translation-dictionaries/     # Language pairs
│       ├── vi-ja.json
│       ├── en-ja.json│       
│       └── custom-template.json
└── scripts/
    └── verify-setup.ts               # Setup verification

workflow/                              # User workspace (gitignored)
├── user-config.json                  # Your personal config
├── translation-cache.json            # Auto-generated cache
└── *-report-*.json                   # Auto-generated reports
```

## 🆚 Comparison: Before vs After

### Before (Hardcoded)

```json
{
  "projectId": 47358,           // ← Hardcoded!
  "spreadsheetId": "1f0dNg..."  // ← Hardcoded!
}
```

❌ Not reusable - every user sees the same project
❌ Must edit config manually for each new user
❌ Risk of committing personal data

### After (Template-Based)

```json
// references/config-template.json
{
  "projectId": "<YOUR_PROJECT_ID>",
  "spreadsheetId": "<YOUR_SHEET_ID>"
}
```

✅ Reusable - each user gets their own config
✅ Interactive setup creates user-config.json
✅ User configs are gitignored

## 📈 Benefits

| Benefit | How It Helps |
|---------|--------------|
| **Extensible** | Add new language pairs easily |
| **Reusable** | Share SKILL with colleagues |
| **Replicable** | Quick setup for new users |
| **Portable** | Works across different environments |
| **Isolated** | Each user's config is independent |
| **Safe** | Preview mode before any changes |
| **Intelligent** | Auto-evaluation for sheet sync |

## 🐛 Troubleshooting

### Issue: "user-config.json not found"
**Solution:** Run interactive setup with Claude, or manually copy from config-template.json

### Issue: "Missing BACKLOG_API_KEY"
**Solution:** Create `.env` file with your API credentials

### Issue: "No translation found"
**Solution:** Add custom translations to your language pair dictionary

### More Help
See [Setup Guide](references/setup-guide.md) for complete troubleshooting guide.

## 🎓 Learning Path

1. **Understanding:** Read [Architecture & Security](ARCHITECTURE-AND-SECURITY.md) to understand how everything works
2. **New User:** Follow [Setup Guide](references/setup-guide.md) for step-by-step setup
3. **Daily Use:** Reference [Commands](references/commands.md) and [Scripts Guide](SCRIPTS-GUIDE.md)
4. **Customization:** Explore translation dictionaries
5. **Advanced:** Read SKILL.md for Claude integration details

## 📝 License

MIT License - Feel free to use and modify

## 🙏 Contributing

Contributions welcome! Especially:
- New translation dictionaries (language pairs)
- Improved translation phrases
- Documentation improvements
- Bug fixes

## 🔗 Related

- **Backlog API:** https://developer.nulab.com/docs/backlog/
- **Anthropic Skills:** https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills
- **Claude Code:** https://code.claude.com/

---

**Made with** ❤️ **and Claude Code**
