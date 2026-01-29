"""Backlog API client for bk-status skill.

This module re-exports client from common/backlog for backward compatibility.
All client code is maintained in .claude/skills/common/backlog/client.py
"""

import sys
from pathlib import Path

# Add common to path
_common_dir = Path(__file__).parent.parent.parent / "common"
if str(_common_dir) not in sys.path:
    sys.path.insert(0, str(_common_dir))

# Re-export client from common
from backlog.client import (
    BacklogClient,
    BacklogAPIError,
)

# Re-export models for backward compatibility (some files import from backlog_client)
from backlog.models import (
    Issue,
    User,
    Status,
    Project,
)

__all__ = [
    "BacklogClient",
    "BacklogAPIError",
    "Issue",
    "User",
    "Status",
    "Project",
]
