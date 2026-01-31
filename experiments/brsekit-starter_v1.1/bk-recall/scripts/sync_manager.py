"""Sync manager for bk-recall - orchestrates source syncs."""
import os
import sys
from typing import Dict, List, Optional

# Add lib path for vault imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

from sources import BacklogSync, EmailSync


class SyncManager:
    """Orchestrate syncing from multiple sources."""

    SOURCES = {
        "email": EmailSync,
        "backlog": BacklogSync,
    }

    def __init__(self, project_key: Optional[str] = None):
        """Initialize sync manager.

        Args:
            project_key: Optional project key for v2 project-aware sync
        """
        self._syncers = {}
        self.project_key = project_key or os.getenv("BACKLOG_PROJECT_KEY")

    def get_syncer(self, source: str):
        """Get or create syncer for source."""
        if source not in self._syncers:
            if source not in self.SOURCES:
                raise ValueError(f"Unknown source: {source}")
            self._syncers[source] = self.SOURCES[source]()
        return self._syncers[source]

    def sync(self, source: str, **kwargs) -> Dict:
        """Sync from specific source.

        Args:
            source: Source name (email, backlog)
            **kwargs: Source-specific options
                - use_memory: Use v2 MemoryStore (default: True if project_key set)
                - project_key: Override project key

        Returns:
            Sync result dict
        """
        syncer = self.get_syncer(source)
        project_key = kwargs.get("project_key") or self.project_key
        use_memory = kwargs.get("use_memory", bool(project_key))

        if source == "backlog":
            if not project_key:
                return {"error": "project_key required for backlog sync", "synced": 0}

            # Use v2 MemoryStore if project_key is set
            if use_memory:
                return syncer.sync_to_memory(
                    project_key,
                    limit=kwargs.get("limit", 100),
                    sync_comments=kwargs.get("sync_comments", True)
                )
            else:
                # Legacy vault sync
                return syncer.sync(project_key, limit=kwargs.get("limit", 100))

        elif source == "email":
            return syncer.sync(
                query=kwargs.get("query", "is:inbox"),
                limit=kwargs.get("limit", 50)
            )

        return {"error": f"Sync not implemented for {source}", "synced": 0}

    def sync_comments(self, project_key: Optional[str] = None, **kwargs) -> Dict:
        """Sync only Backlog comments to MemoryStore.

        Args:
            project_key: Backlog project key
            **kwargs: Options
                - issue_keys: List of specific issue keys to sync
                - limit: Max comments per issue

        Returns:
            Sync result dict
        """
        project_key = project_key or self.project_key
        if not project_key:
            return {"error": "project_key required", "synced": 0}

        syncer = self.get_syncer("backlog")
        return syncer.sync_comments_only(
            project_key,
            issue_keys=kwargs.get("issue_keys"),
            limit=kwargs.get("limit", 50)
        )

    def sync_all(self, sources: Optional[List[str]] = None, **kwargs) -> Dict:
        """Sync from all configured sources.

        Args:
            sources: List of sources to sync (default: all)
            **kwargs: Source-specific options

        Returns:
            Combined sync results
        """
        sources = sources or list(self.SOURCES.keys())
        results = {}
        total_synced = 0

        for source in sources:
            try:
                result = self.sync(source, **kwargs)
                results[source] = result
                total_synced += result.get("synced", 0)
            except Exception as e:
                results[source] = {"error": str(e), "synced": 0}

        return {
            "total_synced": total_synced,
            "sources": results
        }
