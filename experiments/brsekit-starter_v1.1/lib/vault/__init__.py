"""Vault infrastructure - SQLite + semantic search for BrseKit memory layer."""
# Legacy v1 modules (backward compatible)
from .db import VaultDB
from .embedder import GeminiEmbedder
from .store import VaultStore, VaultItem
from .search import VaultSearch, SearchResult
from .sync_tracker import SyncTracker
from .time_log_store import TimeLogStore, TimeLogEntry

# v2 Phase 1 modules - per-project storage
from .directory_manager import DirectoryManager
from .metadata_db import (
    MetadataDB,
    ProjectRegistry,
    ProjectInfo,
    SyncStateManager,
    ReadMarkerManager,
)
from .memory_store import MemoryStore, MemoryEntry
from .knowledge_store import KnowledgeStore, GlossaryEntry
from .unread_detector import UnreadDetector
from .compat import LegacyMigrator

# v2 Phase 2 modules - semantic search
from .embedding_store import EmbeddingStore, EmbeddingItem
from .embedding_store import SearchResult as EmbeddingSearchResult
from .hybrid_search import HybridSearch
from .indexer import Indexer

# v2 Phase 3 modules - auto-sync & morning brief
from .morning_brief import MorningBrief
from .sync_scheduler import SyncScheduler, SyncStatus

__all__ = [
    # Legacy v1
    "VaultDB",
    "GeminiEmbedder",
    "VaultStore",
    "VaultItem",
    "VaultSearch",
    "SearchResult",
    "SyncTracker",
    "TimeLogStore",
    "TimeLogEntry",
    # v2 Phase 1 - Directory & Metadata
    "DirectoryManager",
    "MetadataDB",
    "ProjectRegistry",
    "ProjectInfo",
    "SyncStateManager",
    "ReadMarkerManager",
    # v2 Phase 1 - Storage
    "MemoryStore",
    "MemoryEntry",
    "KnowledgeStore",
    "GlossaryEntry",
    # v2 Phase 1 - Unread & Compat
    "UnreadDetector",
    "LegacyMigrator",
    # v2 Phase 2 - Semantic Search
    "EmbeddingStore",
    "EmbeddingItem",
    "EmbeddingSearchResult",
    "HybridSearch",
    "Indexer",
    # v2 Phase 3 - Auto-sync & Morning Brief
    "MorningBrief",
    "SyncScheduler",
    "SyncStatus",
]
