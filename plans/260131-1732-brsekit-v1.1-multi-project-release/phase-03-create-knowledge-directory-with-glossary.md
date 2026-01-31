# Phase 03: Create knowledge/ Directory with Glossary

## Context

- Parent: [plan.md](plan.md)
- Depends on: Phase 02

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Priority | P1 |
| Effort | 0.5h |
| Status | pending |

Create knowledge/ directory with shared glossary-it-terms.json.

## Key Insights

- knowledge/ stores workspace-level shared resources
- glossary-it-terms.json used by bk-convert for JA↔VI translation
- Breaking change from v1.0 glossaries/ path

## Requirements

### Functional
- Create knowledge/ directory
- Copy glossary-it-terms.json from local

### Structure
```
knowledge/
└── glossary-it-terms.json
```

## Related Code Files

### Source
- `.claude/skills/bk-convert/glossaries/default-it-terms.json` (or similar)

### Target
- `experiments/brsekit-starter_v1.0/knowledge/glossary-it-terms.json`

## Implementation Steps

1. Create knowledge/ directory
2. Copy/create glossary-it-terms.json with IT terms
3. Ensure JSON structure: `{"terms": {"term": "translation", ...}}`

## Todo List

- [ ] Create knowledge/ directory
- [ ] Create glossary-it-terms.json

## Success Criteria

- [ ] knowledge/ directory exists
- [ ] glossary-it-terms.json is valid JSON

## Next Steps

→ Phase 04: Update bk-init for multi-project
