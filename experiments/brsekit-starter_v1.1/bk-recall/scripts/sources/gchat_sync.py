"""Google Chat source sync for bk-recall.

Syncs Google Chat messages to vault for context memory.
Requires Google Workspace API with Chat API enabled.

Note: Google Chat API requires a Google Workspace account.
For personal accounts, this sync will not be available.
"""
import os
import sys
from datetime import datetime
from typing import List, Optional
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../lib"))

from vault import VaultStore, VaultItem, SyncTracker

# Google Chat API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GCHAT_AVAILABLE = True
except ImportError:
    GCHAT_AVAILABLE = False

SCOPES = [
    "https://www.googleapis.com/auth/chat.spaces.readonly",
    "https://www.googleapis.com/auth/chat.messages.readonly"
]


class GChatSync:
    """Sync Google Chat messages to vault.

    Note: Requires Google Workspace account with Chat API enabled.
    Personal Gmail accounts do not have access to Chat API.
    """

    def __init__(self, credentials_path: str = None):
        """Initialize Google Chat sync.

        Args:
            credentials_path: Path to OAuth credentials JSON.
        """
        self.credentials_path = credentials_path or str(
            Path.home() / ".brsekit" / "gchat_credentials.json"
        )
        self.token_path = str(Path.home() / ".brsekit" / "gchat_token.json")
        self.store = VaultStore()
        self.tracker = SyncTracker()
        self.service = None

    def _get_service(self):
        """Get authenticated Google Chat service."""
        if not GCHAT_AVAILABLE:
            raise ImportError(
                "Google API not available. Install google-api-python-client"
            )

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Google Chat credentials not found: {self.credentials_path}"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            Path(self.token_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as f:
                f.write(creds.to_json())

        return build("chat", "v1", credentials=creds)

    def sync(self, space_name: str = None, limit: int = 50) -> dict:
        """Sync messages from Google Chat space.

        Args:
            space_name: Chat space name (e.g., "spaces/XXXXXX").
                       If None, syncs all accessible spaces.
            limit: Max messages per space to sync.

        Returns:
            Sync result with counts.
        """
        if not GCHAT_AVAILABLE:
            return {"error": "Google API not available", "synced": 0}

        try:
            self.service = self._get_service()
        except FileNotFoundError as e:
            return {"error": str(e), "synced": 0}
        except Exception as e:
            return {"error": f"Authentication failed: {e}", "synced": 0}

        synced = 0
        spaces = []

        # Get spaces to sync
        if space_name:
            spaces = [{"name": space_name, "displayName": space_name}]
        else:
            try:
                result = self.service.spaces().list().execute()
                spaces = result.get("spaces", [])
            except Exception as e:
                return {"error": f"Failed to list spaces: {e}", "synced": 0}

        # Sync each space
        for space in spaces:
            synced += self._sync_space(space, limit)

        self.tracker.update_sync("gchat", datetime.now())
        return {"synced": synced, "source": "gchat", "spaces": len(spaces)}

    def _sync_space(self, space: dict, limit: int) -> int:
        """Sync messages from single space.

        Args:
            space: Space info dict
            limit: Max messages

        Returns:
            Number of messages synced
        """
        synced = 0
        space_name = space.get("name", "")
        display_name = space.get("displayName", space_name)

        try:
            result = self.service.spaces().messages().list(
                parent=space_name,
                pageSize=min(limit, 100)  # API max is 100
            ).execute()

            for msg in result.get("messages", []):
                item = self._message_to_vault_item(msg, display_name)
                try:
                    self.store.add(item)
                    synced += 1
                except Exception:
                    pass  # Skip duplicates

        except Exception as e:
            print(f"Error syncing space {space_name}: {e}")

        return synced

    def _message_to_vault_item(self, msg: dict, space_name: str) -> VaultItem:
        """Convert Google Chat message to VaultItem.

        Args:
            msg: Chat message object
            space_name: Space display name

        Returns:
            VaultItem for storage
        """
        msg_name = msg.get("name", "")
        text = msg.get("text", "")
        sender = msg.get("sender", {}).get("displayName", "unknown")
        create_time = msg.get("createTime", "")

        return VaultItem(
            id=f"gchat-{msg_name.replace('/', '-')}",
            source="gchat",
            title=f"[{space_name}] {text[:50]}..." if len(text) > 50 else f"[{space_name}] {text}",
            content=text,
            metadata={
                "space_name": space_name,
                "message_name": msg_name,
                "sender": sender,
                "date": create_time,
                "thread_name": msg.get("thread", {}).get("name")
            }
        )
