"""Backlog source sync for bk-recall."""
import os
import sys
from datetime import datetime, date
from typing import Dict, List, Optional

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../common"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../lib"))

try:
    from backlog.client import BacklogClient
except ImportError:
    BacklogClient = None

from vault import VaultStore, VaultItem, SyncTracker, TimeLogStore, TimeLogEntry
# v2 imports for project-aware sync
from vault import MemoryStore, MemoryEntry, SyncStateManager, SyncScheduler


class BacklogSync:
    """Sync Backlog issues, comments, and time logs to vault."""

    def __init__(self, space_url: str = None, api_key: str = None):
        """Initialize Backlog sync."""
        self.space_url = space_url or os.getenv("BACKLOG_SPACE_URL")
        self.api_key = api_key or os.getenv("BACKLOG_API_KEY")
        self.store = VaultStore()
        self.tracker = SyncTracker()
        self.time_log_store = TimeLogStore()

    def sync(self, project_key: str, limit: int = 100, sync_time_logs: bool = True) -> dict:
        """Sync recent issues and comments from project.

        Args:
            project_key: Backlog project key
            limit: Max items to sync

        Returns:
            Sync result with counts
        """
        if not BacklogClient:
            return {"error": "BacklogClient not available", "synced": 0}

        if not self.space_url or not self.api_key:
            return {"error": "BACKLOG_SPACE_URL or BACKLOG_API_KEY not set", "synced": 0}

        client = BacklogClient(self.space_url, self.api_key)
        last_sync = self.tracker.get_last_sync("backlog")

        # Fetch recent issues
        issues = client.get_issues(
            project_key,
            count=limit,
            updated_since=last_sync
        )

        synced = 0
        for issue in issues:
            # Create vault item from issue
            item = self._issue_to_vault_item(issue, project_key)
            try:
                self.store.add(item)
                synced += 1
            except Exception:
                # Skip duplicates
                pass

            # Sync comments
            comments = client.get_issue_comments(issue["id"])
            for comment in comments:
                comment_item = self._comment_to_vault_item(comment, issue, project_key)
                try:
                    self.store.add(comment_item)
                    synced += 1
                except Exception:
                    pass

        # Sync time logs from activities
        time_logs_synced = 0
        if sync_time_logs:
            time_logs_synced = self._sync_time_logs(client, project_key)

        # Update sync tracker
        self.tracker.update_sync("backlog", datetime.now())

        return {
            "synced": synced,
            "time_logs_synced": time_logs_synced,
            "source": "backlog"
        }

    def sync_time_logs_only(self, project_key: str, limit: int = 500) -> dict:
        """Sync only time logs (actualHours changes) from project activities.

        Args:
            project_key: Backlog project key
            limit: Max activities to scan

        Returns:
            Sync result with time_logs_synced count
        """
        if not BacklogClient:
            return {"error": "BacklogClient not available", "time_logs_synced": 0}

        if not self.space_url or not self.api_key:
            return {"error": "BACKLOG_SPACE_URL or BACKLOG_API_KEY not set", "time_logs_synced": 0}

        client = BacklogClient(self.space_url, self.api_key)
        time_logs_synced = self._sync_time_logs(client, project_key, limit)

        return {"time_logs_synced": time_logs_synced, "source": "backlog"}

    def _sync_time_logs(self, client: "BacklogClient", project_key: str, limit: int = 500) -> int:
        """Sync actualHours changes from project activities to time_logs table.

        Args:
            client: BacklogClient instance
            project_key: Backlog project key
            limit: Max activities to scan

        Returns:
            Number of time log entries synced
        """
        # Get last synced activity ID for time logs
        last_activity_id = self.tracker.get_last_item_id("backlog_time_logs")

        # Fetch activities (type 2 = issue updated)
        activities = client.get_all_project_activities(
            project_key,
            activity_type_ids=[2],  # Issue updated
            since_id=int(last_activity_id) if last_activity_id else None,
            limit=limit
        )

        synced = 0
        max_activity_id = int(last_activity_id) if last_activity_id else 0

        for activity in activities:
            entries = self._parse_time_log_from_activity(activity, project_key)
            for entry in entries:
                if self.time_log_store.add(entry):
                    synced += 1

            # Track max activity ID
            if activity["id"] > max_activity_id:
                max_activity_id = activity["id"]

        # Update tracker with latest activity ID
        if max_activity_id > 0:
            self.tracker.update_sync(
                "backlog_time_logs",
                datetime.now(),
                last_item_id=str(max_activity_id)
            )

        return synced

    def _parse_time_log_from_activity(
        self, activity: dict, project_key: str
    ) -> List[TimeLogEntry]:
        """Parse actualHours changes from a Backlog activity.

        Args:
            activity: Backlog activity dict
            project_key: Backlog project key

        Returns:
            List of TimeLogEntry (usually 0 or 1)
        """
        entries = []

        content = activity.get("content", {})
        changes = content.get("changes", [])

        for change in changes:
            field = change.get("field", "")
            if field != "actualHours":
                continue

            # Parse old and new values
            old_val = float(change.get("old_value") or 0)
            new_val = float(change.get("new_value") or 0)
            delta = new_val - old_val

            if delta == 0:
                continue

            # Get activity metadata
            created_user = activity.get("createdUser", {})
            created_at = activity.get("created", "")

            # Parse date from created timestamp
            try:
                if "T" in created_at:
                    log_date = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    ).date()
                else:
                    log_date = date.fromisoformat(created_at[:10])
            except (ValueError, TypeError):
                log_date = date.today()

            # Create entry ID from activity ID and field
            entry_id = f"backlog-timelog-{activity['id']}-actualHours"

            entry = TimeLogEntry(
                id=entry_id,
                project_key=project_key,
                issue_key=content.get("key_id") or f"{project_key}-?",
                member_id=created_user.get("id"),
                member_name=created_user.get("name", "Unknown"),
                hours_delta=delta,
                total_after=new_val,
                logged_at=log_date,
                activity_id=activity["id"]
            )
            entries.append(entry)

        return entries

    def _issue_to_vault_item(self, issue: dict, project_key: str) -> VaultItem:
        """Convert Backlog issue to VaultItem."""
        content = f"{issue.get('summary', '')}\n\n{issue.get('description', '')}"
        item_id = f"backlog-issue-{issue['id']}"

        return VaultItem(
            id=item_id,
            source="backlog",
            title=issue.get("summary", ""),
            content=content,
            metadata={
                "project_key": project_key,
                "issue_key": issue.get("issueKey"),
                "status": issue.get("status", {}).get("name"),
                "assignee": issue.get("assignee", {}).get("name") if issue.get("assignee") else None,
                "type": "issue"
            }
        )

    def _comment_to_vault_item(self, comment: dict, issue: dict, project_key: str) -> VaultItem:
        """Convert Backlog comment to VaultItem."""
        item_id = f"backlog-comment-{comment['id']}"

        return VaultItem(
            id=item_id,
            source="backlog",
            title=f"Comment on {issue.get('issueKey', '')}",
            content=comment.get("content", ""),
            metadata={
                "project_key": project_key,
                "issue_key": issue.get("issueKey"),
                "author": comment.get("createdUser", {}).get("name"),
                "type": "comment"
            }
        )

    # ===== v2 Project-aware sync methods =====

    def sync_to_memory(
        self,
        project_key: str,
        limit: int = 100,
        sync_comments: bool = True,
    ) -> Dict:
        """Sync Backlog issues and comments to MemoryStore (v2).

        Args:
            project_key: Backlog project key (also used as brsekit project key)
            limit: Max issues to sync
            sync_comments: Whether to sync comments (default: True)

        Returns:
            Sync result with counts
        """
        if not BacklogClient:
            return {"error": "BacklogClient not available", "synced": 0}

        if not self.space_url or not self.api_key:
            return {"error": "BACKLOG_SPACE_URL or BACKLOG_API_KEY not set", "synced": 0}

        client = BacklogClient(self.space_url, self.api_key)
        memory_store = MemoryStore(project_key)
        sync_state = SyncStateManager(project_key)
        scheduler = SyncScheduler(project_key)

        # Get last sync time
        last_sync = sync_state.get_last_sync("backlog")

        # Fetch recent issues
        issues = client.get_issues(
            project_key,
            count=limit,
            updated_since=last_sync
        )

        synced_issues = 0
        synced_comments = 0
        entries = []

        for issue in issues:
            # Convert issue to MemoryEntry
            entry = self._issue_to_memory_entry(issue, project_key)
            entries.append(entry)
            synced_issues += 1

            # Sync comments if enabled
            if sync_comments:
                comments = client.get_issue_comments(issue["id"])
                for comment in comments:
                    comment_entry = self._comment_to_memory_entry(
                        comment, issue, project_key
                    )
                    entries.append(comment_entry)
                    synced_comments += 1

        # Batch append to memory store
        if entries:
            memory_store.append_batch("backlog", entries)

        # Update sync state
        scheduler.record_sync_complete(
            "backlog",
            items_synced=len(entries),
            last_item_id=str(issues[-1]["id"]) if issues else None
        )

        return {
            "synced": len(entries),
            "issues": synced_issues,
            "comments": synced_comments,
            "source": "backlog",
            "project_key": project_key,
        }

    def sync_comments_only(
        self,
        project_key: str,
        issue_keys: Optional[List[str]] = None,
        limit: int = 50,
    ) -> Dict:
        """Sync only comments for specific issues to MemoryStore.

        Args:
            project_key: Backlog project key
            issue_keys: Optional list of issue keys to sync (if None, sync recent)
            limit: Max comments per issue

        Returns:
            Sync result with counts
        """
        if not BacklogClient:
            return {"error": "BacklogClient not available", "synced": 0}

        if not self.space_url or not self.api_key:
            return {"error": "BACKLOG_SPACE_URL or BACKLOG_API_KEY not set", "synced": 0}

        client = BacklogClient(self.space_url, self.api_key)
        memory_store = MemoryStore(project_key)
        sync_state = SyncStateManager(project_key)

        entries = []

        if issue_keys:
            # Sync specific issues
            for issue_key in issue_keys:
                try:
                    issue = client.get_issue(issue_key)
                    comments = client.get_issue_comments(issue["id"], count=limit)
                    for comment in comments:
                        entry = self._comment_to_memory_entry(
                            comment, issue, project_key
                        )
                        entries.append(entry)
                except Exception:
                    continue
        else:
            # Sync comments from recent activities
            last_activity_id = sync_state.get_last_item_id("backlog_comments")
            activities = client.get_all_project_activities(
                project_key,
                activity_type_ids=[3],  # Issue commented
                since_id=int(last_activity_id) if last_activity_id else None,
                limit=limit * 2
            )

            for activity in activities:
                content = activity.get("content", {})
                issue_key = content.get("key_id")
                if issue_key:
                    try:
                        issue = client.get_issue(issue_key)
                        comment_id = content.get("id")
                        if comment_id:
                            comments = client.get_issue_comments(
                                issue["id"], count=1
                            )
                            for comment in comments:
                                if comment["id"] == comment_id:
                                    entry = self._comment_to_memory_entry(
                                        comment, issue, project_key
                                    )
                                    entries.append(entry)
                    except Exception:
                        continue

        # Batch append
        if entries:
            memory_store.append_batch("backlog", entries)
            sync_state.update_sync("backlog_comments", datetime.now())

        return {
            "synced": len(entries),
            "source": "backlog_comments",
            "project_key": project_key,
        }

    def _issue_to_memory_entry(self, issue: dict, project_key: str) -> MemoryEntry:
        """Convert Backlog issue to MemoryEntry."""
        content = f"{issue.get('summary', '')}\n\n{issue.get('description', '')}"
        item_id = f"backlog-issue-{issue['id']}"

        # Parse created/updated timestamp
        updated = issue.get("updated") or issue.get("created")
        if updated:
            try:
                timestamp = datetime.fromisoformat(
                    updated.replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        return MemoryEntry(
            id=item_id,
            source="backlog",
            timestamp=timestamp,
            content=content,
            metadata={
                "project_key": project_key,
                "issue_key": issue.get("issueKey"),
                "status": issue.get("status", {}).get("name"),
                "assignee": issue.get("assignee", {}).get("name") if issue.get("assignee") else None,
                "type": "issue",
            }
        )

    def _comment_to_memory_entry(
        self, comment: dict, issue: dict, project_key: str
    ) -> MemoryEntry:
        """Convert Backlog comment to MemoryEntry."""
        item_id = f"backlog-comment-{comment['id']}"

        # Parse created timestamp
        created = comment.get("created")
        if created:
            try:
                timestamp = datetime.fromisoformat(
                    created.replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        return MemoryEntry(
            id=item_id,
            source="backlog",
            timestamp=timestamp,
            content=comment.get("content", ""),
            metadata={
                "project_key": project_key,
                "issue_key": issue.get("issueKey"),
                "author": comment.get("createdUser", {}).get("name"),
                "type": "comment",
            }
        )
