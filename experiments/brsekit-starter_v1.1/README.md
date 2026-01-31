# BrseKit Starter v1.1.0

AI-powered toolkit for Bridge System Engineers (BrSE).

## What's New in v1.1

- **Cleaned up deprecated skills**: Removed 6 deprecated skills (bk-status, bk-report, bk-task, bk-minutes, bk-tester, bk-translate)
- **Streamlined structure**: Only 9 active skills + shared libraries
- **Unified experience**: All functionality preserved in consolidated skills

## Installation

```bash
# Install CLI
npm install -g brsekit-cli

# Initialize in your project
bk init
```

## Skills

| Skill | Description | Commands |
|-------|-------------|----------|
| **bk-track** | Project tracking, weekly reports | `status`, `report`, `summary` |
| **bk-capture** | Parse tasks, meeting notes | `task`, `meeting`, `email` |
| **bk-spec** | Requirement analysis, test docs | `analyze`, `test`, `feature` |
| **bk-recall** | Memory layer, semantic search | `sync`, `search`, `summary` |
| **bk-convert** | JA<->VI translation | `text`, `excel`, `pptx` |
| **bk-init** | Setup wizard | `setup` |
| **bk-morning** | Morning brief | `brief` |
| **bk-write** | Japanese documents | `email`, `report`, `spec` |
| **brsekit** | Help & documentation | `help`, `skills` |

## Quick Start

```bash
# Check project status
/bk-track status --threshold 3 --lang ja

# Generate weekly report (PPTX)
/bk-track report --format pptx --output weekly.pptx

# Parse tasks from text
/bk-capture task "明日までにログイン機能を実装"

# Search project context
/bk-recall search "payment integration"

# Translate JA->VI
/bk-convert "テストを実施しました"
```

## Configuration

Create `.env` in `.claude/skills/`:

```bash
BACKLOG_SPACE_URL=https://xxx.backlog.jp
BACKLOG_API_KEY=your-api-key
BACKLOG_PROJECT_KEY=PROJECT
GOOGLE_API_KEY=your-gemini-key  # Optional: for semantic search
```

## Requirements

- Python >= 3.9
- Node.js >= 18.0.0
- Claude Code CLI

## License

MIT
