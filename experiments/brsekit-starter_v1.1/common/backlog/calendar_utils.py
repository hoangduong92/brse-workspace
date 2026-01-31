"""Calendar utilities for BrseKit skills.

Handles working days calculation with weekend and holiday support.
Loads configuration from brsekit/master.yaml.
"""

from datetime import date, timedelta
from pathlib import Path
from typing import Optional
import yaml


class CalendarConfig:
    """Calendar configuration with working days and holidays."""

    # Monday=0, Sunday=6
    DEFAULT_WORKING_DAYS = [0, 1, 2, 3, 4]  # Mon-Fri

    def __init__(
        self,
        working_days: Optional[list[int]] = None,
        holidays: Optional[list[date]] = None,
        default_hours_per_day: float = 6.0,
        daily_standup: str = "morning"
    ):
        """Initialize calendar config.

        Args:
            working_days: List of weekday numbers (0=Mon, 6=Sun)
            holidays: List of holiday dates to skip
            default_hours_per_day: Default working hours per day (single source of truth)
            daily_standup: "morning" or "evening" - affects days_remaining calculation
                - morning: today is still workable
                - evening: only count from tomorrow
        """
        self.working_days = set(working_days or self.DEFAULT_WORKING_DAYS)
        self.holidays = set(holidays or [])
        self.default_hours_per_day = default_hours_per_day
        self.daily_standup = daily_standup

    def is_working_day(self, d: date) -> bool:
        """Check if date is a working day.

        Args:
            d: Date to check

        Returns:
            True if working day (not weekend, not holiday)
        """
        if d.weekday() not in self.working_days:
            return False
        if d in self.holidays:
            return False
        return True

    def is_weekend(self, d: date) -> bool:
        """Check if date is a weekend (not in working_days).

        Args:
            d: Date to check

        Returns:
            True if weekend day
        """
        return d.weekday() not in self.working_days

    def check_date_warning(self, d: date) -> Optional[str]:
        """Check if date falls on non-working day and return warning reason.

        Args:
            d: Date to check

        Returns:
            Warning string if non-working day, None otherwise
        """
        if d in self.holidays:
            return "holiday"
        if d.weekday() not in self.working_days:
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            return f"weekend ({day_names[d.weekday()]})"
        return None

    def count_working_days(self, start: date, end: date) -> int:
        """Count working days between two dates (inclusive).

        Args:
            start: Start date (today, after daily standup)
            end: End date (due date, inclusive)

        Returns:
            Number of working days
        """
        if end < start:
            return 0

        working_days = 0
        current = start
        while current <= end:
            if self.is_working_day(current):
                working_days += 1
            current += timedelta(days=1)
        return working_days

    def count_remaining_working_days(self, today: date, due_date: date) -> int:
        """Count remaining working days from today to due_date, considering daily_standup.

        Args:
            today: Current date
            due_date: Task due date

        Returns:
            Number of working days remaining (considers daily_standup timing)
            - morning standup: today is included if it's a working day
            - evening standup: today is excluded, count from tomorrow
        """
        if due_date < today:
            return 0

        if self.daily_standup == "evening":
            # Evening: today is done, start from tomorrow
            start = today + timedelta(days=1)
        else:
            # Morning (default): today is still workable
            start = today

        return self.count_working_days(start, due_date)

    def get_working_days_list(self, start: date, end: date) -> list[date]:
        """Get list of working days between two dates.

        Args:
            start: Start date
            end: End date (inclusive)

        Returns:
            List of working day dates
        """
        if end < start:
            return []

        result = []
        current = start
        while current <= end:
            if self.is_working_day(current):
                result.append(current)
            current += timedelta(days=1)
        return result

    @classmethod
    def from_master_yaml(cls, yaml_path: Optional[Path] = None) -> "CalendarConfig":
        """Load calendar config from brsekit master.yaml.

        Args:
            yaml_path: Path to master.yaml (default: brsekit/master.yaml)

        Returns:
            CalendarConfig instance
        """
        if yaml_path is None:
            # Look for master.yaml in brsekit skill directory
            skill_dir = Path(__file__).parent.parent.parent  # .claude/skills
            yaml_path = skill_dir / "brsekit" / "master.yaml"

        if not yaml_path.exists():
            # Return default config if file not found
            return cls()

        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            return cls()

        calendar_data = data.get("calendar", {})

        # Parse working days
        working_days = calendar_data.get("working_days", cls.DEFAULT_WORKING_DAYS)

        # Parse holidays
        holidays = []
        for h in calendar_data.get("holidays", []):
            date_str = h.get("date")
            if date_str:
                try:
                    holidays.append(date.fromisoformat(date_str))
                except ValueError:
                    pass

        # Parse default hours (single source of truth for capacity)
        default_hours = calendar_data.get("default_hours_per_day", 6.0)

        # Parse daily standup timing (morning/evening)
        daily_standup = calendar_data.get("daily_standup", "morning")

        return cls(
            working_days=working_days,
            holidays=holidays,
            default_hours_per_day=default_hours,
            daily_standup=daily_standup
        )


