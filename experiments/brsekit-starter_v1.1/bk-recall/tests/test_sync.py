"""Unit tests for bk-recall sync modules."""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime

# Setup paths for imports - paths are already set in conftest.py
test_dir = os.path.dirname(__file__)
scripts_dir = os.path.join(test_dir, "../scripts")
lib_dir = os.path.join(test_dir, "../../lib")
sys.path.insert(0, scripts_dir)
sys.path.insert(0, lib_dir)


class TestSyncManager:
    """Tests for SyncManager orchestration."""

    def test_get_syncer_email_creates_instance(self):
        """Test getting email syncer creates EmailSync instance."""
        from sync_manager import SyncManager
        from sources.email_sync import EmailSync
        manager = SyncManager()
        syncer = manager.get_syncer("email")
        assert isinstance(syncer, EmailSync)

    def test_get_syncer_backlog_creates_instance(self):
        """Test getting backlog syncer creates BacklogSync instance."""
        from sync_manager import SyncManager
        from sources.backlog_sync import BacklogSync
        manager = SyncManager()
        syncer = manager.get_syncer("backlog")
        assert isinstance(syncer, BacklogSync)

    def test_get_syncer_caches_instance(self):
        """Test syncer instances are cached."""
        from sync_manager import SyncManager
        manager = SyncManager()
        syncer1 = manager.get_syncer("email")
        syncer2 = manager.get_syncer("email")
        assert syncer1 is syncer2

    def test_get_syncer_unknown_source_raises_error(self):
        """Test requesting unknown source raises ValueError."""
        from sync_manager import SyncManager
        manager = SyncManager()
        with pytest.raises(ValueError, match="Unknown source"):
            manager.get_syncer("unknown_source")

    def test_sync_email_returns_result(self):
        """Test sync email returns syncer result."""
        from sync_manager import SyncManager
        mock_syncer = MagicMock()
        mock_syncer.sync.return_value = {"synced": 10, "source": "email"}

        manager = SyncManager()
        # Inject mock syncer
        manager._syncers["email"] = mock_syncer

        result = manager.sync("email", query="test", limit=50)

        assert result["synced"] == 10
        mock_syncer.sync.assert_called_once_with(
            query="test",
            limit=50
        )

    def test_sync_email_default_query(self):
        """Test sync email uses default query if not provided."""
        from sync_manager import SyncManager
        mock_syncer = MagicMock()
        mock_syncer.sync.return_value = {"synced": 5}

        manager = SyncManager()
        # Inject mock syncer
        manager._syncers["email"] = mock_syncer

        manager.sync("email")

        mock_syncer.sync.assert_called_once_with(
            query="is:inbox",
            limit=50
        )

    @patch("sync_manager.BacklogSync")
    def test_sync_backlog_requires_project_key(self, mock_backlog_class):
        """Test backlog sync fails without project_key."""
        from sync_manager import SyncManager
        manager = SyncManager()
        result = manager.sync("backlog")

        assert result["error"] == "project_key required for backlog sync"
        assert result["synced"] == 0

    def test_sync_backlog_with_project_key(self):
        """Test backlog sync with project key."""
        from sync_manager import SyncManager
        mock_syncer = MagicMock()
        mock_syncer.sync.return_value = {"synced": 20, "source": "backlog"}

        manager = SyncManager()
        # Inject mock syncer
        manager._syncers["backlog"] = mock_syncer

        result = manager.sync("backlog", project_key="PROJ")

        assert result["synced"] == 20
        mock_syncer.sync.assert_called_once_with(
            "PROJ",
            limit=100
        )

    @patch.dict(os.environ, {"BACKLOG_PROJECT_KEY": "ENV_PROJ"})
    def test_sync_backlog_from_env_var(self):
        """Test backlog sync reads project_key from environment."""
        from sync_manager import SyncManager
        mock_syncer = MagicMock()
        mock_syncer.sync.return_value = {"synced": 15}

        manager = SyncManager()
        # Inject mock syncer
        manager._syncers["backlog"] = mock_syncer

        result = manager.sync("backlog")

        assert result["synced"] == 15
        mock_syncer.sync.assert_called_once_with(
            "ENV_PROJ",
            limit=100
        )

    @patch.dict(os.environ, {"BACKLOG_PROJECT_KEY": "PROJ"})
    def test_sync_all_default_sources(self):
        """Test sync_all calls default sources."""
        from sync_manager import SyncManager
        mock_email_syncer = MagicMock()
        mock_email_syncer.sync.return_value = {"synced": 10}

        mock_backlog_syncer = MagicMock()
        mock_backlog_syncer.sync.return_value = {"synced": 5}

        manager = SyncManager()
        # Inject mock syncers
        manager._syncers["email"] = mock_email_syncer
        manager._syncers["backlog"] = mock_backlog_syncer

        result = manager.sync_all()

        assert result["total_synced"] == 15
        assert "email" in result["sources"]
        assert "backlog" in result["sources"]
        assert result["sources"]["email"]["synced"] == 10
        assert result["sources"]["backlog"]["synced"] == 5

    def test_sync_all_selective_sources(self):
        """Test sync_all with specific sources."""
        from sync_manager import SyncManager
        mock_syncer = MagicMock()
        mock_syncer.sync.return_value = {"synced": 8}

        manager = SyncManager()
        # Inject mock syncer
        manager._syncers["email"] = mock_syncer

        result = manager.sync_all(sources=["email"], query="custom")

        assert result["total_synced"] == 8
        assert "email" in result["sources"]
        assert "backlog" not in result["sources"]

    def test_sync_all_handles_exception(self):
        """Test sync_all captures exceptions from individual sources."""
        from sync_manager import SyncManager
        mock_syncer = MagicMock()
        mock_syncer.sync.side_effect = Exception("Connection failed")

        manager = SyncManager()
        # Inject mock syncer
        manager._syncers["email"] = mock_syncer

        result = manager.sync_all(sources=["email"])

        assert "Connection failed" in result["sources"]["email"]["error"]
        assert result["sources"]["email"]["synced"] == 0
        assert result["total_synced"] == 0


