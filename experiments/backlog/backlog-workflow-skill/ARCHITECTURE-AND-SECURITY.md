# Architecture and Security Guide

**Understanding how the SKILL works, where credentials are stored, and who creates what**

## 🏗️ Execution Environment

### Where Everything Runs

```
┌─────────────────────────────────────────────────────────────┐
│ YOUR LOCAL COMPUTER                                         │
│ (e.g., D:\project\claude-code\)                             │
└─────────────────────────────────────────────────────────────┘
    │
    ├─ Claude Desktop App
    │  ├─ Conversation UI (you type questions here)
    │  └─ Tool Execution Engine
    │     ├─ Read tool → reads YOUR local files
    │     ├─ Write tool → writes to YOUR local files
    │     └─ Bash tool → executes commands on YOUR machine
    │
    └─ Your Project Files
       ├─ .env (YOUR Backlog API key)
       ├─ credentials/ (YOUR Google credentials)
       ├─ workflow/user-config.json (YOUR configuration)
       └─ backlog/backlog-workflow-skill/ (SKILL code)

┌─────────────────────────────────────────────────────────────┐
│ CLAUDE'S SERVERS (Anthropic Cloud)                          │
└─────────────────────────────────────────────────────────────┘
    │
    └─ Conversation history
       └─ NO credentials stored here ✓
```

### Critical Understanding

**Everything runs on YOUR local machine:**
- ✅ Scripts execute locally
- ✅ Credentials stay on your computer
- ✅ Claude accesses files only during conversation
- ✅ No data uploaded to Claude servers

**Claude Desktop App is like a local assistant:**
- Reads your local files (with your permission)
- Writes files locally
- Executes commands locally
- Everything happens on your machine

## 🔐 Credential Management

### Two Types of Credentials

#### 1. Backlog API Key

**What it is:**
- Secret token that authenticates you to Backlog API
- Gives read/write access to your Backlog projects

**Who creates it:** ❌ **YOU (manually)**
- Go to Backlog website → Personal Settings → API
- Generate API key
- Copy the key

**Where it's stored:** **YOUR computer** (`.env` file)
```env
BACKLOG_DOMAIN=your-space.backlogtool.com
BACKLOG_API_KEY=abc123xyz...
```

**Can Claude create it?** ❌ **NO**
- Claude cannot access Backlog website UI
- Only you can generate API keys from Backlog
- You must create `.env` file manually

**Is it shared in git?** ❌ **NO** (gitignored)

#### 2. Google Service Account Credentials

**What it is:**
- JSON file containing private key for Google API access
- Allows programmatic access to Google Sheets

**Who creates it:** ❌ **YOU (manually)**
- Go to Google Cloud Console
- Create service account
- Download JSON key file
- Save to your local computer

**Where it's stored:** **YOUR computer** (`credentials/` folder)
```
credentials/
└─ google-service-account.json
```

**Can Claude create it?** ❌ **NO**
- Claude cannot access Google Cloud Console
- Only you can create service accounts
- You must download the JSON file manually

**Is it shared in git?** ❌ **NO** (gitignored by pattern `*ggsheet*.json`)

### What Claude Creates

#### user-config.json

**What it is:**
- Configuration file that points to your credentials
- Contains project IDs, spreadsheet IDs, preferences
- Does NOT contain actual secrets (only paths to them)

**Who creates it:** ✅ **CLAUDE (automatically)**
- Claude asks you questions
- You provide answers (project ID, sheet ID, etc.)
- Claude writes the file using Write tool

**Where it's stored:** **YOUR computer** (`workflow/user-config.json`)
```json
{
  "backlog": {
    "projectId": 47358,
    "projectKey": "HB21373"
  },
  "googleSheets": {
    "spreadsheetId": "1AbCdEfG...",
    "credentialsFile": "credentials/google-creds.json"  ← Path only
  },
  "translation": {
    "languagePair": "vi-ja"
  }
}
```