def get_member_capacity(
    member_name: str,
    yaml_path: Optional[Path] = None
) -> Optional[float]:
    """Get member's capacity hours per day from master.yaml.

    Args:
        member_name: Member name to look up
        yaml_path: Path to master.yaml

    Returns:
        Hours per day capacity, or None if not found
    """
    if yaml_path is None:
        skill_dir = Path(__file__).parent.parent.parent
        yaml_path = skill_dir / "brsekit" / "master.yaml"

    if not yaml_path.exists():
        return None

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return None

    team_data = data.get("team", {})
    members = team_data.get("members", [])

    for member in members:
        if member.get("name") == member_name:
            return member.get("capacity_hours_per_day")

    return None


def get_all_member_capacities(
    yaml_path: Optional[Path] = None
) -> dict[str, float]:
    """Get all members' capacity hours per day from master.yaml.

    Args:
        yaml_path: Path to master.yaml

    Returns:
        Dict mapping member_name -> capacity_hours_per_day
    """
    if yaml_path is None:
        skill_dir = Path(__file__).parent.parent.parent
        yaml_path = skill_dir / "brsekit" / "master.yaml"

    if not yaml_path.exists():
        return {}

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return {}

    team_data = data.get("team", {})
    members = team_data.get("members", [])

    result = {}
    for member in members:
        name = member.get("name")
        capacity = member.get("capacity_hours_per_day")
        if name and capacity:
            result[name] = float(capacity)

    return result


def get_sprint_info(yaml_path: Optional[Path] = None) -> dict:
    """Get current sprint info from master.yaml.

    Args:
        yaml_path: Path to master.yaml

    Returns:
        Dict with sprint_name, start_date, end_date or empty dict
    """
    if yaml_path is None:
        skill_dir = Path(__file__).parent.parent.parent
        yaml_path = skill_dir / "brsekit" / "master.yaml"

    if not yaml_path.exists():
        return {}

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception:
        return {}

    sprints_data = data.get("sprints", {})
    current_sprint_name = sprints_data.get("current")

    if not current_sprint_name:
        return {}

    for sprint in sprints_data.get("definitions", []):
        if sprint.get("name") == current_sprint_name:
            result = {"sprint_name": sprint.get("name")}

            if sprint.get("start_date"):
                try:
                    result["start_date"] = date.fromisoformat(sprint["start_date"])
                except ValueError:
                    pass

            if sprint.get("end_date"):
                try:
                    result["end_date"] = date.fromisoformat(sprint["end_date"])
                except ValueError:
                    pass

            return result

    return {}


def sync_sprint_from_api(
    milestone_name: str,
    milestone_end_date: date,
    yaml_path: Optional[Path] = None
) -> tuple[bool, str]:
    """Sync sprint end_date from Backlog API milestone to master.yaml.

    Args:
        milestone_name: Name of milestone from Backlog API
        milestone_end_date: End date from Backlog API
        yaml_path: Path to master.yaml

    Returns:
        Tuple of (changed: bool, message: str)
    """
    if yaml_path is None:
        skill_dir = Path(__file__).parent.parent.parent
        yaml_path = skill_dir / "brsekit" / "master.yaml"

    if not yaml_path.exists():
        return False, f"master.yaml not found: {yaml_path}"

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
            f.seek(0)
            data = yaml.safe_load(f)
    except Exception as e:
        return False, f"Failed to read master.yaml: {e}"

    sprints_data = data.get("sprints", {})
    definitions = sprints_data.get("definitions", [])

    # Find matching sprint by name
    for sprint in definitions:
        if sprint.get("name") == milestone_name:
            old_end = sprint.get("end_date")
            new_end = milestone_end_date.isoformat()

            if old_end == new_end:
                return False, f"Sprint '{milestone_name}' already synced (end_date: {new_end})"

            # Update the end_date in YAML content (preserve formatting)
            if old_end:
                updated_content = content.replace(
                    f'end_date: "{old_end}"',
                    f'end_date: "{new_end}"'
                )
            else:
                # Add end_date if not exists (rare case)
                updated_content = content

            try:
                with open(yaml_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                return True, f"Synced '{milestone_name}' end_date: {old_end} -> {new_end}"
            except Exception as e:
                return False, f"Failed to write master.yaml: {e}"

    return False, f"Sprint '{milestone_name}' not found in master.yaml definitions"
