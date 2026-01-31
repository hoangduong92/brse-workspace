"""Master data loader for BrseKit skills."""

import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# Use simple YAML parsing without external dependency
# For production, consider using PyYAML


class MasterData:
    """Container for parsed master data."""

    def __init__(self, data: dict):
        self._data = data

    @property
    def team(self) -> dict:
        return self._data.get("team", {})

    @property
    def members(self) -> list[dict]:
        return self.team.get("members", [])

    @property
    def calendar(self) -> dict:
        return self._data.get("calendar", {})

    @property
    def holidays(self) -> list[dict]:
        return self.calendar.get("holidays", [])

    @property
    def sprints(self) -> dict:
        return self._data.get("sprints", {})

    @property
    def current_sprint(self) -> Optional[str]:
        return self.sprints.get("current")

    @property
    def thresholds(self) -> dict:
        return self._data.get("thresholds", {})

    def get_member_by_id(self, member_id: int) -> Optional[dict]:
        """Get member config by Backlog user ID."""
        for m in self.members:
            if m.get("id") == member_id:
                return m
        return None

    def get_member_by_name(self, name: str) -> Optional[dict]:
        """Get member config by name (case-insensitive)."""
        name_lower = name.lower()
        for m in self.members:
            if m.get("name", "").lower() == name_lower:
                return m
        return None

    def get_member_capacity(self, member_id: int) -> float:
        """Get member's daily capacity in hours."""
        member = self.get_member_by_id(member_id)
        if member:
            return member.get("capacity_hours_per_day", 6.0)
        return self.calendar.get("default_hours_per_day", 6.0)

    def is_holiday(self, check_date: date) -> bool:
        """Check if a date is a holiday."""
        date_str = check_date.isoformat()
        for h in self.holidays:
            if h.get("date") == date_str:
                return True
        return False

    def get_holiday_dates(self) -> set[date]:
        """Get all holiday dates as a set."""
        result = set()
        for h in self.holidays:
            date_str = h.get("date")
            if date_str:
                try:
                    result.add(date.fromisoformat(date_str))
                except ValueError:
                    pass
        return result

    def get_current_sprint_end(self) -> Optional[date]:
        """Get current sprint end date."""
        current = self.current_sprint
        if not current:
            return None
        for s in self.sprints.get("definitions", []):
            if s.get("name") == current:
                end_str = s.get("end_date")
                if end_str:
                    try:
                        return date.fromisoformat(end_str)
                    except ValueError:
                        pass
        return None

    def can_member_support(self, helper_id: int, task_skills: list[str]) -> bool:
        """Check if a member can support tasks requiring given skills."""
        helper = self.get_member_by_id(helper_id)
        if not helper:
            return False

        can_support = set(helper.get("can_support", []))
        task_skill_set = set(task_skills)

        # Check for any overlap
        return bool(can_support & task_skill_set)


def load_master_data(master_path: Optional[Path] = None) -> MasterData:
    """Load master data from YAML file.

    Args:
        master_path: Path to master.yaml. If None, uses default location.

    Returns:
        MasterData instance with parsed configuration
    """
    if master_path is None:
        # Default: .claude/skills/brsekit/master.yaml relative to project root
        master_path = Path(__file__).parent / "master.yaml"

    if not master_path.exists():
        # Return empty data if file not found
        return MasterData({})

    # Simple YAML parsing (basic support without PyYAML)
    # For production, install and use PyYAML for full support
    try:
        import yaml
        with open(master_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return MasterData(data or {})
    except ImportError:
        # Fallback: return empty if PyYAML not installed
        print("Warning: PyYAML not installed. Install with: pip install pyyaml")
        return MasterData({})
    except Exception as e:
        print(f"Error loading master data: {e}")
        return MasterData({})


# Convenience function
def get_master() -> MasterData:
    """Get master data singleton."""
    return load_master_data()