**Can you create it manually?** ✅ **YES**
- You can copy from `references/config-template.json`
- Fill in your values
- Save to `workflow/user-config.json`

**Is it shared in git?** ❌ **NO** (gitignored)

## 📋 Complete Workflow: Who Does What

### Phase 1: Prerequisites (YOU do manually)

```
┌─────────────────────────────────────────────────────────────┐
│ TASK: Get Backlog API Key                                   │
│ WHO:  YOU (the user)                                        │
│ WHY:  Claude cannot access Backlog website                 │
└─────────────────────────────────────────────────────────────┘

Steps:
1. Open browser
2. Go to your Backlog space
3. Personal Settings → API
4. Click "Register" to generate new key
5. Copy the API key
6. Create .env file on your computer:

   $ cd D:\project\claude-code
   $ notepad .env

   Type:
   BACKLOG_DOMAIN=your-space.backlogtool.com
   BACKLOG_API_KEY=paste_key_here

   Save and close.

Result: ✅ .env file exists on YOUR computer
```

```
┌─────────────────────────────────────────────────────────────┐
│ TASK: Get Google Service Account Credentials                │
│ WHO:  YOU (the user)                                        │
│ WHY:  Claude cannot access Google Cloud Console            │
└─────────────────────────────────────────────────────────────┘

Steps:
1. Open browser
2. Go to https://console.cloud.google.com
3. Enable Google Sheets API
4. Create Service Account:
   - IAM & Admin → Service Accounts
   - Create Service Account
   - Name: "backlog-sheets-sync"
5. Create Key:
   - Click service account
   - Keys → Add Key → Create new key
   - Choose JSON format
   - Download: project-abc123.json
6. Move to your project:

   $ mkdir D:\project\claude-code\credentials
   $ move Downloads\project-abc123.json ^
          D:\project\claude-code\credentials\google-creds.json

7. Share your Google Sheet:
   - Open your Google Sheet
   - Click "Share"
   - Enter service account email (from JSON file)
   - Give "Editor" permission

Result: ✅ credentials/google-creds.json exists on YOUR computer
```

### Phase 2: Interactive Setup (CLAUDE does automatically)

```
┌─────────────────────────────────────────────────────────────┐
│ TASK: Create user-config.json                               │
│ WHO:  CLAUDE (via interactive questions)                   │
│ WHY:  Automates configuration based on your answers        │
└─────────────────────────────────────────────────────────────┘

Flow:
YOU: "Help me sync Backlog issues to bilingual format"

CLAUDE checks: Does workflow/user-config.json exist?
└─ NO → Start interactive setup

CLAUDE asks:
┌────────────────────────────────────────┐
│ "What's your Backlog project ID?"      │
│ → You answer: "47358"                  │
│                                        │
│ "What's your Backlog project key?"     │
│ → You answer: "HB21373"                │
│                                        │
│ "Do you want Google Sheets sync?"      │
│ → You answer: "yes"                    │
│                                        │
│ "What's your spreadsheet ID?"          │
│ → You answer: "1AbCdEfG..."            │
│                                        │
│ "Where is your credentials file?"      │
│ → You answer: "credentials/google-creds.json" │
│                                        │
│ "What language pair?"                  │
│ → You answer: "vi-ja"                  │
└────────────────────────────────────────┘

CLAUDE uses Write tool:
└─ Creates: D:\project\claude-code\workflow\user-config.json
   Content: {
     "backlog": { "projectId": 47358, ... },
     "googleSheets": {
       "credentialsFile": "credentials/google-creds.json",
       ...
     },
     "translation": { "languagePair": "vi-ja" }
   }

Result: ✅ user-config.json exists on YOUR computer
```

### Phase 3: Execution (CLAUDE runs on your machine)

