---
title: "BrseKit v2 Refactor"
description: "Major redesign: 9 skills → 7 skills + memory layer"
status: completed
priority: P1
effort: 2w
branch: main
tags: [brsekit, refactor, memory, vault, v2]
created: 2026-01-29
validated: 2026-01-29
---

# BrseKit v2 Refactor - Overview Plan

## Target Architecture

| Category | Skill | Purpose |
|----------|-------|---------|
| SETUP | `bk-init` | Project setup, PM mindset |
| MEMORY | `bk-recall` | Store + Search + Summary (vault invisible) |
| MONITOR | `bk-track` | Merge status + report (MD/PPTX) |
| CAPTURE | `bk-capture` | Merge task + minutes |
| ANALYZE | `bk-spec` | Merge analyze + tester |
| WRITE | `bk-write` | Keep as-is |
| WRITE | `bk-convert` | Rename from bk-translate |

**Infrastructure:** `lib/vault/` - SQLite + sqlite-vec + Gemini embeddings

## Phases Summary

| Phase | Name | Status | Completion | Dependencies |
|-------|------|--------|------------|--------------|
| [0](./phase-00-vault-infrastructure.md) | Vault Infrastructure | ✅ done | 100% | None |
| [1](./phase-01-bk-recall.md) | bk-recall | ✅ done | 100% | Phase 0 |
| [2](./phase-02-bk-track.md) | bk-track | ✅ done | 100% | Phase 0 |
| [3](./phase-03-bk-capture.md) | bk-capture | ✅ done | 100% | Phase 0, 1 |
| [4](./phase-04-bk-spec.md) | bk-spec | ✅ done | 100% | Phase 1 |
| [5](./phase-05-bk-init.md) | bk-init | ✅ done | 100% | None |
| [6](./phase-06-alias-layer.md) | Alias Layer | ✅ done | 100% | Phase 2-5 |
| [7](./phase-07-pptx-integration.md) | PPTX Integration | ✅ done | 100% | Phase 2 |

**Overall Progress: 100%** (all phases complete, ready for manual QA)

## Key Decisions

1. **Vault**: Invisible infrastructure, auto-called from bk-capture, bk-recall sync
2. **bk-recall**: Queryable by bk-spec for context enrichment
3. **Embedding**: Gemini API (free tier: 1000/day)
4. **Migration**: Alias layer for backward compatibility
5. **Sync priority**: email → meeting → slack → backlog → gchat
6. **Code reuse**: ~70-90% existing logic preserved

## Risk Assessment

- Gemini API rate limits (1000 embeddings/day free tier)
- SQLite sqlite-vec cross-platform compatibility
- Alias layer complexity for edge cases

## Reports

- [Existing Skills Analysis](./research/researcher-existing-skills-report.md)
- [Vault Patterns Research](./research/researcher-vault-patterns-report.md)

---

## Validation Summary

**Validated:** 2026-01-29
**Questions asked:** 6

### Confirmed Decisions

| Decision | User Choice |
|----------|-------------|
| Email auth method | Gmail API + OAuth (setup Google Cloud project) |
| Rate limit exceeded | Queue & batch next day (store pending, embed on quota reset) |
| sqlite-vec fallback | Brute-force cosine similarity (slower but portable) |
| Vault save timing | Async non-blocking (user sees output immediately) |
| Deprecation warnings | Single line notice (short, then normal output) |
| PPTX template | BrSE-specific (JP-style: Summary, Progress, Risks, Next Week) |

### Action Items

- [x] Update phase-01-bk-recall.md: Use Gmail API OAuth, not IMAP
- [x] Update phase-00-vault-infrastructure.md: Add queue system for rate limit
- [x] Update phase-00-vault-infrastructure.md: Implement brute-force fallback when sqlite-vec unavailable
- [x] Update phase-03-bk-capture.md: Vault save is async, non-blocking
- [x] Update phase-06-alias-layer.md: Single line deprecation notice
- [x] Update phase-07-pptx-integration.md: Create BrSE-specific JP template
