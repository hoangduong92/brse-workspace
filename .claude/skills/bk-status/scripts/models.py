"""Data models for bk-status skill.

This module re-exports models from common/backlog for backward compatibility.
All models are maintained in .claude/skills/common/backlog/models.py
"""

import sys
from pathlib import Path

# Add common to path
_common_dir = Path(__file__).parent.parent.parent / "common"
if str(_common_dir) not in sys.path:
    sys.path.insert(0, str(_common_dir))

# Re-export all models from common
from backlog.models import (
    RiskLevel,
    User,
    Status,
    Project,
    Issue,
)

__all__ = [
    "RiskLevel",
    "User",
    "Status",
    "Project",
    "Issue",
]
