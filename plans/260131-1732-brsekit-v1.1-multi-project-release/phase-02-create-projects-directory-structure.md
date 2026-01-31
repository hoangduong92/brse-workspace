# Phase 02: Create projects/ Directory Structure

## Context

- Parent: [plan.md](plan.md)
- Depends on: Phase 01

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Priority | P1 |
| Effort | 0.5h |
| Status | pending |

Create projects/ directory with README.md for per-project data storage.

## Key Insights

- projects/ will contain per-project directories
- Each project has: .env, context.yaml, vault/
- README explains first-run setup

## Requirements

### Functional
- Create projects/ directory
- Create README.md with setup instructions

### Structure
```
projects/
└── README.md
```

## Implementation Steps

1. Create projects/ directory
2. Write README.md with:
   - Purpose explanation
   - How to create projects via bk-init
   - Directory structure per project

## Todo List

- [ ] Create projects/ directory
- [ ] Create projects/README.md

## Success Criteria

- [ ] projects/ directory exists
- [ ] README.md explains setup

## Next Steps

→ Phase 03: Create knowledge/ structure