class TestEmailSync:
    """Tests for Gmail email sync."""

    def test_init_default_paths(self):
        """Test EmailSync uses default credential paths."""
        from sources.email_sync import EmailSync
        syncer = EmailSync()
        assert "gmail_credentials.json" in syncer.credentials_path
        assert "gmail_token.json" in syncer.token_path

    def test_init_custom_credentials_path(self):
        """Test EmailSync accepts custom credentials path."""
        from sources.email_sync import EmailSync
        custom_path = "/custom/path"
        syncer = EmailSync(credentials_path=custom_path)
        assert syncer.credentials_path == custom_path

    @patch("sources.email_sync.GMAIL_AVAILABLE", False)
    def test_sync_fails_without_gmail_api(self):
        """Test sync returns error if Gmail API not available."""
        from sources.email_sync import EmailSync
        syncer = EmailSync()
        result = syncer.sync()
        assert result["error"] == "Gmail API not available"
        assert result["synced"] == 0

    @patch("sources.email_sync.GMAIL_AVAILABLE", False)
    def test_get_service_raises_import_error(self):
        """Test _get_service raises ImportError if Gmail API missing."""
        from sources.email_sync import EmailSync
        syncer = EmailSync()
        with pytest.raises(ImportError, match="Gmail API not available"):
            syncer._get_service()

    @patch("sources.email_sync.build", create=True)
    @patch("sources.email_sync.os.path.exists")
    def test_get_service_with_valid_token(self, mock_exists, mock_build):
        """Test _get_service uses existing token."""
        from sources.email_sync import EmailSync
        mock_exists.return_value = True
        mock_creds = MagicMock()
        mock_creds.valid = True

        with patch("sources.email_sync.GMAIL_AVAILABLE", True):
            with patch("sources.email_sync.Credentials.from_authorized_user_file") as mock_creds_load:
                mock_creds_load.return_value = mock_creds
                mock_service = MagicMock()
                mock_build.return_value = mock_service

                syncer = EmailSync()
                service = syncer._get_service()

                assert service == mock_service
                mock_build.assert_called_once()

    @patch("sources.email_sync.build", create=True)
    @patch("sources.email_sync.os.path.exists")
    def test_get_service_missing_credentials(self, mock_exists, mock_build):
        """Test _get_service raises FileNotFoundError if credentials missing."""
        from sources.email_sync import EmailSync
        mock_exists.return_value = False

        with patch("sources.email_sync.GMAIL_AVAILABLE", True):
            syncer = EmailSync()
            with pytest.raises(FileNotFoundError, match="Gmail credentials not found"):
                syncer._get_service()

    @patch("sources.email_sync.build", create=True)
    @patch("sources.email_sync.SyncTracker")
    @patch("sources.email_sync.VaultStore")
    def test_sync_returns_count(self, mock_store_class, mock_tracker_class, mock_build):
        """Test sync returns synced count."""
        from sources.email_sync import EmailSync
        mock_store = MagicMock()
        mock_store_class.return_value = mock_store
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        mock_service = MagicMock()
        mock_messages_list = MagicMock()
        mock_messages_list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}, {"id": "msg2"}]
        }
        mock_messages_get = MagicMock()
        mock_messages_get.return_value.execute.return_value = {
            "id": "msg1",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test"},
                    {"name": "From", "value": "test@example.com"},
                    {"name": "Date", "value": "2026-01-30"}
                ],
                "body": {"data": ""}
            }
        }

        mock_service.users.return_value.messages.return_value.list = mock_messages_list
        mock_service.users.return_value.messages.return_value.get = mock_messages_get
        mock_build.return_value = mock_service

        # Mock credentials to prevent actual auth flow
        with patch("sources.email_sync.GMAIL_AVAILABLE", True):
            with patch("sources.email_sync.os.path.exists") as mock_exists:
                mock_exists.return_value = True
                with patch("sources.email_sync.Credentials.from_authorized_user_file") as mock_creds_load:
                    mock_creds = MagicMock()
                    mock_creds.valid = True
                    mock_creds_load.return_value = mock_creds

                    syncer = EmailSync()
                    result = syncer.sync(query="is:inbox", limit=50)

                    assert result["synced"] == 2
                    assert result["source"] == "email"

    @patch("sources.email_sync.SyncTracker")
    @patch("sources.email_sync.VaultStore")
    def test_sync_handles_store_errors(self, mock_store_class, mock_tracker_class):
        """Test sync continues on vault store errors."""
        from sources.email_sync import EmailSync
        mock_store = MagicMock()
        mock_store.add.side_effect = Exception("Duplicate")
        mock_store_class.return_value = mock_store
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        mock_service = MagicMock()
        mock_messages_list = MagicMock()
        mock_messages_list.return_value.execute.return_value = {
            "messages": [{"id": "msg1"}]
        }
        mock_messages_get = MagicMock()
        mock_messages_get.return_value.execute.return_value = {
            "id": "msg1",
            "payload": {
                "headers": [{"name": "Subject", "value": "Test"}],
                "body": {"data": ""}
            }
        }

        mock_service.users.return_value.messages.return_value.list = mock_messages_list
        mock_service.users.return_value.messages.return_value.get = mock_messages_get

        syncer = EmailSync()
        syncer.service = mock_service

        result = syncer.sync()

        assert result["synced"] == 0

    def test_message_to_vault_item_extracts_headers(self):
        """Test message conversion extracts email headers."""
        from sources.email_sync import EmailSync
        msg = {
            "id": "msg123",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "Date", "value": "2026-01-30"}
                ],
                "body": {"data": ""}
            }
        }

        syncer = EmailSync()
        item = syncer._message_to_vault_item(msg)

        assert item.source == "email"
        assert item.title == "Test Subject"
        assert item.id == "email-msg123"
        assert item.metadata["from"] == "sender@example.com"
        assert item.metadata["gmail_id"] == "msg123"

    def test_message_to_vault_item_handles_missing_headers(self):
        """Test message conversion handles missing headers."""
        from sources.email_sync import EmailSync
        msg = {
            "id": "msg123",
            "payload": {
                "headers": [],
                "body": {"data": ""}
            }
        }

        syncer = EmailSync()
        item = syncer._message_to_vault_item(msg)

        assert item.title == "(No Subject)"
        assert item.metadata["from"] == ""

    def test_extract_body_from_simple_payload(self):
        """Test body extraction from simple payload."""
        import base64
        from sources.email_sync import EmailSync
        body_text = "This is a test message"
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        payload = {
            "body": {"data": encoded_body}
        }

        syncer = EmailSync()
        body = syncer._extract_body(payload)

        assert body == body_text

    def test_extract_body_from_multipart_payload(self):
        """Test body extraction from multipart payload."""
        import base64
        from sources.email_sync import EmailSync
        body_text = "Plain text content"
        encoded_body = base64.urlsafe_b64encode(body_text.encode()).decode()

        payload = {
            "parts": [
                {
                    "mimeType": "text/html",
                    "body": {"data": ""}
                },
                {
                    "mimeType": "text/plain",
                    "body": {"data": encoded_body}
                }
            ]
        }

        syncer = EmailSync()
        body = syncer._extract_body(payload)

        assert body == body_text

    def test_extract_body_empty_payload(self):
        """Test body extraction returns empty for empty payload."""
        from sources.email_sync import EmailSync
        payload = {"parts": []}
        syncer = EmailSync()
        body = syncer._extract_body(payload)
        assert body == ""


