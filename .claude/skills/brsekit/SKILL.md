---
name: brsekit
description: BrseKit help and documentation. Use when asking about BrseKit features, installation, or usage.
argument-hint: "[list|info|help|version] [PROJECT]"
user-invocable: true
---

# BrseKit v1.1 - Multi-Project Toolkit

Bộ công cụ AI hỗ trợ Bridge System Engineer quản lý nhiều dự án.

## Quick Start

```bash
# Create a project
/bk-init HB21373

# Check status
/bk-track status HB21373

# Search context
/bk-recall search "deadline" --project HB21373

# Morning brief
/bk-morning HB21373
```

## Project Structure

```
projects/HB21373/
├── .env                # Backlog API key, Slack token
├── context.yaml        # Project config
├── glossary.json       # Project-specific terms
└── vault/              # Project memory (SQLite)
```

## Commands

### Project Management
```bash
/brsekit list              # List all projects
/brsekit info PROJECT      # Show project details
/bk-init PROJECT           # Create new project
```

### Daily Workflow
```bash
/bk-track status PROJECT   # Status report
/bk-track report PROJECT   # Weekly report (--format pptx)
/bk-morning PROJECT        # Morning brief
```

### Memory & Search
```bash
/bk-recall sync --project PROJECT      # Sync data to vault
/bk-recall search "query" --project PROJECT  # Search project memory
/cc-memory search "query"              # User-level memory (cross-project)
```

### Task Management
```bash
/bk-capture task "text..."   # Extract tasks from text
/bk-spec refine "spec..."    # Refine requirements
```

### Translation
```bash
/bk-convert file.xlsx        # Translate Excel/PowerPoint
/bk-write "email content"    # Japanese business writing
```

## Hooks

BrseKit hooks inject project context automatically at session start.

### Session Start Hook
- Scans `projects/` directory on startup
- **1 project**: Auto-selected, no `--project` needed
- **2+ projects**: Shows list with warning to use `--project`
- **0 projects**: Warning + `/bk-init` hint
- Shows env var status (✓/✗) for API keys

### Subagent Hook
- Injects minimal context for spawned agents (~40 tokens)
- Provides `vault` path and `glossary` path for project
- Helps agents access project resources without re-scanning

### --project Behavior

| Scenario | Behavior |
|----------|----------|
| 1 project | Auto-selected, `--project` optional |
| 2+ projects | `--project` required |
| 0 projects | Error, run `/bk-init` |

## Configuration

### Config File (`.claude/.bk.json`)

BrseKit supports cascading config: `~/.claude/.bk.json` (global) → `.claude/.bk.json` (local).

```json
{
  "brseLevel": 1,
  "hooks": {
    "session-init": true,
    "subagent-init": true
  },
  "defaults": {
    "project": "HB21373",
    "language": "vi"
  }
}
```

### brseLevel System

Controls output verbosity and guidance level. **Skills MUST respect `BK_BRSE_LEVEL` env var.**

| Level | Name | Verbosity | Guidance |
|-------|------|-----------|----------|
| -1 | Disabled | No injection | No guidelines (default) |
| 0 | Intern | Very detailed | Step-by-step instructions |
| 1 | Junior | Detailed | Tips + warnings |
| 2 | Mid | Balanced | When relevant |
| 3 | Senior | Concise | Minimal |
| 4 | Lead | Raw/compact | None |

**Default:** `-1` (disabled) - brseLevel not injected, saves tokens.

**Opt-in:** Set `"brseLevel": 1` in `.bk.json` to enable.

### Environment Variables

BrseKit hooks write these env vars to `CLAUDE_ENV_FILE`:

| Var | Purpose | Example |
|-----|---------|---------|
| `BK_BRSE_LEVEL` | Output verbosity | `1` |
| `BK_ACTIVE_PROJECT` | Current project | `HB21373` |
| `BK_VAULT_PATH` | Project vault | `projects/HB21373/vault/` |
| `BK_GLOSSARY_PATH` | Project glossary | `projects/HB21373/glossary.json` |

## Multi-Project Architecture

### Core Principle
No `.active` file - always specify project explicitly:
- `/bk-track status HB21373`
- `/bk-recall search "query" --project HB21373`

### Env Fallback Chain
1. `projects/{name}/.env` (project-specific)
2. `.env` (workspace-level)
3. System environment variables

### Vault Scoping
- **Project vault**: `projects/{name}/vault/vault.db`
- **User memory**: `~/claude_client/memory/` (cross-project, via cc-memory)

### Knowledge Fallback
1. `projects/{name}/glossary.json` (project-specific)
2. `knowledge/glossary-it-terms.json` (shared IT terms)

## Available Skills

| Skill | Description |
|-------|-------------|
| **bk-track** | Project tracking, status reports, weekly PPTX |
| **bk-capture** | Parse tasks, meeting notes, emails |
| **bk-spec** | Requirement analysis, test documents |
| **bk-recall** | Project memory layer (project-scoped) |
| **bk-convert** | JA↔VI translation with glossary |
| **bk-write** | Japanese business writing |
| **bk-morning** | Morning brief with unread counts |
| **bk-init** | Project initialization wizard |
| **cc-memory** | User-level memory (cross-project) |

## Environment Variables

### Project-level (`projects/PROJECT/.env`)
```env
BACKLOG_API_KEY=your-api-key
NULAB_SPACE_URL=yourspace.backlog.com
NULAB_PROJECT_ID=PROJECT
SLACK_TOKEN=xoxb-...  # optional
```

### Workspace-level (`.env`)
```env
GEMINI_API_KEY=your-key  # for embeddings
GOOGLE_API_KEY=your-key  # alternative
```

## Support

- Issues: Tạo issue trong repository
- Slack: #brsekit-support
