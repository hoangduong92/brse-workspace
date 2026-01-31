# BrseKit v2 Phase 1: Basic Storage Infrastructure

## Overview
- **Priority**: High
- **Status**: ✅ Completed (2026-01-30)
- **Scope**: Create foundational storage layer with Knowledge + Memory separation

## Architecture

```
~/.brsekit/
├── projects/
│   └── {project-key}/
│       ├── knowledge/           # Human-editable (markdown/json)
│       │   ├── glossary.json
│       │   ├── faq.md
│       │   ├── rules.md
│       │   └── specs/
│       ├── memory/              # Auto-synced (JSONL, append-only)
│       │   ├── backlog/
│       │   │   └── YYYY-MM-DD.jsonl
│       │   ├── slack/
│       │   ├── email/
│       │   └── meetings/
│       ├── templates/           # User templates
│       └── archive/             # Auto-archived files (>30 days)
├── db/
│   ├── metadata.sqlite          # Fast lookup, sync state
│   └── embeddings/
│       └── {project-key}.db     # Per-project vector DB
├── vault.db                     # Legacy (backward compat)
└── config.json                  # Global config
```

## Key Decisions
- **JSONL Compression**: Gzip sau 7 ngày (*.jsonl.gz)
- **Embedding DB**: Per-project isolation
- **Cleanup**: Archive sau 30 ngày → `archive/` folder

## Modules to Create

### 1. `directory_manager.py` (~60 lines)
```python
class DirectoryManager:
    def ensure_project_structure(project_key: str) -> Path
    def get_knowledge_path(project_key: str) -> Path
    def get_memory_path(project_key: str, source: str) -> Path
    def list_projects() -> List[str]
```

### 2. `metadata_db.py` (~120 lines)
```python
# Schema
- projects: project_key, name, created_at, config
- sync_state: project_key, source, last_synced, last_item_id, cursor
- file_index: project_key, layer, file_path, entry_count, timestamps
- read_markers: project_key, source, last_read_at

class MetadataDB  # Singleton, thread-safe
class ProjectRegistry  # Project CRUD
```

### 3. `memory_store.py` (~100 lines)
```python
@dataclass
class MemoryEntry:
    id, source, timestamp, content, metadata, synced_at

class MemoryStore:
    def append(source: str, entry: MemoryEntry)
    def append_batch(source: str, entries: List) -> int
    def read_entries(source: str, start_date, end_date) -> List
    def compress_old_files(days_threshold: int = 7)  # Gzip
    def archive_old_files(days_threshold: int = 30)  # Move to archive/
```

### 4. `knowledge_store.py` (~120 lines)
```python
@dataclass
class GlossaryEntry:
    term, definition, aliases, category

class KnowledgeStore:
    # Glossary
    def get_glossary() -> Dict[str, GlossaryEntry]
    def add_term(term, definition, aliases)
    # FAQ/Rules
    def get_faq() -> str
    def update_faq(content: str)
    # Specs
    def list_specs() -> List[str]
    def get_spec(name: str) -> str
    def save_spec(name: str, content: str)
```

### 5. `unread_detector.py` (~80 lines)
```python
class UnreadDetector:
    def get_cutoff_time(source: str) -> datetime
        # Logic: max(last_sync, 18:00_yesterday)
    def mark_as_read(source: str)
    def get_unread_entries(source: str, limit: int) -> List
    def get_unread_summary() -> Dict[str, int]
```

### 6. `compat.py` (~80 lines)
```python
class LegacyMigrator:
    def detect_legacy_data() -> bool
    def migrate_to_project(project_key: str)
    def backup_vault() -> Path
```

## Files to Modify

| File | Change |
|------|--------|
| `lib/vault/__init__.py` | Export new modules |
| `bk-recall/scripts/sync_manager.py` | Add project_key parameter |
| `bk-recall/scripts/sources/backlog_sync.py` | Use MemoryStore when project set |

## Implementation Steps

- [ ] 1. Create `directory_manager.py` + tests
- [ ] 2. Create `metadata_db.py` + tests
- [ ] 3. Create `memory_store.py` + tests (with gzip + archive)
- [ ] 4. Create `knowledge_store.py` + tests
- [ ] 5. Create `unread_detector.py` + tests
- [ ] 6. Create `compat.py` + tests
- [ ] 7. Update `bk-recall` sync integration
- [ ] 8. Update `__init__.py` exports
- [ ] 9. Integration testing

## Success Criteria

1. Directory structure created correctly for new projects
2. Knowledge files CRUD works (glossary, FAQ, rules, specs)
3. Memory JSONL append works with date-based files
4. Gzip compression runs for files >7 days old
5. Archive moves files >30 days to archive/
6. Unread detection works with both last_sync and 18:00 cutoff
7. Existing vault.db continues to work
8. All unit tests pass (target: 40+ tests)

## Verification

```bash
# Run tests
cd .claude/skills
.venv/Scripts/python.exe -m pytest lib/vault/tests/ -v

# Manual test
.venv/Scripts/python.exe -c "
from lib.vault import DirectoryManager, MemoryStore, UnreadDetector
dm = DirectoryManager()
dm.ensure_project_structure('TEST-PROJECT')
ms = MemoryStore('TEST-PROJECT')
# ... test operations
"
```

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Cross-platform paths | Use pathlib everywhere |
| JSONL corruption | Atomic writes with temp files |
| Large archives | Gzip compression + daily rotation |
| Migration data loss | Backup vault.db first |

## Estimated Effort

- **New code**: ~560 lines (6 modules)
- **Tests**: ~400 lines (40+ test cases)
- **Integration**: ~100 lines (modify existing)
- **Total**: ~1,060 lines

---
*Created: 2026-01-30*
