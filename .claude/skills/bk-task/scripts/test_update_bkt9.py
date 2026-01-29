"""Test script to update BKT-9 with new bilingual template."""

import sys
import io
from pathlib import Path

# Fix Windows console encoding for Japanese/Vietnamese characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add common to path
_common_dir = Path(__file__).parent.parent.parent / "common"
if str(_common_dir) not in sys.path:
    sys.path.insert(0, str(_common_dir))

import os


def load_env_file(path: Path) -> None:
    """Simple .env file loader."""
    if not path.exists():
        return
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


# Load env from multiple locations
load_env_file(Path(__file__).parent.parent / ".env")
load_env_file(Path(__file__).parent.parent.parent / ".env")

from backlog.client import BacklogClient


def main():
    """Update BKT-9 with new bilingual template."""
    # Get credentials from env
    space_url = os.getenv("NULAB_SPACE_URL")
    api_key = os.getenv("NULAB_API_KEY")

    if not space_url or not api_key:
        print("Error: NULAB_SPACE_URL and NULAB_API_KEY must be set")
        print("Set these in .claude/skills/bk-task/.env or .claude/skills/.env")
        sys.exit(1)

    # Initialize client
    client = BacklogClient(space_url, api_key)

    # Get current BKT-9
    print("Fetching BKT-9...")
    issue = client.get_issue("BKT-9")

    print(f"\nCurrent BKT-9:")
    print(f"  Summary: {issue.get('summary')}")
    print(f"  Status: {issue.get('status', {}).get('name')}")
    print(f"  Description: {issue.get('description', '(empty)')[:100]}...")

    # New bilingual template
    # Original: 待合室機能を実装 (Implement waiting room feature)
    new_summary = "[TASK] Triển khai chức năng phòng chờ -- 待合室機能を実装"

    new_description = """## [TASK] Triển khai chức năng phòng chờ -- 待合室機能を実装

### Mô tả (説明)
Triển khai chức năng phòng chờ cho ứng dụng.
Bao gồm: giao diện phòng chờ, real-time updates, notification khi được gọi.

待合室機能をアプリに実装する。
待合室UI、リアルタイム更新、呼び出し通知を含む。

### Tiêu chí hoàn thành (完了基準)
- [ ] Waiting room UI implemented / 待合室UI実装完了
- [ ] Real-time status updates / リアルタイムステータス更新
- [ ] Push notification when called / 呼び出し時プッシュ通知
- [ ] Unit tests written / ユニットテスト作成

### Ghi chú (備考)
- Reference existing queue system
- Consider mobile responsiveness
"""

    print(f"\nNew template:")
    print(f"  Summary: {new_summary}")
    print(f"  Description preview: {new_description[:200]}...")

    # Check for --execute flag
    if len(sys.argv) < 2 or sys.argv[1] != "--execute":
        print("\n" + "="*60)
        print("PREVIEW MODE - No changes made")
        print("To execute the update, run with --execute flag:")
        print("  python test_update_bkt9.py --execute")
        print("="*60)
        return

    # Update issue
    print("\nUpdating BKT-9...")
    updated = client.update_issue(
        "BKT-9",
        summary=new_summary,
        description=new_description
    )

    print(f"\nUpdated successfully!")
    print(f"  Summary: {updated.get('summary')}")
    print(f"  Issue Key: {updated.get('issueKey')}")


if __name__ == "__main__":
    main()
