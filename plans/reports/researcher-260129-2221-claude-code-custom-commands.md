# Research Report: Claude Code Custom Slash Commands

**Date:** 2026-01-29
**Researcher:** Claude Code Agent
**Status:** Complete

---

## Executive Summary

Claude Code supports custom slash commands through markdown files in `.claude/commands/` directories. Commands are defined with optional YAML frontmatter, support dynamic arguments, bash execution, and file references. Official documentation exists in Anthropic's Claude Code docs and Agent SDK reference.

---

## 1. Official Documentation Sources

### Primary References
- **Claude Code Docs - Slash Commands**: https://code.claude.com/docs/en/slash-commands
- **Claude Agent SDK - Slash Commands**: https://platform.claude.com/docs/en/agent-sdk/slash-commands
- **Slash commands in SDK Docs**: https://platform.claude.com/docs/en/agent-sdk/slash-commands (most comprehensive)

### Community Resources
- **GitHub - Production Slash Commands**: https://github.com/wshobson/commands
- **Awesome Claude Code List**: https://github.com/hesreallyhim/awesome-claude-code
- **BioErrorLog Tech Blog**: https://en.bioerrorlog.work/entry/claude-code-custom-slash-command
- **Cloud Artisan Guide**: https://cloudartisan.com/posts/2025-04-14-claude-code-tips-slash-commands/
- **Shipyard CLI Cheatsheet**: https://shipyard.build/blog/claude-code-cheat-sheet/

---

## 2. Directory Structure & Scopes

Commands are stored in two scope levels:

```
Project Scope:    .claude/commands/        (shared with team via git)
Personal Scope:   ~/.claude/commands/      (available across all projects)
```

### Organizational Example
```
.claude/commands/
├── frontend/
│   ├── component.md        # /component command (project:frontend)
│   └── style-check.md      # /style-check command (project:frontend)
├── backend/
│   ├── api-test.md         # /api-test command (project:backend)
│   └── db-migrate.md       # /db-migrate command (project:backend)
└── review.md               # /review command (project)
```

**Key Point:** Subdirectories organize commands but don't affect command name. File name becomes slash command (without .md extension).

---

## 3. Command File Format & Syntax

### Basic Structure
```markdown
---
[optional YAML frontmatter]
---

Command description and instructions
```

### YAML Frontmatter Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `description` | string | Brief explanation shown in /help | `Review pull request with priority` |
| `argument-hint` | string | Visual hint for expected arguments | `[issue-number] [priority]` |
| `allowed-tools` | list | Tools the command can use | `Read, Grep, Glob, Bash(git:*)` |
| `model` | string | Specific Claude model override | `claude-sonnet-4-5-20250929` |

### Complete Example with Frontmatter
```markdown
---
allowed-tools: Read, Grep, Glob, Bash(git diff:*)
description: Comprehensive code review
argument-hint: [branch-name]
model: claude-opus-4-5-20251101
---

Review the following branch: $1

## Changed Files
!`git diff --name-only origin/main...$1`

## Detailed Changes
!`git diff origin/main...$1`

## Review Checklist
1. Code quality and readability
2. Security vulnerabilities
3. Performance implications
4. Test coverage
5. Documentation completeness

Provide specific, actionable feedback organized by priority.
```

---

## 4. Dynamic Arguments & Placeholders

### Positional Arguments
- `$1`, `$2`, `$3` - Access specific positional arguments
- `$ARGUMENTS` - Capture all arguments as single string

### Example: Multi-Argument Command
```markdown
---
argument-hint: [issue-number] [priority] [assignee]
description: Fix a GitHub issue
---

## Task
Fix issue #$1 with priority $2 and assign to $3.

Check the issue description and implement necessary changes.
```

**Usage via SDK:**
```bash
/fix-issue 123 high john-doe
```

Becomes:
- `$1` = "123"
- `$2` = "high"
- `$3` = "john-doe"

---

