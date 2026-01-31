---
name: bk-init
description: BrseKit project setup wizard - credentials, .env generation, project configuration
argument-hint: "[--fresh|--env-only|--validate]"
user-invocable: true
---

# bk-init - BrseKit Project Setup Wizard

Interactive wizard for initializing BrseKit with credentials and project configuration.

## Purpose

Complete setup wizard that:
1. **Collects credentials** - Backlog URL, API key, Google API key (optional)
2. **Generates .env file** - Auto-saves credentials
3. **Configures project** - Name, type, customer, PM methodology
4. **Verifies connection** - Tests Backlog API
5. **Shows quick start** - Ready-to-use commands

## Usage

```bash
# Full setup (credentials + project config)
/bk-init

# Only setup credentials and .env
/bk-init --env-only

# Force reconfigure everything
/bk-init --fresh

# Validate existing config
/bk-init --validate

# Check environment variables
/bk-init --check-env

# Preview config without saving
/bk-init --dry-run
```

## Workflow

```
[Phase 1] Environment Setup
├── Check existing .env
├── Collect Backlog URL, API key
├── Collect Google API key (optional)
├── Test connection
└── Save .env file

[Phase 2] Project Configuration
├── Step 1: Project info (name, Backlog key)
├── Step 2: Project type & methodology
├── Step 3: Customer profile
├── Step 4: PM focus areas
└── Step 5: Vault configuration

[Phase 3] Verification
├── Validate config structure
├── Test Backlog connection
└── Save project-context.yaml

[Done] Quick Start Guide
```

## Output Files

### .env
```bash
# BrseKit Environment Configuration
BACKLOG_SPACE_URL=https://your-space.backlog.jp
BACKLOG_API_KEY=your-api-key
BACKLOG_PROJECT_KEY=PROJ

# Google Gemini API (optional)
GOOGLE_API_KEY=your-gemini-key
```

### project-context.yaml
```yaml
project:
  name: "Project Name"
  backlog_key: "PROJ"
  type: "project-based"
  methodology: "waterfall"

customer:
  name: "Customer Corp"
  industry: "Finance"
  timezone: "JST"
  communication_style: "formal"

focus_areas:
  primary: [change_request_tracking, budget_monitoring]
  secondary: [documentation_quality]

vault:
  enabled: true
  sources: [email, backlog]
  sync_schedule: "daily"
```

## Quick Start (after setup)

```bash
/bk-track status     # Check project health
/bk-track report     # Generate weekly report
/bk-recall sync      # Start syncing data
/bk-morning          # Get morning brief
/brsekit help        # Full documentation
```

## PM Templates

| Template | Best For | Key Features |
|----------|----------|--------------|
| **waterfall** | Fixed scope projects | CR tracking, budget monitoring, phase gates |
| **agile** | Time & materials | Sprint goals, velocity tracking, ceremonies |
| **hybrid** | Combined approach | CR + sprint cadence |

## Related Skills

- `/brsekit help` - Full BrseKit documentation
- `/bk-track` - Uses project-context.yaml for reports
- `/bk-recall` - Uses .env for Backlog sync

## Implementation

- **Language:** Python 3.11+
- **Dependencies:** PyYAML, python-dotenv
- **Entry:** `.claude/skills/bk-init/scripts/main.py`
- **New module:** `env_setup.py` (credential collection)
