# Phase 5: CLI & Documentation

## Priority: P3
## Status: pending
## Effort: 3h

## Overview

Update brsekit-cli for new structure and create comprehensive documentation.

## Key Insights

- Current brsekit/SKILL.md needs update for multi-project
- Need onboarding guide for new users
- CLI should provide project management commands

## Requirements

### Functional
- `brsekit list` - List all projects
- `brsekit info PROJECT` - Show project details
- `brsekit switch PROJECT` - Set env for interactive use
- Updated README with quick start
- Onboarding guide for new BrSE

### Non-functional
- Clear error messages
- Help text for all commands
- Examples in documentation

## Architecture

```
brsekit-cli commands:
  brsekit list              # List projects in ./projects/
  brsekit info HB21373      # Show project config
  brsekit help              # Show all commands
  brsekit version           # Show version
```

## Implementation Steps

### 1. Update brsekit main CLI

```python
# .claude/skills/brsekit/scripts/main.py
#!/usr/bin/env python3
"""BrseKit CLI - Multi-project management."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))

from project_manager import ProjectManager


def cmd_list(args):
    """List all projects."""
    pm = ProjectManager()
    projects = pm.list_projects()

    if not projects:
        print("No projects found.")
        print("Create one with: /bk-init PROJECT_NAME")
        return

    print(f"## Projects ({len(projects)})\n")
    for name in sorted(projects):
        context = pm.get_context(name)
        if context:
            desc = context.get("project", {}).get("description", "")
            backlog = context.get("project", {}).get("backlog_key", "")
            print(f"- **{name}** ({backlog})")
            if desc:
                print(f"  {desc[:60]}...")
        else:
            print(f"- **{name}** (no context.yaml)")


def cmd_info(args):
    """Show project info."""
    pm = ProjectManager()
    name = args.project

    if not pm.project_exists(name):
        print(f"Project '{name}' not found")
        return

    context = pm.get_context(name) or {}
    project = context.get("project", {})

    print(f"## {name}\n")
    print(f"**Path:** {pm.get_project_path(name)}")
    print(f"**Backlog Key:** {project.get('backlog_key', 'N/A')}")
    print(f"**Type:** {project.get('type', 'N/A')}")
    print(f"**Description:** {project.get('description', 'N/A')}")

    # Check files
    path = pm.get_project_path(name)
    print("\n**Files:**")
    print(f"  context.yaml: {'[ok]' if (path / 'context.yaml').exists() else '[missing]'}")
    print(f"  .env: {'[ok]' if (path / '.env').exists() else '[missing]'}")
    print(f"  vault/: {'[ok]' if (path / 'vault').is_dir() else '[missing]'}")
    print(f"  glossary.json: {'[ok]' if (path / 'glossary.json').exists() else '[optional]'}")


def cmd_help(args):
    """Show help."""
    print("""
## BrseKit v1.1 - Multi-Project Toolkit

### Project Management
  /brsekit list              List all projects
  /brsekit info PROJECT      Show project details
  /bk-init PROJECT           Create new project

### Daily Workflow
  /bk-track status PROJECT   Project status report
  /bk-morning PROJECT        Morning brief
  /bk-recall search "..."    Search project memory

### Task Management
  /bk-capture task "..."     Capture tasks from text
  /bk-spec refine "..."      Refine requirements

### Translation
  /bk-convert file.xlsx      Translate Excel
  /bk-translate "text"       Translate text
  /bk-write "email"          Japanese business writing

### Memory (User-level)
  /cc-memory search "..."    Search all memories
  /cc-memory recent          Recent sessions

### Examples
  /bk-track status HB21373 --lang ja
  /bk-recall search "deadline" --project HB21373
  /bk-init NEW_PROJECT
""")


def cmd_version(args):
    """Show version."""
    print("BrseKit v1.1.0")
    print("Multi-project architecture")


def main():
    parser = argparse.ArgumentParser(
        description="BrseKit - Multi-project toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="List all projects")

    # info
    info_p = subparsers.add_parser("info", help="Show project info")
    info_p.add_argument("project", help="Project name")

    # help
    subparsers.add_parser("help", help="Show help")

    # version
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    handlers = {
        "list": cmd_list,
        "info": cmd_info,
        "help": cmd_help,
        "version": cmd_version,
    }

    if not args.command:
        cmd_help(args)
        return

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

### 2. Update brsekit SKILL.md

```markdown
# brsekit

BrseKit v1.1 - Multi-project toolkit for Bridge Software Engineers.

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

