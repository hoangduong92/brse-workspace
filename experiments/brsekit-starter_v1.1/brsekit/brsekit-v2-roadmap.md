# BrseKit v2 Roadmap

## Vision
Bộ công cụ AI hỗ trợ BrSE giảm 30-40 phút/ngày cho các công việc lặp đi lặp lại.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        BrseKit v2                               │
├─────────────────────────────────────────────────────────────────┤
│  📦 KNOWLEDGE LAYER (Human-editable)                            │
│  └─ glossary.json, faq.md, rules.md, specs/                    │
├─────────────────────────────────────────────────────────────────┤
│  🧠 MEMORY LAYER (Auto-synced)                                  │
│  └─ backlog/, slack/, email/, meetings/ (JSONL by date)        │
├─────────────────────────────────────────────────────────────────┤
│  🔧 CORE SKILLS                                                 │
│  ├─ /bk-track     : status + members + report                  │
│  ├─ /bk-capture   : task + meeting                             │
│  ├─ /bk-spec      : analyze + test docs                        │
│  ├─ /bk-recall    : search + sync + summary                    │
│  ├─ /bk-convert   : JA↔VI translation                          │
│  └─ /bk-write     : emails, reports (keigo support)            │
├─────────────────────────────────────────────────────────────────┤
│  🎯 COMPOSITE SKILLS                                            │
│  └─ /bk-morning   : morning brief for BrSE                     │
└─────────────────────────────────────────────────────────────────┘
```

## Phases

| Phase | Name | Status | Est. Lines | Description |
|-------|------|--------|------------|-------------|
| 1 | Storage Infrastructure | ✅ Complete | ~1,060 | Directory structure, Knowledge/Memory stores, Metadata DB |
| 2 | Semantic Search | ✅ Complete | ~510 | Per-project embeddings, Hybrid search, Indexer |
| 3 | Auto-sync & Morning Brief | ✅ Complete | ~460 | Comments sync, Unread detection, `/bk-morning` |
| **Total** | | | **~2,030** | |

## Phase Details

### Phase 1: Storage Infrastructure
**File:** [phase1-storage-infrastructure-plan.md](phase1-storage-infrastructure-plan.md)

**Modules:**
- `directory_manager.py` - Project folder structure
- `metadata_db.py` - SQLite for fast lookups
- `memory_store.py` - JSONL append-only storage
- `knowledge_store.py` - Human-editable files CRUD
- `unread_detector.py` - Cutoff time logic
- `compat.py` - Legacy vault.db migration

**Key Decisions:**
- Gzip compression sau 7 ngày
- Archive sau 30 ngày
- Per-project isolation

---

### Phase 2: Semantic Search
**File:** [phase2-semantic-search-plan.md](phase2-semantic-search-plan.md)

**Modules:**
- `embedding_store.py` - Per-project vector DB
- `hybrid_search.py` - Semantic + keyword combined
- `indexer.py` - Background content indexing

**Key Features:**
- Hybrid search (70% semantic + 30% keyword)
- Search across Knowledge + Memory
- Incremental indexing

---

### Phase 3: Auto-sync & Morning Brief
**File:** [phase3-auto-sync-plan.md](phase3-auto-sync-plan.md)

**Modules:**
- `backlog_sync.py` - Enhanced with comments sync
- `morning_brief.py` - Generate daily summary
- `sync_scheduler.py` - Periodic sync management

**New Skill:**
- `/bk-morning` - Morning brief for BrSE

---

## Implementation Order

```
Phase 1 ──────────────────────────────────────────────►
         │
         │ depends on
         ▼
Phase 2 ──────────────────────────────────────────────►
         │
         │ depends on
         ▼
Phase 3 ──────────────────────────────────────────────►
```

## Usage After v2

```bash
# Morning routine (Phase 3)
/bk-morning

# Search anything (Phase 2)
/bk-recall search "login bug"

# Track project (existing, enhanced)
/bk-track status
/bk-track report --format pptx

# Capture tasks (existing)
/bk-capture task "email content..."

# Write reports (existing, to be enhanced)
/bk-write email --tone careful --explain
```

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Morning prep time | -30 min/day | User feedback |
| Search relevance | >70% precision | Manual evaluation |
| Sync latency | <5 sec | Performance test |
| Report generation | <10 sec | Performance test |

---

## Commands to Implement

```bash
# Invoke implementation
implement phase1
implement phase2
implement phase3
```

---
*Last updated: 2026-01-30*
