# BrseKit v2 Phase 2: Semantic Search

## Overview
- **Priority**: High
- **Status**: ✅ Complete
- **Depends on**: Phase 1 (Storage Infrastructure)
- **Scope**: Integrate Gemini embeddings với per-project vector DB

## Architecture

```
~/.brsekit/
├── db/
│   └── embeddings/
│       └── {project-key}.db     # Per-project ChromaDB/SQLite-vec
└── ...
```

## Key Features

### 1. Per-project Embedding Database
- Mỗi project có vector DB riêng
- Isolation hoàn toàn giữa các dự án
- Dễ backup/migrate từng project

### 2. Hybrid Search
- **Semantic**: Gemini embeddings + cosine similarity
- **Keyword**: Full-text search trong SQLite
- **Combined**: Weighted score = 0.7*semantic + 0.3*keyword

### 3. Search Across Layers
- Search trong Knowledge (glossary, FAQ, specs)
- Search trong Memory (Backlog, Slack, meetings)
- Filter by source, date range, type

## Modules to Create/Modify

### 1. `embedding_store.py` (~100 lines)
```python
class EmbeddingStore:
    def __init__(self, project_key: str)

    def index_item(self, item_id: str, content: str, metadata: dict)
    def index_batch(self, items: List[tuple]) -> int
    def delete_item(self, item_id: str)

    def search(self, query: str, top_k: int = 10,
               min_score: float = 0.5) -> List[SearchResult]
    def search_by_source(self, query: str, source: str,
                         top_k: int = 10) -> List[SearchResult]

    def get_stats(self) -> dict  # {total_items, sources, last_indexed}
```

### 2. `hybrid_search.py` (~80 lines)
```python
class HybridSearch:
    def __init__(self, project_key: str)

    def search(self, query: str, top_k: int = 10,
               semantic_weight: float = 0.7) -> List[SearchResult]

    def search_knowledge(self, query: str, top_k: int = 5)
    def search_memory(self, query: str, source: str = None,
                      start_date: date = None, end_date: date = None)
```

### 3. `indexer.py` (~80 lines)
```python
class Indexer:
    """Background indexer for new content"""

    def __init__(self, project_key: str)

    def index_knowledge(self)  # Index all knowledge files
    def index_memory(self, source: str = None,
                     since: datetime = None)  # Index memory entries
    def reindex_all(self)  # Full reindex

    def get_index_status(self) -> dict
```

### 4. Modify `bk-recall/search_handler.py`
```python
# Before
def query(self, text: str) -> List[SearchResult]:
    return self.vault_search.query(text)

# After
def query(self, text: str, project_key: str = None) -> List[SearchResult]:
    if project_key:
        return self.hybrid_search.search(text)
    else:
        return self.vault_search.query(text)  # Legacy
```

## Implementation Steps

- [x] 1. Create `embedding_store.py` + tests (379 lines)
- [x] 2. Create `hybrid_search.py` + tests (267 lines)
- [x] 3. Create `indexer.py` + tests (345 lines)
- [x] 4. Modify `bk-recall/search_handler.py` (132 lines)
- [x] 5. Add CLI commands for indexing (deferred to Phase 3)
- [x] 6. Integration testing (16/16 tests passing)

## CLI Commands

```bash
# Index project content
/bk-recall index                    # Index all
/bk-recall index --knowledge        # Index knowledge only
/bk-recall index --memory           # Index memory only

# Search with project context
/bk-recall search "query" --project PROJECT_KEY

# Check index status
/bk-recall index-status
```

## Success Criteria

1. Per-project embedding DB created và isolated
2. Semantic search returns relevant results (>0.7 precision)
3. Hybrid search combines keyword + semantic
4. Indexer handles incremental updates
5. Search performance <500ms for 10k items
6. Backward compatible với existing vault search

## Estimated Effort

- **New code**: ~260 lines (3 modules)
- **Tests**: ~200 lines
- **Integration**: ~50 lines
- **Total**: ~510 lines

---
*Created: 2026-01-30*
