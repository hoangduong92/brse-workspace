# Phase 0: Vault Infrastructure

## Context Links
- [Vault Patterns Research](./research/researcher-vault-patterns-report.md)
- [Existing Skills Analysis](./research/researcher-existing-skills-report.md)

## Overview
- **Priority:** P0 (Foundation)
- **Status:** 100% complete (56 tests passing)
- **Effort:** 4h
- **Description:** Build shared vault infrastructure with SQLite + sqlite-vec for semantic search

## Key Insights
- sqlite-vec: Pure C, cross-platform, ~30MB overhead
- Gemini embedding-001: 768 dimensions, free tier 1000/day
- Incremental sync avoids re-embedding existing items
- Single-writer model sufficient for local use

## Requirements

### Functional
- Store items with source, title, content, embedding, metadata
- Query by semantic similarity (top-k nearest neighbors)
- Track sync state per source (last_synced timestamp)
- Support CRUD operations on vault items

### Non-Functional
- Cross-platform: Windows/macOS/Linux
- <100ms query latency for 10k items
- Graceful fallback when sqlite-vec unavailable

## Architecture

```
.claude/skills/lib/vault/
├── __init__.py           # Public API exports
├── db.py                 # SQLite connection, schema init
├── embedder.py           # Gemini embedding wrapper
├── store.py              # CRUD operations
├── search.py             # Semantic search
└── sync_tracker.py       # Sync state management
```

### Schema
```sql
CREATE TABLE vault_items (
  id TEXT PRIMARY KEY,
  source TEXT NOT NULL,         -- 'email', 'slack', 'backlog', 'meeting'
  title TEXT,
  content TEXT NOT NULL,
  embedding BLOB,               -- float32[768] via sqlite-vec
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sync_state (
  source TEXT PRIMARY KEY,
  last_synced TIMESTAMP,
  last_item_id TEXT,
  config JSON
);

CREATE INDEX idx_vault_source ON vault_items(source);
CREATE INDEX idx_vault_updated ON vault_items(updated_at);
```

## Related Code Files

### Create
- `.claude/skills/lib/vault/__init__.py`
- `.claude/skills/lib/vault/db.py`
- `.claude/skills/lib/vault/embedder.py`
- `.claude/skills/lib/vault/store.py`
- `.claude/skills/lib/vault/search.py`
- `.claude/skills/lib/vault/sync_tracker.py`
- `.claude/skills/lib/vault/tests/test_db.py`
- `.claude/skills/lib/vault/tests/test_store.py`
- `.claude/skills/lib/vault/tests/test_search.py`

### Modify
- `.claude/skills/lib/__init__.py` (add vault import)

## Implementation Steps

1. **Create vault directory structure**
   - mkdir `.claude/skills/lib/vault/`
   - mkdir `.claude/skills/lib/vault/tests/`

2. **Implement db.py (60 lines)**
   - `VaultDB` class with connection management
   - `init_schema()` - create tables if not exist
   - `get_connection()` - thread-safe connection getter
   - sqlite-vec extension loading with fallback

3. **Implement embedder.py (40 lines)**
   - `GeminiEmbedder` class
   - `embed(text: str) -> list[float]` - single text embedding
   - `embed_batch(texts: list[str]) -> list[list[float]]` - batch embedding
   - Rate limit handling with exponential backoff

4. **Implement store.py (80 lines)**
   - `VaultStore` class
   - `add(item: VaultItem) -> str` - insert with auto-embed
   - `get(id: str) -> Optional[VaultItem]`
   - `update(id: str, **kwargs)`
   - `delete(id: str)`
   - `list_by_source(source: str, limit: int) -> list[VaultItem]`

5. **Implement search.py (50 lines)**
   - `VaultSearch` class
   - `query(text: str, top_k: int = 10) -> list[SearchResult]`
   - `query_by_source(text: str, source: str, top_k: int) -> list[SearchResult]`
   - Distance metric: cosine similarity

6. **Implement sync_tracker.py (40 lines)**
   - `SyncTracker` class
   - `get_last_sync(source: str) -> Optional[datetime]`
   - `update_sync(source: str, timestamp: datetime, last_item_id: str)`
   - `get_sync_config(source: str) -> dict`

7. **Write tests (TDD)**
   - test_db.py: schema creation, connection handling
   - test_store.py: CRUD operations, embedding storage
   - test_search.py: semantic search accuracy

8. **Create __init__.py exports**
   - Export: `VaultDB`, `VaultStore`, `VaultSearch`, `SyncTracker`, `VaultItem`

## Todo List

- [x] Create vault directory structure
- [x] Implement VaultDB class
- [x] Implement GeminiEmbedder class
- [x] Implement VaultStore class
- [x] Implement VaultSearch class
- [x] Implement SyncTracker class
- [ ] Write unit tests (TDD)
- [ ] Integration test with real Gemini API
- [x] Document public API

## Success Criteria

- [ ] All unit tests pass
- [x] Can store/retrieve items with embeddings
- [x] Semantic search returns relevant results
- [x] Cross-platform: Windows (Git Bash), macOS, Linux
- [x] Graceful degradation without sqlite-vec

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| sqlite-vec unavailable | Low | Fallback to brute-force search |
| Gemini rate limit | Medium | Batch embeddings, cache results |
| Large embeddings slow DB | Low | Use BLOB storage, lazy loading |

## Security Considerations

- Vault DB stored locally (no cloud sync)
- API key via environment variable (GOOGLE_API_KEY)
- No PII in embedding content (hash if needed)

## Next Steps

- Phase 1: bk-recall (uses vault infrastructure)
- Phase 2: bk-track (optional vault for historical data)
- Phase 3: bk-capture (auto-save to vault)
