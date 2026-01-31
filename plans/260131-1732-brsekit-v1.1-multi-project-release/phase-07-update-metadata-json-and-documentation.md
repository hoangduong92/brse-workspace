# Phase 07: Update metadata.json and Documentation

## Context

- Parent: [plan.md](plan.md)
- Depends on: All previous phases

## Overview

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Priority | P2 |
| Effort | 0.5h |
| Status | pending |

Update metadata.json to v1.1.0 and update README with multi-project examples.

## Key Insights

- Current version: 1.0.0
- Need to bump to 1.1.0
- README should show multi-project usage

## Requirements

### metadata.json Changes
```json
{
  "version": "1.1.0",
  "features": {
    "multiProject": true,
    "sharedKnowledge": true
  }
}
```

### README Updates
- Add multi-project section
- Show /bk-init PROJECT usage
- Show --project argument examples

## Related Code Files

### Target
- `experiments/brsekit-starter_v1.0/metadata.json`
- `experiments/brsekit-starter_v1.0/README.md`

## Implementation Steps

1. Update metadata.json version to 1.1.0
2. Add multiProject feature flag
3. Update README with multi-project examples
4. Add directory structure diagram

## Todo List

- [ ] Bump metadata.json version to 1.1.0
- [ ] Add feature flags for multi-project
- [ ] Update README with multi-project usage

## Success Criteria

- [ ] metadata.json shows version 1.1.0
- [ ] README shows multi-project examples

## Release Checklist

After all phases complete:
- [ ] Rename directory to brsekit-starter (remove _v1.0 suffix)
- [ ] Create git tag v1.1.0
- [ ] Push to GitHub