class TestSlackSync:
    """Tests for Slack message sync."""

    def test_init_from_token_parameter(self):
        """Test SlackSync initialization with token parameter."""
        from sources.slack_sync import SlackSync
        syncer = SlackSync(token="xoxb-test-token")
        assert syncer.token == "xoxb-test-token"

    def test_init_from_env_variable(self):
        """Test SlackSync reads token from environment."""
        from sources.slack_sync import SlackSync
        with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-env-token"}):
            syncer = SlackSync()
            assert syncer.token == "xoxb-env-token"

    @patch("sources.slack_sync.VaultStore")
    @patch("sources.slack_sync.SyncTracker")
    def test_init_no_token(self, mock_tracker, mock_store):
        """Test SlackSync with no token."""
        from sources.slack_sync import SlackSync
        with patch.dict(os.environ, {}, clear=True):
            syncer = SlackSync()
            assert syncer.token == ""

    @patch("sources.slack_sync.SLACK_AVAILABLE", False)
    def test_sync_fails_without_sdk(self):
        """Test sync returns error if Slack SDK not available."""
        from sources.slack_sync import SlackSync
        syncer = SlackSync(token="test")
        result = syncer.sync()
        assert result["error"] == "Slack SDK not available"
        assert result["synced"] == 0

    @patch("sources.slack_sync.SLACK_AVAILABLE", True)
    def test_sync_fails_without_token(self):
        """Test sync returns error without token."""
        from sources.slack_sync import SlackSync
        syncer = SlackSync()
        result = syncer.sync()
        assert result["error"] == "SLACK_BOT_TOKEN not set"
        assert result["synced"] == 0

    @patch("sources.slack_sync.SLACK_AVAILABLE", False)
    def test_get_client_raises_import_error(self):
        """Test _get_client raises ImportError if SDK unavailable."""
        from sources.slack_sync import SlackSync
        syncer = SlackSync(token="test")
        with pytest.raises(ImportError, match="Slack SDK not available"):
            syncer._get_client()

    @patch("sources.slack_sync.SLACK_AVAILABLE", True)
    def test_get_client_raises_without_token(self):
        """Test _get_client raises ValueError without token."""
        from sources.slack_sync import SlackSync
        syncer = SlackSync()
        with pytest.raises(ValueError, match="Slack Bot Token required"):
            syncer._get_client()

    @patch("sources.slack_sync.WebClient", create=True)
    @patch("sources.slack_sync.SLACK_AVAILABLE", True)
    @patch("sources.slack_sync.SyncTracker")
    @patch("sources.slack_sync.VaultStore")
    def test_sync_specific_channel(self, mock_store_class, mock_tracker_class, mock_webclient):
        """Test syncing specific channel."""
        from sources.slack_sync import SlackSync
        mock_store = MagicMock()
        mock_store_class.return_value = mock_store
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        mock_client = MagicMock()
        mock_webclient.return_value = mock_client

        mock_client.conversations_info.return_value = {
            "channel": {"name": "general", "id": "C123"}
        }
        mock_client.conversations_history.return_value = {
            "messages": [
                {"type": "message", "ts": "1234567890.123456", "user": "U123", "text": "Hello"}
            ]
        }

        syncer = SlackSync(token="xoxb-test")
        result = syncer.sync(channel_id="C123", limit=50)

        assert result["synced"] == 1
        assert result["source"] == "slack"
        assert result["channels"] == 1

    def test_message_to_vault_item_converts_timestamp(self):
        """Test message conversion with timestamp."""
        from sources.slack_sync import SlackSync
        msg = {
            "type": "message",
            "ts": "1234567890.123456",
            "user": "U123",
            "text": "Hello world"
        }

        syncer = SlackSync(token="test")
        item = syncer._message_to_vault_item(msg, "general", "C123")

        assert item.source == "slack"
        assert item.id == "slack-C123-1234567890.123456"
        assert "[#general]" in item.title
        assert item.metadata["channel_id"] == "C123"
        assert item.metadata["user"] == "U123"

    def test_message_to_vault_item_truncates_long_text(self):
        """Test message title truncates long text."""
        from sources.slack_sync import SlackSync
        long_text = "a" * 100
        msg = {
            "ts": "123",
            "user": "U123",
            "text": long_text
        }

        syncer = SlackSync(token="test")
        item = syncer._message_to_vault_item(msg, "general", "C123")

        assert "..." in item.title
        assert len(item.title) < len(long_text)