```
┌─────────────────────────────────────────────────────────────┐
│ TASK: Sync Backlog issues                                   │
│ WHO:  CLAUDE executes, scripts run on YOUR machine         │
│ WHY:  To update Backlog using your credentials             │
└─────────────────────────────────────────────────────────────┘

CLAUDE uses Bash tool:
$ npx tsx backlog/backlog-workflow-skill/scripts/backlog-sync.ts

What happens (on YOUR local machine):
┌────────────────────────────────────────┐
│ 1. Script starts                       │
│ 2. Reads .env → gets YOUR API key     │
│ 3. Reads user-config.json → gets IDs  │
│ 4. Calls Backlog API with YOUR key    │
│ 5. Updates issues                      │
│ 6. Done!                               │
└────────────────────────────────────────┘

Result: ✅ Backlog issues updated using YOUR credentials
```

## 🔒 Security: Multi-User Scenarios

### Scenario: You and Your Friend Both Use the SKILL

```
┌─────────────────────────────────────────────────────────────┐
│ YOUR COMPUTER (Computer A)                                  │
└─────────────────────────────────────────────────────────────┘
Location: D:\project\claude-code\

Files YOU created:
├─ .env
│  └─ BACKLOG_API_KEY=YOUR_key_abc123
├─ credentials/
│  └─ google-creds.json (YOUR service account)
└─ workflow/
   └─ user-config.json
      ├─ projectId: 47358 (YOUR project)
      └─ credentialsFile: "credentials/google-creds.json"

Shared files (from git):
└─ backlog/backlog-workflow-skill/
   ├─ SKILL.md
   ├─ scripts/
   └─ references/

┌─────────────────────────────────────────────────────────────┐
│ FRIEND'S COMPUTER (Computer B)                              │
└─────────────────────────────────────────────────────────────┘
Location: C:\friend\project\

Files FRIEND created:
├─ .env
│  └─ BACKLOG_API_KEY=FRIEND_key_xyz789
├─ credentials/
│  └─ google-creds.json (FRIEND's service account)
└─ workflow/
   └─ user-config.json
      ├─ projectId: 12345 (FRIEND's project)
      └─ credentialsFile: "credentials/google-creds.json"

Shared files (from git):
└─ backlog/backlog-workflow-skill/
   ├─ SKILL.md
   ├─ scripts/
   └─ references/
```

### Key Security Properties

**✅ Complete Isolation:**
- You run on YOUR computer with YOUR files
- Friend runs on THEIR computer with THEIR files
- No credentials shared between users

**✅ No Cloud Storage:**
- Credentials stay on local machines
- Claude doesn't upload credentials to servers
- Each person's data is private

**✅ Same Code, Different Data:**
- Both use same SKILL scripts (shared in git)
- Each has their own credentials (NOT in git)
- Each has their own configuration (NOT in git)

**✅ Claude Accesses Only Local Files:**
- When YOU talk to Claude → Claude reads YOUR files
- When FRIEND talks to Claude → Claude reads FRIEND's files
- No cross-contamination

## 🤔 Common Questions

### Q1: Can Claude access my credentials?

**A:** Yes, but only **locally during your conversation**:

**What Claude CAN do:**
- ✅ Read `.env` file (your Backlog API key)
- ✅ Read credentials file (your Google credentials)
- ✅ Execute scripts that use these credentials
- ✅ All happens on YOUR local machine

**What Claude CANNOT do:**
- ❌ Upload credentials to Claude servers
- ❌ Store credentials permanently in cloud
- ❌ Share credentials with other users
- ❌ Access credentials after conversation ends

**Important:** Claude only accesses files through tools during active conversation. Files never leave your computer.

### Q2: Where are my credentials stored?

**A:** On YOUR local computer ONLY:

```
Your Computer Filesystem
├─ .env                              ← Backlog API key here
├─ credentials/google-creds.json     ← Google credentials here
└─ workflow/user-config.json         ← Points to above files

Claude's Servers
└─ (Nothing - no credentials stored)
```