| Command | Description |
|---------|-------------|
| `/brsekit list` | List all projects |
| `/brsekit info PROJECT` | Show project details |
| `/bk-init PROJECT` | Create new project |
| `/bk-track status PROJECT` | Status report |
| `/bk-recall search "..." --project PROJECT` | Search memory |
| `/bk-capture task "..."` | Capture tasks |
| `/cc-memory search "..."` | User-level memory |

## Multi-Project Architecture

- **Explicit project**: Always specify `--project` or positional arg
- **Env fallback**: project/.env → workspace/.env → system
- **Project vault**: Each project has own SQLite in `projects/NAME/vault/`
- **User memory**: cc-memory stays at `~/claude_client/memory/` (cross-project)

## Env Variables

Project-level (in `projects/PROJECT/.env`):
- `BACKLOG_API_KEY` - Backlog API key
- `NULAB_SPACE_URL` - Backlog space URL
- `SLACK_TOKEN` - Slack bot token (optional)

Workspace-level (in `.env`):
- `GEMINI_API_KEY` - For embeddings
- `GOOGLE_API_KEY` - Alternative Gemini key
```

### 3. Create onboarding guide

```markdown
# BrseKit Onboarding Guide

## First-Time Setup

### 1. Install Dependencies

```bash
cd .claude/skills
pip install -r requirements.txt
```

### 2. Create Your First Project

```bash
/bk-init HB21373
```

Follow the wizard to set up:
- Backlog API key
- Project type (agile/waterfall/hybrid)
- Team members
- Sprint settings

### 3. Configure API Keys

Edit `projects/HB21373/.env`:
```
BACKLOG_API_KEY=your-api-key
NULAB_SPACE_URL=yourspace.backlog.com
```

### 4. Test Connection

```bash
/bk-track status HB21373
```

## Daily Workflow

### Morning Routine
```bash
/bk-morning HB21373
```
Gets: today's tasks, unread messages, schedule.

### Check Project Health
```bash
/bk-track status HB21373 --lang ja
```
Generates: status report with BrSE insights.

### Capture Meeting Notes
```bash
/bk-capture task "
- Tanaka-san mentioned deadline moved to 2/15
- Need to review login feature
- Bug in payment module (high priority)
"
```
Extracts and saves tasks to vault.

### Search Context
```bash
/bk-recall search "login feature" --project HB21373
```
Finds relevant discussions and decisions.

## Multi-Project Management

```bash
# List all projects
/brsekit list

# Switch context
/bk-track status PROJECT_A
/bk-track status PROJECT_B
```

## Troubleshooting

### "Project not found"
Run `/bk-init PROJECT_NAME` first.

### "API key missing"
Check `projects/PROJECT/.env` has `BACKLOG_API_KEY`.

### "Vault error"
Run `/bk-recall sync --project PROJECT` to initialize.
```

### 4. Update main README section

Add to workspace README:

```markdown
## BrseKit v1.1

Multi-project toolkit for Bridge Software Engineers.

### Quick Start

```bash
# Initialize project
/bk-init HB21373

# Daily status
/bk-track status HB21373

# See all commands
/brsekit help
```

See [onboarding guide](.claude/skills/brsekit/onboarding-guide.md) for details.
```

## Related Code Files

### Create/Update
- `.claude/skills/brsekit/scripts/main.py` - CLI commands
- `.claude/skills/brsekit/SKILL.md` - Skill documentation
- `.claude/skills/brsekit/onboarding-guide.md` - New user guide
- `README.md` - Add BrseKit section

## Todo List

- [ ] Update brsekit/scripts/main.py with list/info commands
- [ ] Update brsekit/SKILL.md with multi-project docs
- [ ] Create onboarding-guide.md
- [ ] Update workspace README.md
- [ ] Update all bk-* SKILL.md files with --project examples
- [ ] Test all CLI commands

## Success Criteria

- [ ] `/brsekit list` shows all projects
- [ ] `/brsekit info HB21373` shows project details
- [ ] `/brsekit help` shows all available commands
- [ ] Documentation complete for new users

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Docs out of sync | Medium | Include examples that can be tested |
| Missing edge cases | Low | Add troubleshooting section |

## Final Checklist

After all phases complete:

- [ ] All bk-* skills accept --project
- [ ] `bk-init PROJECT` creates correct structure
- [ ] Env fallback chain works
- [ ] Vault scoped to project
- [ ] Knowledge fallback works
- [ ] cc-memory integrated
- [ ] CLI commands work
- [ ] Documentation complete
- [ ] All tests pass
