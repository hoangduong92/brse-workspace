# Phase 06: Update Install Scripts for New Directories

## Context

- Parent: [plan.md](plan.md)
- Depends on: Phase 02, 03

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Priority | P2 |
| Effort | 1h |
| Status | pending |

Update install.sh and install.ps1 to create new directory structure.

## Key Insights

- Install scripts need to create projects/, knowledge/
- Should copy glossary-it-terms.json to knowledge/
- Post-install message should mention /bk-init

## Requirements

### Directories to Create
- `projects/` with README.md
- `knowledge/` with glossary-it-terms.json

### Post-install Message
```
BrseKit v1.1 installed successfully!

Next steps:
  1. Create a project: /bk-init PROJECT_NAME
  2. Check status: /bk-track status PROJECT_NAME
```

## Related Code Files

### Target
- `experiments/brsekit-starter_v1.0/install.sh`
- `experiments/brsekit-starter_v1.0/install.ps1`

## Implementation Steps

1. Read current install.sh structure
2. Add mkdir for projects/ and knowledge/
3. Add cp for README.md and glossary
4. Update post-install message
5. Mirror changes to install.ps1

## Todo List

- [ ] Update install.sh with new directories
- [ ] Update install.ps1 with new directories
- [ ] Add post-install message about bk-init

## Success Criteria

- [ ] Fresh install creates projects/ and knowledge/
- [ ] glossary-it-terms.json copied to knowledge/
- [ ] Post-install shows next steps

## Next Steps

→ Phase 07: Update metadata and docs
