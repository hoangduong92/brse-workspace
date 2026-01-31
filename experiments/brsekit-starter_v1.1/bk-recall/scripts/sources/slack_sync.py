"""Slack source sync for bk-recall.

Syncs Slack messages and threads to vault for context memory.
Requires Slack Bot Token with channels:history, channels:read scopes.
"""
import os
import sys
from datetime import datetime
from typing import List, Optional
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../lib"))

from vault import VaultStore, VaultItem, SyncTracker

# Slack SDK import
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False


class SlackSync:
    """Sync Slack messages to vault."""

    def __init__(self, token: str = None):
        """Initialize Slack sync.

        Args:
            token: Slack Bot Token. If not provided, reads from SLACK_BOT_TOKEN env.
        """
        self.token = token or os.environ.get("SLACK_BOT_TOKEN", "")
        self.store = VaultStore()
        self.tracker = SyncTracker()
        self.client = None

    def _get_client(self) -> "WebClient":
        """Get authenticated Slack client."""
        if not SLACK_AVAILABLE:
            raise ImportError(
                "Slack SDK not available. Install with: pip install slack_sdk"
            )

        if not self.token:
            raise ValueError(
                "Slack Bot Token required. Set SLACK_BOT_TOKEN env or pass to constructor."
            )

        return WebClient(token=self.token)

    def sync(self, channel_id: str = None, limit: int = 50) -> dict:
        """Sync messages from Slack channel.

        Args:
            channel_id: Slack channel ID. If None, syncs all joined channels.
            limit: Max messages per channel to sync.

        Returns:
            Sync result with counts.
        """
        if not SLACK_AVAILABLE:
            return {"error": "Slack SDK not available", "synced": 0}

        if not self.token:
            return {"error": "SLACK_BOT_TOKEN not set", "synced": 0}

        try:
            self.client = self._get_client()
        except Exception as e:
            return {"error": str(e), "synced": 0}

        synced = 0
        channels = []

        # Get channels to sync
        if channel_id:
            channels = [channel_id]
        else:
            # List joined channels
            try:
                result = self.client.conversations_list(types="public_channel,private_channel")
                channels = [ch["id"] for ch in result.get("channels", [])]
            except SlackApiError as e:
                return {"error": f"Failed to list channels: {e.response['error']}", "synced": 0}

        # Sync each channel
        for ch_id in channels:
            synced += self._sync_channel(ch_id, limit)

        self.tracker.update_sync("slack", datetime.now())
        return {"synced": synced, "source": "slack", "channels": len(channels)}

    def _sync_channel(self, channel_id: str, limit: int) -> int:
        """Sync messages from single channel.

        Args:
            channel_id: Channel to sync
            limit: Max messages

        Returns:
            Number of messages synced
        """
        synced = 0

        try:
            # Get channel info
            ch_info = self.client.conversations_info(channel=channel_id)
            channel_name = ch_info.get("channel", {}).get("name", channel_id)

            # Get messages
            result = self.client.conversations_history(
                channel=channel_id,
                limit=limit
            )

            for msg in result.get("messages", []):
                if msg.get("type") != "message":
                    continue

                item = self._message_to_vault_item(msg, channel_name, channel_id)
                try:
                    self.store.add(item)
                    synced += 1
                except Exception:
                    pass  # Skip duplicates

        except SlackApiError as e:
            # Log error but continue with other channels
            print(f"Error syncing channel {channel_id}: {e.response['error']}")

        return synced

    def _message_to_vault_item(self, msg: dict, channel_name: str, channel_id: str) -> VaultItem:
        """Convert Slack message to VaultItem.

        Args:
            msg: Slack message object
            channel_name: Channel name
            channel_id: Channel ID

        Returns:
            VaultItem for storage
        """
        ts = msg.get("ts", "")
        user = msg.get("user", "unknown")
        text = msg.get("text", "")

        # Convert timestamp to datetime
        date_str = ""
        if ts:
            try:
                dt = datetime.fromtimestamp(float(ts))
                date_str = dt.isoformat()
            except (ValueError, OSError):
                date_str = ts

        return VaultItem(
            id=f"slack-{channel_id}-{ts}",
            source="slack",
            title=f"[#{channel_name}] {text[:50]}..." if len(text) > 50 else f"[#{channel_name}] {text}",
            content=text,
            metadata={
                "channel_id": channel_id,
                "channel_name": channel_name,
                "user": user,
                "timestamp": ts,
                "date": date_str,
                "thread_ts": msg.get("thread_ts")
            }
        )

    def sync_thread(self, channel_id: str, thread_ts: str) -> dict:
        """Sync all messages in a thread.

        Args:
            channel_id: Channel containing thread
            thread_ts: Thread timestamp

        Returns:
            Sync result
        """
        if not SLACK_AVAILABLE:
            return {"error": "Slack SDK not available", "synced": 0}

        try:
            self.client = self._get_client()
            result = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )

            synced = 0
            ch_info = self.client.conversations_info(channel=channel_id)
            channel_name = ch_info.get("channel", {}).get("name", channel_id)

            for msg in result.get("messages", []):
                item = self._message_to_vault_item(msg, channel_name, channel_id)
                try:
                    self.store.add(item)
                    synced += 1
                except Exception:
                    pass

            return {"synced": synced, "source": "slack", "thread": thread_ts}

        except SlackApiError as e:
            return {"error": f"Failed to sync thread: {e.response['error']}", "synced": 0}
