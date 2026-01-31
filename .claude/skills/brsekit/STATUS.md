# BrseKit Status Report

**Generated:** 2026-01-30
**Version:** v2.0 (post-refactor)

---

## Executive Summary

BrseKit đã hoàn thành refactor từ 10+ skills riêng lẻ → **8 active skills** với **6 deprecated** (đã migrate).
Infrastructure layer (vault/) cung cấp memory, semantic search, và auto-sync cho toàn bộ ecosystem.

---

## Skills Matrix

### Active Skills (8)

| Skill | Purpose | Commands | Test Coverage |
|-------|---------|----------|---------------|
| **bk-init** | Project setup wizard | `/bk-init` | Good (3 files) |
| **bk-track** | Status + Reports (PPTX) | `/bk-track status\|report\|summary` | Good (4 files) |
| **bk-capture** | Parse tasks/meetings | `/bk-capture task\|meeting\|email` | Basic (1 file) |
| **bk-spec** | Requirements + Test docs | `/bk-spec analyze\|test\|feature` | Excellent (7 files) |
| **bk-recall** | Memory & Search | `/bk-recall sync\|search\|summary` | Good (2 files) |
| **bk-convert** | JA↔VI translation | `/bk-convert <text>` | Good (4 files) |
| **bk-morning** | Daily brief | `/bk-morning` | None |
| **bk-write** | Japanese docs | `/bk-write email\|issue\|pr` | Basic (2 files) |

### Deprecated Skills (6) - Ready to Remove

| Old Skill | Migrated To | Status |
|-----------|-------------|--------|
| bk-status | **bk-track status** | ✓ Alias working |
| bk-report | **bk-track report** | ✓ Alias working |
| bk-task | **bk-capture task** | ✓ Alias working |
| bk-minutes | **bk-capture meeting** | ✓ Alias working |
| bk-tester | **bk-spec test** | ✓ Alias working |
| bk-translate | **bk-convert** | ✓ Alias working |

**Recommendation:** Giữ deprecated skills thêm 2 tuần để user quen, sau đó xóa.

---

## Infrastructure Status

### lib/vault/ (18 modules)

| Layer | Modules | Status |
|-------|---------|--------|
| Storage | db.py, memory_store.py, metadata_db.py, directory_manager.py | ✅ Stable |
| Indexing | embedder.py, indexer.py, embedding_store.py | ✅ Stable |
| Search | hybrid_search.py, search.py | ✅ Stable |
| Sync | sync_tracker.py, sync_scheduler.py | ✅ Stable |
| Features | morning_brief.py, unread_detector.py, time_log_store.py | ✅ Stable |

**Test Coverage:** 4 test files (vault core, storage, semantic search, autosync)

---

## Workflow Proposal

### Installation Flow (Recommended)

```
Step 1: User có Claude Code đã cài
        ↓
Step 2: Clone/copy BrseKit vào workspace
        ↓
Step 3: /bk-init [--fresh]
        ├── Collect credentials (Backlog URL, API key)
        ├── Generate .env
        ├── Collect project info
        ├── Generate project-context.yaml
        ├── Verify connection
        └── Show quick start
        ↓
Step 4: User bắt đầu dùng
        /bk-track status
        /bk-recall sync
```

### Enhanced bk-init Wizard

```
/bk-init [options]

Options:
  (default)  - Skip credentials nếu .env đã có
  --fresh    - Reconfigure từ đầu
  --env-only - Chỉ generate .env, skip project config

Flow:
1. [NEW] Check/collect Backlog credentials
2. [NEW] Check/collect Google API key (optional, cho semantic search)
3. [EXISTING] Project info, type, customer, focus areas
4. [EXISTING] Vault config
5. [NEW] Generate .env file
6. [EXISTING] Generate project-context.yaml
7. [NEW] Verify setup (test API connection)
8. [NEW] Show quick start guide
```

### Credential Collection UX

```
=== BrseKit Setup Wizard ===

[Step 1] Backlog Configuration
─────────────────────────────
Paste your Backlog credentials:

Space URL (e.g., your-space.backlog.jp): _
API Key: _

Or paste both in format: URL|KEY
> https://myspace.backlog.jp|xxxxx

Testing connection... ✓ Connected! Found project ABC.

[Step 2] Google Gemini API (optional)
─────────────────────────────────────
For semantic search in bk-recall.
Get key at: https://makersuite.google.com/app/apikey

API Key (Enter to skip): _
```

### Verification Output

```
Setup Complete!
─────────────────

✓ .env exists with BACKLOG_SPACE_URL
✓ .env exists with BACKLOG_API_KEY
✓ Backlog API responds (project: ABC)
✓ project-context.yaml valid
✓ Python venv activated
✓ Dependencies installed

Quick Start:
  /bk-track status     - Check project health
  /bk-recall sync      - Start syncing data
  /brsekit help        - Full documentation
```

---

## Help System

| Command | Purpose |
|---------|---------|
| `/brsekit help` | Full guide (consolidated) |
| `/brsekit skills` | Quick reference table |
| `/brsekit glossary` | IT terms JA↔VI |
| `/<skill> --help` | Skill-specific help |

---

## Release Checklist

### Pre-Release

- [x] Tất cả deprecated skills có redirect message
- [x] Test bk-init wizard trên Windows (99 tests pass)
- [ ] Test bk-init wizard trên Mac/Linux
- [x] Verify .env generation works (env_setup.py added)
- [x] Verify Backlog connection test works
- [x] Update SKILL.md với commands mới
- [ ] Update onboarding-guide.md với new flow

### Skills Testing (2026-01-30)

| Skill | Unit Test | Status | Notes |
|-------|-----------|--------|-------|
| bk-init | 99 pass | ✅ Ready | Enhanced with env_setup.py |
| bk-track | 53 pass / 37 fail | ⚠️ Needs fix | Tests outdated after refactor |
| bk-capture | - | ⬜ Pending | |
| bk-spec | - | ⬜ Pending | |
| bk-recall | - | ⬜ Pending | |
| bk-convert | - | ⬜ Pending | |
| bk-morning | 0 tests | ⬜ No tests | |
| bk-write | - | ⬜ Pending | |

### Post-Release

- [ ] Announce migration deadline cho deprecated skills
- [ ] Monitor user feedback
- [ ] Remove deprecated skills sau 2 tuần

---

## Unresolved Questions

1. **Credential storage location**: `.env` at workspace root hay `.claude/skills/brsekit/.env`?
   - Recommendation: workspace root cho visibility

2. **Multiple projects**: One workspace support nhiều project configs?
   - Current: single project-context.yaml
   - Future: `configs/project-a.yaml`, `configs/project-b.yaml`?

3. **Offline mode**: Skills có nên work (degraded) without Backlog connection?

4. **Version compatibility**: Làm sao handle BrseKit updates breaking existing configs?

---

## Next Steps

1. **Enhance bk-init** - Add credential collection + .env generation
2. **Test each skill** - Run unit + integration tests
3. **Update docs** - Sync onboarding-guide với workflow mới
4. **Deprecation cleanup** - Schedule removal của old skills

---

*Last updated: 2026-01-30*
