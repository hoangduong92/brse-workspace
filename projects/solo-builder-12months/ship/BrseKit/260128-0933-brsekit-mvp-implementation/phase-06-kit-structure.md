# Phase 6: Kit Structure Finalization

## Overview
- **Priority:** P1
- **Status:** pending
- **Description:** Finalize BrseKit structure, CLAUDE.md, hooks, install scripts

## Deliverables

### 1. CLAUDE.md
Kit entry point với:
- Skill index
- Quick start guide
- Command reference

### 2. Hooks
- `prevent-external-without-approval.py` - Block external actions
- `sensitive-data-filter.py` - Warn about credentials

### 3. Install Scripts
- `install.sh` (Linux/Mac)
- `install.ps1` (Windows)

### 4. README.md
- What is BrseKit
- Installation
- Usage
- Contributing

### 5. Shared lib/
- `backlog_client.py` - Extended Backlog API client
- `language_detector.py` - JA/VI detection
- `models.py` - Data models

## Final Structure
```
brsekit/
├── CLAUDE.md
├── README.md
├── install.sh
├── install.ps1
├── .env.example
├── skills/
│   ├── bk-status/
│   ├── bk-report/
│   ├── bk-task/
│   ├── bk-write/
│   └── bk-translate/
├── hooks/
├── lib/
└── tests/
```

## Detailed plan: TBD after core skills complete
