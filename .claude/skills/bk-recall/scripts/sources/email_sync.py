"""Email source sync for bk-recall using Gmail API OAuth."""
import os
import sys
import base64
import hashlib
from datetime import datetime
from typing import List, Optional
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../lib"))

from vault import VaultStore, VaultItem, SyncTracker

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class EmailSync:
    """Sync Gmail messages to vault using OAuth."""

    def __init__(self, credentials_path: str = None):
        """Initialize Gmail sync."""
        self.credentials_path = credentials_path or str(
            Path.home() / ".brsekit" / "gmail_credentials.json"
        )
        self.token_path = str(Path.home() / ".brsekit" / "gmail_token.json")
        self.store = VaultStore()
        self.tracker = SyncTracker()
        self.service = None

    def _get_service(self):
        """Get authenticated Gmail service."""
        if not GMAIL_AVAILABLE:
            raise ImportError("Gmail API not available. Install google-api-python-client")

        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Gmail credentials not found: {self.credentials_path}"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            Path(self.token_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as f:
                f.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    def sync(self, query: str = "is:inbox", limit: int = 50) -> dict:
        """Sync emails matching query.

        Args:
            query: Gmail search query
            limit: Max emails to sync

        Returns:
            Sync result with counts
        """
        if not GMAIL_AVAILABLE:
            return {"error": "Gmail API not available", "synced": 0}

        try:
            self.service = self._get_service()
        except Exception as e:
            return {"error": str(e), "synced": 0}

        # Get messages
        results = self.service.users().messages().list(
            userId="me",
            q=query,
            maxResults=limit
        ).execute()

        messages = results.get("messages", [])
        synced = 0

        for msg_ref in messages:
            msg = self.service.users().messages().get(
                userId="me",
                id=msg_ref["id"],
                format="full"
            ).execute()

            item = self._message_to_vault_item(msg)
            try:
                self.store.add(item)
                synced += 1
            except Exception:
                pass

        self.tracker.update_sync("email", datetime.now())
        return {"synced": synced, "source": "email"}

    def _message_to_vault_item(self, msg: dict) -> VaultItem:
        """Convert Gmail message to VaultItem."""
        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        subject = headers.get("Subject", "(No Subject)")
        sender = headers.get("From", "")
        date_str = headers.get("Date", "")

        # Extract body
        body = self._extract_body(msg["payload"])

        return VaultItem(
            id=f"email-{msg['id']}",
            source="email",
            title=subject,
            content=f"From: {sender}\nSubject: {subject}\n\n{body}",
            metadata={
                "from": sender,
                "subject": subject,
                "date": date_str,
                "gmail_id": msg["id"]
            }
        )

    def _extract_body(self, payload: dict) -> str:
        """Extract text body from message payload."""
        if "body" in payload and payload["body"].get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")

        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    if part["body"].get("data"):
                        return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")

        return ""
