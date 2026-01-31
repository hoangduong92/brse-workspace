# Memory/Vault System with Semantic Search: Research Report

## Executive Summary
SQLite + embeddings is production-ready for local semantic search. Gemini embedding API offers free tier suitable for prototyping; SQLite extensions (sqlite-vec, SQLite-Vector) enable native vector search. Incremental sync patterns reduce overhead for multi-source data ingestion.

## Architecture Recommendations

### Storage Layer (KISS Principle)
**Recommended: SQLite + sqlite-vec extension**
- Native vector search capability without external DB dependencies
- sqlite-vec: Pure C, no dependencies, runs on all platforms (iOS, Android, Linux, macOS, Windows, WASM)
- Atomic transactions for safe concurrent writes
- ~30MB memory footprint base overhead
- Handles tens of thousands of embeddings per machine efficiently

**Schema Design:**
```sql
CREATE TABLE vault_items (
  id TEXT PRIMARY KEY,
  source TEXT,              -- 'email', 'slack', 'backlog'
  title TEXT,
  content TEXT,
  embedding FLOAT32[768],   -- Gemini embeddings (768 dims)
  metadata JSON,            -- sync timestamp, source_id
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE INDEX idx_source ON vault_items(source);
CREATE INDEX idx_updated ON vault_items(updated_at);
-- sqlite-vec for vector search:
-- SELECT * FROM vault_items WHERE embedding MATCH ? ORDER BY distance LIMIT 10
```

### Embedding API Strategy

**Gemini Embedding API (gemini-embedding-001)**
- Free tier: 100 RPM, 1,000 RPD — suitable for incremental syncs
- Pricing: $0.15/1M tokens (paid tier)
- **Batch strategy for free tier:** Queue embeddings, batch process daily to stay within limits
- **Error handling:** Retry with exponential backoff, cache results in SQLite

**Implementation Pattern:**
- Embed new/updated items only (incremental)
- Cache embeddings in SQLite to avoid re-processing
- Daily batch job: collect pending items → embed via Gemini → store in DB

### Vector Similarity Search

**Query Pattern:**
```sql
SELECT id, title, distance
FROM vault_items
WHERE embedding MATCH query_vector
ORDER BY distance
LIMIT 10;
```

**Performance Notes:**
- sqlite-vec uses SIMD acceleration for distance metrics (euclidean, cosine)
- K-nearest neighbor search is native, not approximate
- Scale: tens of thousands embeddings practical; millions would need distributed solution

## Data Sync Strategy

### Incremental Sync Architecture
**Pull-based pattern (KISS > push complexity):**

1. **Email Source**
   - Store last sync timestamp in metadata table
   - Query only messages after timestamp (IMAP UID SEARCH, Gmail API)
   - Extract subject + body → vault_items

2. **Slack Source**
   - Use conversations API with ts > last_sync_timestamp
   - Store message_ts as source_id for idempotency
   - Extract thread_id, message text → vault_items

3. **Backlog Source**
   - Similar pattern: query updated_at > last_sync_timestamp
   - API-specific rate limits: honor them

**Sync Frequency:**
- Full sync: weekly (refresh everything)
- Incremental: daily or hourly (new/modified items only)
- Schedule: avoid Gemini API rate limit collisions

### Metadata for Sync Tracking
```json
{
  "source": "email",
  "source_id": "gmail:message:abc123",
  "last_synced": "2026-01-29T12:00:00Z",
  "sync_version": 1,
  "external_url": "https://mail.google.com/mail/u/0/#inbox/abc123"
}
```

## Implementation Priorities

1. **Phase 1:** SQLite schema + sqlite-vec setup, Gemini API wrapper
2. **Phase 2:** Email sync (IMAP/Gmail), basic semantic search
3. **Phase 3:** Slack integration, sync orchestration
4. **Phase 4:** Backlog integration, UI/search interface
5. **Phase 5:** Caching, performance tuning

## Known Constraints

- **Gemini free tier:** 1,000 embeddings/day max (plan accordingly)
- **SQLite limitation:** Single-writer, good for local use; multi-writer requires Turso/libSQL
- **Embedding dimensions:** Gemini 768-dim vectors; optimize before SQLite storage if needed
- **Duplicate handling:** Use source_id + timestamp for idempotency detection

## Unresolved Questions

- How to handle embedding schema changes if Gemini updates dimensions?
- Should we implement local offline embeddings fallback (e.g., ONNX) for rate limit exceed scenarios?
- Multi-user sync strategy (currently designed for single-writer model)?

---

**Sources:**
- [sqlite-vec: Vector Search in SQLite](https://github.com/asg017/sqlite-vec)
- [SQLite-Vector: Cross-Platform Extension](https://github.com/sqliteai/sqlite-vector)
- [Gemini API Pricing & Rate Limits](https://ai.google.dev/gemini-api/docs/pricing)
- [Using SQLite as LLM Vector Database](https://turso.tech/blog/using-sqlite-as-your-llm-vector-database)
- [Slack Data Integration Patterns](https://docs.airbyte.com/integrations/sources/slack)
