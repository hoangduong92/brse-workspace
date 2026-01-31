"""Vault saver for bk-capture - auto-save captured items to vault."""
import os
import sys
import hashlib
import threading
from typing import List
from dataclasses import dataclass

# Add lib path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../lib"))

try:
    from vault import VaultStore, VaultItem
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


@dataclass
class CapturedItem:
    """Captured item data."""
    content: str
    item_type: str
    source: str
    priority: str = "low"
    deadline: str = None
    metadata: dict = None


class VaultSaver:
    """Save captured items to vault asynchronously."""

    def __init__(self):
        """Initialize vault saver."""
        self.store = VaultStore() if VAULT_AVAILABLE else None

    def save(self, items: List[CapturedItem], source: str = "capture") -> dict:
        """Save items to vault (non-blocking).

        Args:
            items: List of CapturedItem
            source: Source identifier

        Returns:
            Save result dict
        """
        if not self.store:
            return {"saved": 0, "error": "Vault not available"}

        # Run async for non-blocking save
        thread = threading.Thread(
            target=self._save_items,
            args=(items, source),
            daemon=True
        )
        thread.start()

        return {"saved": len(items), "async": True}

    def _save_items(self, items: List[CapturedItem], source: str):
        """Internal method to save items."""
        for item in items:
            content_hash = hashlib.md5(item.content.encode()).hexdigest()[:12]
            item_id = f"{source}-{content_hash}"

            vault_item = VaultItem(
                id=item_id,
                source=source,
                title=item.content[:100],
                content=item.content,
                metadata={
                    "type": item.item_type,
                    "priority": item.priority,
                    "deadline": item.deadline,
                    **(item.metadata or {})
                }
            )

            try:
                self.store.add(vault_item)
            except Exception:
                # Skip duplicates
                pass

    def save_sync(self, items: List[CapturedItem], source: str = "capture") -> dict:
        """Save items synchronously (blocking).

        Args:
            items: List of CapturedItem
            source: Source identifier

        Returns:
            Save result dict
        """
        if not self.store:
            return {"saved": 0, "error": "Vault not available"}

        saved = 0
        for item in items:
            content_hash = hashlib.md5(item.content.encode()).hexdigest()[:12]
            item_id = f"{source}-{content_hash}"

            vault_item = VaultItem(
                id=item_id,
                source=source,
                title=item.content[:100],
                content=item.content,
                metadata={
                    "type": item.item_type,
                    "priority": item.priority,
                    "deadline": item.deadline,
                    **(item.metadata or {})
                }
            )

            try:
                self.store.add(vault_item)
                saved += 1
            except Exception:
                pass

        return {"saved": saved}
