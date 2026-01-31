"""Time log store for tracking actualHours changes."""
from datetime import date, datetime
from typing import List, Optional, Dict
from dataclasses import dataclass

from .db import VaultDB


@dataclass
class TimeLogEntry:
    """Represents a single time log entry."""
    id: str
    project_key: str
    issue_key: str
    member_id: Optional[int]
    member_name: str
    hours_delta: float
    total_after: float
    logged_at: date
    activity_id: Optional[int] = None
    synced_at: Optional[datetime] = None


class TimeLogStore:
    """Store and query time log entries."""

    def __init__(self):
        """Initialize time log store."""
        VaultDB.initialize()

    def add(self, entry: TimeLogEntry) -> bool:
        """Add a time log entry.

        Returns True if added, False if duplicate.
        """
        conn = VaultDB.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO time_logs
                (id, project_key, issue_key, member_id, member_name,
                 hours_delta, total_after, logged_at, activity_id, synced_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                entry.id,
                entry.project_key,
                entry.issue_key,
                entry.member_id,
                entry.member_name,
                entry.hours_delta,
                entry.total_after,
                entry.logged_at.isoformat() if isinstance(entry.logged_at, date) else entry.logged_at,
                entry.activity_id
            ))
            conn.commit()
            return True
        except Exception:
            return False

    def add_batch(self, entries: List[TimeLogEntry]) -> int:
        """Add multiple entries. Returns count added."""
        added = 0
        for entry in entries:
            if self.add(entry):
                added += 1
        return added

    def get_by_project(
        self,
        project_key: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TimeLogEntry]:
        """Get time logs for a project within date range."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM time_logs WHERE project_key = ?"
        params = [project_key]

        if start_date:
            query += " AND logged_at >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND logged_at <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY logged_at ASC, issue_key ASC"
        cursor.execute(query, params)

        return [self._row_to_entry(row) for row in cursor.fetchall()]

    def get_by_member(
        self,
        member_name: str,
        project_key: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[TimeLogEntry]:
        """Get time logs for a specific member."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM time_logs WHERE member_name = ?"
        params = [member_name]

        if project_key:
            query += " AND project_key = ?"
            params.append(project_key)
        if start_date:
            query += " AND logged_at >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND logged_at <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY logged_at ASC"
        cursor.execute(query, params)

        return [self._row_to_entry(row) for row in cursor.fetchall()]

    def get_daily_summary(
        self,
        project_key: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Dict[date, float]]:
        """Get daily hours summary per member.

        Returns: {member_name: {date: total_hours_logged}}
        """
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT member_name, logged_at, SUM(hours_delta) as daily_hours
            FROM time_logs
            WHERE project_key = ?
              AND logged_at >= ?
              AND logged_at <= ?
            GROUP BY member_name, logged_at
            ORDER BY member_name, logged_at
        """, (project_key, start_date.isoformat(), end_date.isoformat()))

        result: Dict[str, Dict[date, float]] = {}
        for row in cursor.fetchall():
            member = row["member_name"]
            log_date = date.fromisoformat(row["logged_at"])
            hours = row["daily_hours"]

            if member not in result:
                result[member] = {}
            result[member][log_date] = hours

        return result

    def get_members_not_logged(
        self,
        project_key: str,
        check_date: date,
        all_members: List[str]
    ) -> List[str]:
        """Get members who haven't logged time on a specific date."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT member_name
            FROM time_logs
            WHERE project_key = ?
              AND logged_at = ?
        """, (project_key, check_date.isoformat()))

        logged_members = {row["member_name"] for row in cursor.fetchall()}
        return [m for m in all_members if m not in logged_members]

    def get_last_log_date_per_member(
        self,
        project_key: str,
        members: List[str]
    ) -> Dict[str, Optional[date]]:
        """Get last log date for each member."""
        conn = VaultDB.get_connection()
        cursor = conn.cursor()

        result: Dict[str, Optional[date]] = {m: None for m in members}

        cursor.execute("""
            SELECT member_name, MAX(logged_at) as last_log
            FROM time_logs
            WHERE project_key = ?
            GROUP BY member_name
        """, (project_key,))

        for row in cursor.fetchall():
            member = row["member_name"]
            if member in result:
                result[member] = date.fromisoformat(row["last_log"])

        return result

    def _row_to_entry(self, row) -> TimeLogEntry:
        """Convert database row to TimeLogEntry."""
        return TimeLogEntry(
            id=row["id"],
            project_key=row["project_key"],
            issue_key=row["issue_key"],
            member_id=row["member_id"],
            member_name=row["member_name"],
            hours_delta=row["hours_delta"],
            total_after=row["total_after"],
            logged_at=date.fromisoformat(row["logged_at"]) if row["logged_at"] else None,
            activity_id=row["activity_id"],
            synced_at=row["synced_at"]
        )