class TestBacklogSync:
    """Tests for Backlog issue sync."""

    def test_init_from_parameters(self):
        """Test BacklogSync initialization with parameters."""
        from sources.backlog_sync import BacklogSync
        syncer = BacklogSync(space_url="https://test.backlog.jp", api_key="test-key")
        assert syncer.space_url == "https://test.backlog.jp"
        assert syncer.api_key == "test-key"

    def test_init_from_env_variables(self):
        """Test BacklogSync reads from environment."""
        from sources.backlog_sync import BacklogSync
        with patch.dict(os.environ, {
            "BACKLOG_SPACE_URL": "https://env.backlog.jp",
            "BACKLOG_API_KEY": "env-key"
        }):
            syncer = BacklogSync()
            assert syncer.space_url == "https://env.backlog.jp"
            assert syncer.api_key == "env-key"

    def test_sync_fails_without_credentials(self):
        """Test sync fails without space_url or api_key."""
        from sources.backlog_sync import BacklogSync
        syncer = BacklogSync()
        result = syncer.sync("PROJ")
        assert "BACKLOG_SPACE_URL or BACKLOG_API_KEY not set" in result["error"]

    def test_issue_to_vault_item(self):
        """Test issue conversion to vault item."""
        from sources.backlog_sync import BacklogSync
        issue = {
            "id": 123,
            "summary": "Fix bug",
            "description": "Bug details",
            "issueKey": "PROJ-123",
            "status": {"name": "In Progress"},
            "assignee": {"name": "Alice"}
        }

        syncer = BacklogSync(space_url="https://test.backlog.jp", api_key="key")
        item = syncer._issue_to_vault_item(issue, "PROJ")

        assert item.source == "backlog"
        assert item.title == "Fix bug"
        assert item.id == "backlog-issue-123"
        assert item.metadata["project_key"] == "PROJ"
        assert item.metadata["issue_key"] == "PROJ-123"
        assert item.metadata["type"] == "issue"

    def test_comment_to_vault_item(self):
        """Test comment conversion to vault item."""
        from sources.backlog_sync import BacklogSync
        comment = {
            "id": 456,
            "content": "Comment text"
        }
        issue = {
            "id": 123,
            "issueKey": "PROJ-123"
        }

        syncer = BacklogSync(space_url="https://test.backlog.jp", api_key="key")
        item = syncer._comment_to_vault_item(comment, issue, "PROJ")

        assert item.source == "backlog"
        assert item.id == "backlog-comment-456"
        assert item.metadata["issue_key"] == "PROJ-123"
        assert item.metadata["type"] == "comment"
        assert "PROJ-123" in item.title
