"""CRUD operations for vault items with auto-embedding."""
import json
import struct
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict

from .db import VaultDB
from .embedder import GeminiEmbedder


@dataclass
class VaultItem:
    """Vault item data model."""
    id: str
    source: str
    content: str
    title: Optional[str] = None
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VaultStore:
    """CRUD operations for vault items."""

    def __init__(self, embedder: Optional[GeminiEmbedder] = None):
        """Initialize store with optional embedder."""
        self.embedder = embedder
        VaultDB.initialize()

    def add(self, item: VaultItem) -> str:
        """Insert item with auto-embedding."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        # Generate embedding if embedder available and content exists
        embedding_blob = None
        if self.embedder and item.content:
            try:
                embedding = self.embedder.embed(item.content)
                item.embedding = embedding
                embedding_blob = self._pack_embedding(embedding)
            except Exception:
                # Continue without embedding on failure
                pass

        cursor.execute("""
            INSERT INTO vault_items (
                id, source, title, content, embedding, metadata,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.id,
            item.source,
            item.title,
            item.content,
            embedding_blob,
            json.dumps(item.metadata) if item.metadata else None,
            item.created_at or datetime.now(),
            item.updated_at or datetime.now()
        ))
        conn.commit()
        return item.id

    def get(self, item_id: str) -> Optional[VaultItem]:
        """Retrieve item by ID."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, source, title, content, embedding, metadata,
                   created_at, updated_at
            FROM vault_items WHERE id = ?
        """, (item_id,))

        row = cursor.fetchone()
        if not row:
            return None

        return self._row_to_item(row)

    def update(self, item_id: str, **kwargs) -> bool:
        """Update item fields."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        # Build update query dynamically
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ["title", "content", "source", "metadata"]:
                if key == "metadata":
                    value = json.dumps(value) if value else None
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return False

        fields.append("updated_at = ?")
        values.append(datetime.now())
        values.append(item_id)

        query = f"UPDATE vault_items SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        return cursor.rowcount > 0

    def delete(self, item_id: str) -> bool:
        """Delete item by ID."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM vault_items WHERE id = ?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0

    def list_by_source(
        self,
        source: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[VaultItem]:
        """List items by source."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, source, title, content, embedding, metadata,
                   created_at, updated_at
            FROM vault_items
            WHERE source = ?
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """, (source, limit, offset))

        return [self._row_to_item(row) for row in cursor.fetchall()]

    def _row_to_item(self, row) -> VaultItem:
        """Convert database row to VaultItem."""
        return VaultItem(
            id=row[0],
            source=row[1],
            title=row[2],
            content=row[3],
            embedding=self._unpack_embedding(row[4]) if row[4] else None,
            metadata=json.loads(row[5]) if row[5] else None,
            created_at=datetime.fromisoformat(row[6]) if row[6] else None,
            updated_at=datetime.fromisoformat(row[7]) if row[7] else None
        )

    def _pack_embedding(self, embedding: List[float]) -> bytes:
        """Pack embedding as binary blob."""
        return struct.pack(f'{len(embedding)}f', *embedding)

    def _unpack_embedding(self, blob: bytes) -> List[float]:
        """Unpack embedding from binary blob."""
        count = len(blob) // 4
        return list(struct.unpack(f'{count}f', blob))
