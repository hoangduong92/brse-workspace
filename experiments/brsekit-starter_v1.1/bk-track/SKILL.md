---
name: bk-track
description: Project tracking - status analysis and weekly reports with PPTX support. Use when checking project health, generating weekly reports, or asking about task status.
argument-hint: "<status|report|summary> [--threshold N] [--lang en|ja|vi] [--format md|pptx] [--output FILE]"
---

# bk-track

Unified tracking skill merging bk-status and bk-report. Provides project health analysis and weekly reports.

## Quick Start

```bash
/bk-track status                          # Check project health
/bk-track report                          # Generate weekly report (Markdown)
/bk-track report --format pptx -o out.pptx  # Generate PowerPoint report
/bk-track summary                         # Quick one-liner status
```

## Commands

### 📊 status - Project Health Check

Analyze project health: late tasks, risk assessment, member workload.

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--threshold` | `-t` | `3` | Days threshold to mark task as "late" |
| `--lang` | `-l` | `en` | Output language: `en`, `ja`, `vi` |

**Examples:**
```bash
/bk-track status                     # Default: threshold=3, lang=en
/bk-track status --threshold 5       # Task late if >5 days overdue
/bk-track status -t 2 -l ja          # Strict threshold, Japanese output
/bk-track status -p MYPROJ           # Specific project
```

**Output includes:**
- Health score (0-100)
- Late tasks list with days overdue
- At-risk tasks (approaching deadline)
- Member workload analysis
- Risk assessment

---

### 📝 report - Weekly Report

Generate weekly progress report in Markdown or PowerPoint format.

**Options:**
| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | | `7` | Report period in days |
| `--format` | `-f` | `md` | Output format: `md` or `pptx` |
| `--output` | `-o` | stdout | Output file path (required for pptx) |

**Examples:**
```bash
/bk-track report                        # Print Markdown to console
/bk-track report -o weekly.md           # Save Markdown to file
/bk-track report --period 14            # 2-week report
/bk-track report -f pptx -o report.pptx # PowerPoint format
```

**PPTX Report includes:**
- Title slide (project name, date range)
- Summary slide (metrics: completed, in-progress, at-risk, late)
- Accomplishments slide
- In-progress tasks slide
- Risks & blockers slide
- Next steps slide
- Team workload table
- Japanese font support (Meiryo)

---

### ⚡ summary - Quick Status

One-liner project status for quick checks.

```bash
/bk-track summary
# Output: "PROJECT: 80% healthy | 5 completed | 3 in-progress | 2 late"
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BACKLOG_SPACE_URL` | Backlog workspace URL (e.g., `https://xxx.backlog.jp`) |
| `BACKLOG_API_KEY` | Backlog API key |
| `BACKLOG_PROJECT_KEY` | Default project key (used if --project not set) |

---

## Migration from bk-status/bk-report

| Old Command | New Command |
|-------------|-------------|
| `/bk-status` | `/bk-track status` |
| `/bk-status --threshold 5` | `/bk-track status --threshold 5` |
| `/bk-status --lang ja` | `/bk-track status --lang ja` |
| `/bk-report` | `/bk-track report` |
| `/bk-report --format pptx` | `/bk-track report --format pptx` |
