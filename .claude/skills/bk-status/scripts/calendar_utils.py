"""Calendar utilities for bk-status skill.

This module re-exports calendar utils from common/backlog for backward compatibility.
All calendar code is maintained in .claude/skills/common/backlog/calendar_utils.py
"""

import sys
from pathlib import Path

# Add common to path
_common_dir = Path(__file__).parent.parent.parent / "common"
if str(_common_dir) not in sys.path:
    sys.path.insert(0, str(_common_dir))

# Re-export all calendar utils from common
from backlog.calendar_utils import (
    CalendarConfig,
    get_member_capacity,
    get_all_member_capacities,
    get_sprint_info,
    sync_sprint_from_api,
)

__all__ = [
    "CalendarConfig",
    "get_member_capacity",
    "get_all_member_capacities",
    "get_sprint_info",
    "sync_sprint_from_api",
]