### Q3: My friend imports the SKILL - do they see my credentials?

**A:** NO! Here's why:

**What IS shared (via git):**
- ✅ SKILL code (`backlog/backlog-workflow-skill/`)
- ✅ Translation dictionaries
- ✅ Documentation
- ✅ Config templates

**What is NOT shared (gitignored):**
- ❌ `.env` (your Backlog API key)
- ❌ `credentials/` (your Google credentials)
- ❌ `workflow/user-config.json` (your configuration)

**Your friend must:**
1. Create their own `.env` file
2. Get their own Google service account
3. Run interactive setup with Claude
4. Get their own `user-config.json`

**Result:** Same SKILL code, completely separate credentials.

### Q4: Does Claude Code have access to external services?

**A:** NO - Claude cannot directly access:

❌ Backlog website (to generate API keys)
❌ Google Cloud Console (to create service accounts)
❌ Your Google Sheets (until you share with service account)
❌ External websites or services

**You must:**
- ✅ Manually create API keys from Backlog
- ✅ Manually create service accounts from Google Cloud
- ✅ Manually share Google Sheets
- ✅ Save credentials locally on your computer

**Then Claude can:**
- ✅ Read the credentials you created
- ✅ Execute scripts that use those credentials
- ✅ All happening on your local machine

### Q5: Is it safe to use Claude with sensitive credentials?

**A:** Yes, with understanding:

**Safe because:**
- ✅ Credentials stay on your local machine
- ✅ Scripts execute locally (not in cloud)
- ✅ No credentials uploaded to Claude servers
- ✅ You control file access permissions

**Best practices:**
- ✅ Keep `.env` and credentials files gitignored
- ✅ Don't paste credentials directly in chat
- ✅ Use environment variables for secrets
- ✅ Review what Claude reads/writes
- ✅ Revoke credentials if compromised

**What to avoid:**
- ❌ Don't commit credentials to git
- ❌ Don't paste API keys in conversation
- ❌ Don't share credentials files via email/chat
- ❌ Don't use absolute paths with usernames

## 📊 Summary Table

| Item | Creator | Location | Shared in Git? | Access |
|------|---------|----------|----------------|--------|
| **SKILL code** | Team/You | `backlog/backlog-workflow-skill/` | ✅ Yes | Everyone |
| **Translation dictionaries** | Team/You | `references/translation-dictionaries/` | ✅ Yes | Everyone |
| **Config template** | Team/You | `references/config-template.json` | ✅ Yes | Everyone |
| **Documentation** | Team/You | `*.md` files | ✅ Yes | Everyone |
| **.env** | **YOU manually** | `project-root/.env` | ❌ No | Only you |
| **Google credentials** | **YOU manually** | `credentials/*.json` | ❌ No | Only you |
| **user-config.json** | **Claude** | `workflow/user-config.json` | ❌ No | Only you |
| **Cache/Reports** | Scripts (auto) | `workflow/*.json` | ❌ No | Only you |

## 🎯 Key Principles

### 1. **Local Execution Model**
All scripts run on your local machine, not in the cloud.

### 2. **Credential Separation**
Code (shared) is separate from credentials (private).

### 3. **User Isolation**
Each user has independent configuration and credentials.

### 4. **Manual Prerequisites**
You must manually obtain credentials from external services.

### 5. **Claude as Local Assistant**
Claude reads/writes/executes locally during conversation.

## 🚀 Next Steps

Now that you understand the architecture:

1. **Create your credentials** (manually from Backlog/Google)
2. **Run interactive setup** (Claude creates user-config.json)
3. **Verify setup** (test connections)
4. **Start using the SKILL** (sync issues, sheets, etc.)

**Read next:**
- `references/setup-guide.md` - Step-by-step setup instructions
- `SCRIPTS-GUIDE.md` - Understand what each script does
- `references/commands.md` - Available commands reference