## 5. Advanced Features

### Bash Command Execution
Use `!` prefix to execute bash and embed output:

```markdown
---
allowed-tools: Bash(git status:*), Bash(git diff:*)
---

## Current Status
!`git status`

## Proposed Changes
!`git diff HEAD`
```

**Note:** Must declare allowed bash commands in `allowed-tools` frontmatter.

### File References
Use `@` prefix to include file contents:

```markdown
---
description: Review configuration files
---

Review these configs for issues:
- @package.json
- @tsconfig.json
- @.env

Check for security issues, outdated deps, misconfigurations.
```

---

## 6. Command Naming & Organization

| Scenario | Example | Result |
|----------|---------|--------|
| Single file | `.claude/commands/test.md` | Command: `/test` |
| Subdirectory | `.claude/commands/backend/migrate.md` | Command: `/migrate` (tagged as project:backend) |
| Nested path | `.claude/commands/infra/docker/build.md` | Command: `/build` (scoped under infra/docker) |

**Best Practice:** Use kebab-case for file names with descriptive names: `security-audit.md`, `code-review.md`, `db-migration.md`

---

## 7. Practical Examples from Official Docs

### Code Review Command
```markdown
---
allowed-tools: Read, Grep, Glob, Bash(git diff:*)
description: Comprehensive code review
---

## Changed Files
!`git diff --name-only HEAD~1`

## Detailed Changes
!`git diff HEAD~1`

Review for: 1) Code quality, 2) Security, 3) Performance, 4) Test coverage, 5) Documentation
```

### Test Runner Command
```markdown
---
allowed-tools: Bash, Read, Edit
argument-hint: [test-pattern]
description: Run tests with optional pattern
---

Run tests matching: $ARGUMENTS

1. Detect test framework (Jest, pytest, etc.)
2. Run tests with pattern
3. If fail: analyze and fix
4. Re-run to verify
```

### Git Commit Command
```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
description: Create a git commit
---

## Context
- Current status: !`git status`
- Current diff: !`git diff HEAD`

## Task
Create git commit with appropriate message based on changes.
```

---

## 8. SDK Integration

### TypeScript Example
```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "/code-review src/auth.ts",
  options: { maxTurns: 3 }
})) {
  if (message.type === "assistant") {
    console.log("Review:", message.message);
  }
}
```

### Python Example
```python
import asyncio
from claude_agent_sdk import query

async def main():
    async for message in query(
        prompt="/test auth",
        options={"max_turns": 5}
    ):
        if message.type == "assistant":
            print("Test results:", message.message)

asyncio.run(main())
```

---

## 9. Built-in Slash Commands

Claude Code provides standard commands (for reference):
- `/compact` - Compress conversation history
- `/clear` - Start fresh conversation
- `/help` - Show all available commands

Custom commands automatically appear in `/help` output.

---

## 10. Best Practices Summary

1. **File Naming**: Use kebab-case, descriptive names (e.g., `security-audit.md`)
2. **Organization**: Group related commands in subdirectories (`frontend/`, `backend/`)
3. **Frontmatter**: Always include `description` for discoverability
4. **Arguments**: Use `argument-hint` when command accepts parameters
5. **Permissions**: Explicitly list `allowed-tools` for security
6. **Version Control**: Keep `.claude/commands/` in git for team sharing
7. **Documentation**: Clear markdown content explains what command does

---

## 11. Key Differences: CLI vs SDK

- **CLI Usage**: Type `/command-name` directly in Claude Code interface
- **SDK Usage**: Pass command as string in `prompt` parameter to `query()`
- **Both** support same markdown format and features

---

## Unresolved Questions

None at this time. Documentation is comprehensive and consistent across official Anthropic sources.

---

## Verification

✅ Official Anthropic documentation confirms all findings
✅ Multiple examples provided in SDK docs
✅ Community resources validate practices
✅ Tested across TypeScript and Python SDK examples

