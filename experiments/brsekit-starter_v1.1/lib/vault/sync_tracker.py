"""Sync state management for vault sources."""
import json
from datetime import datetime
from typing import Optional, Dict, Any

from .db import VaultDB


class SyncTracker:
    """Track sync state for different vault sources."""

    def __init__(self):
        """Initialize sync tracker."""
        VaultDB.initialize()

    def get_last_sync(self, source: str) -> Optional[datetime]:
        """Get last sync timestamp for source."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_synced FROM sync_state WHERE source = ?",
            (source,)
        )
        row = cursor.fetchone()

        if row and row[0]:
            return datetime.fromisoformat(row[0])
        return None

    def update_sync(
        self,
        source: str,
        timestamp: datetime,
        last_item_id: Optional[str] = None
    ):
        """Update sync state for source."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sync_state (source, last_synced, last_item_id)
            VALUES (?, ?, ?)
            ON CONFLICT(source) DO UPDATE SET
                last_synced = excluded.last_synced,
                last_item_id = excluded.last_item_id
        """, (source, timestamp.isoformat(), last_item_id))

        conn.commit()

    def get_sync_config(self, source: str) -> Dict[str, Any]:
        """Get sync configuration for source."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT config FROM sync_state WHERE source = ?",
            (source,)
        )
        row = cursor.fetchone()

        if row and row[0]:
            return json.loads(row[0])
        return {}

    def update_sync_config(self, source: str, config: Dict[str, Any]):
        """Update sync configuration for source."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sync_state (source, config)
            VALUES (?, ?)
            ON CONFLICT(source) DO UPDATE SET
                config = excluded.config
        """, (source, json.dumps(config)))

        conn.commit()

    def get_last_item_id(self, source: str) -> Optional[str]:
        """Get last synced item ID for source."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_item_id FROM sync_state WHERE source = ?",
            (source,)
        )
        row = cursor.fetchone()

        return row[0] if row else None
