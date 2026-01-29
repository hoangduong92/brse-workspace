"""Translations for bk-status skill reports.

Supports: English (en), Vietnamese (vi).
Add more languages by adding new keys to TRANSLATIONS dict.
"""

from typing import Optional
from pathlib import Path

# Default language
DEFAULT_LANG = "en"
SUPPORTED_LANGS = ["en", "vi", "ja"]


# Translation strings organized by section
TRANSLATIONS = {
    "en": {
        # Report header
        "report_title": "Project Status Report",
        "date": "Date",
        "project": "Project",
        "sprint_end": "Sprint End",

        # Summary section
        "summary": "Summary",
        "metric": "Metric",
        "value": "Value",
        "estimated_hours": "Estimated Hours",
        "actual_hours": "Actual Hours",
        "progress": "Progress",
        "total_issues": "Total Issues",
        "closed": "Closed",
        "by_status": "By Status",
        "status": "Status",
        "count": "Count",

        # Executive Summary / Action Items
        "action_items": "⚡ Action Required",
        "action_items_note": "Issues requiring immediate attention:",
        "no_action_items": "✅ No issues requiring immediate action",
        "issue_overdue": "🔴 Overdue",
        "issue_impossible": "🔴 Impossible schedule",
        "issue_needs_reest": "🔴 Needs re-estimate",
        "issue_needs_overtime": "⚠️ Needs overtime",
        "issue_will_miss": "📅 Will miss deadline",
        "overdue_detail": "{days} days overdue",
        "impossible_detail": "Need {hours}h but only 1 day (start=due)",
        "reest_detail": "Actual ({actual}h) >= Estimate ({est}h)",
        "overtime_detail": "Need {velocity}h/day, capacity {capacity}h/day",
        "will_miss_detail": "Due {due} → Complete {completion}",
        "status_ok_overdue": "✅ No overdue tasks",
        "status_ok_overtime": "✅ No tasks needing overtime",
        "status_ok_impossible": "✅ No impossible schedules",
        "status_ok_reest": "✅ No tasks needing re-estimate",

        # At-risk tasks (renamed for clarity)
        "at_risk_tasks": "Tasks Needing Overtime",
        "no_at_risk_tasks": "No tasks needing overtime to meet deadline.",
        "issue": "Issue",
        "required": "Required",
        "capacity": "Capacity",
        "days": "Days",
        "reason": "Reason",
        "at_risk_reason": "Need {velocity:.1f}h/day > {capacity:.1f}h capacity (+{gap:.1f}h/day over)",

        # Late tasks
        "late_tasks": "Late Tasks",
        "no_late_tasks": "No late tasks.",
        "assignee": "Assignee",
        "days_overdue": "Days Overdue",
        "unassigned": "Unassigned",

        # BrSE Insights
        "brse_insights_title": "BrSE Insights - Member Capacity",
        "analysis_date": "Analysis Date",
        "gap_note": "**Note:** Gap = Available Capacity - Workload. Positive = surplus, Negative = deficit (needs reschedule).",
        "capacity_overview": "Capacity Overview",
        "member": "Member",
        "tasks": "Tasks",
        "workload": "Workload",
        "gap": "Gap",
        "velocity": "Velocity",

        # Member status
        "status_surplus": "✅ Surplus",
        "status_on_track": "🟢 On Track",
        "status_at_risk": "⚠️ At Risk",
        "status_overloaded": "🔴 Overload",

        # Member details
        "tasks_open": "{count} open",
        "workload_remaining": "{hours:.0f}h remaining",
        "capacity_detail": "{hours:.0f}h ({days} days × {per_day:.0f}h/day)",
        "gap_surplus": "+{gap:.0f}h (can support others)",
        "gap_deficit": "{gap:.0f}h (**needs reschedule**)",
        "due_range": "Due Range",

        # Task table
        "est": "Est",
        "act": "Act",
        "due": "Due",
        "alert": "Alert",
        "alert_resched": "⚠️ RESCHED",
        "alert_reest": "🔴 RE-EST",
        "alert_deficit": "🔴 Deficit",
        "alert_ok": "✅",

        # Re-estimation section
        "reest_title": "🔴 Action Required - Tasks Need Re-estimation",
        "reest_desc": "These tasks have actual hours >= estimated hours.",
        "reest_action": "**Cannot schedule without new estimate.** Please re-estimate remaining work.",
        "over_pct": "Over%",

        # Reschedule section (impossible schedules)
        "resched_title": "⚠️ Action Required - Tasks Need Rescheduling",
        "resched_desc": "These tasks have start_date = due_date but remaining work exceeds daily capacity.",
        "resched_action": "**Impossible to complete in 1 day.** Please extend due_date or reduce scope.",

        # Recommendations
        "recommendations": "💡 Recommendations",
        "on_track_msg": "- Project is on track. No action needed.",
        "urgent_resched": "- **⚠️ URGENT:** {count} tasks have impossible schedule (start=due, extend due_date)",
        "urgent_reest": "- **🔴 URGENT:** {count} tasks need re-estimation before scheduling",
        "available_support": "- **Available support:** {names} has +{hours:.0f}h surplus capacity",
        "needs_help": "- **Needs help:** {name} is {hours:.0f}h short",
        "suggested_action": "**Suggested action:** Reassign tasks from overloaded to surplus members",

        # Schedule warnings
        "schedule_warnings": "⚠️ Schedule Warnings",
        "schedule_warnings_desc": "The following tasks have dates falling on **non-working days**.",
        "schedule_warnings_action": "Please confirm if this is intentional or needs adjustment.",
        "date_type": "Date Type",
        "action_required": "**Action Required:** Review these dates and update if needed.",

        # Gantt schedule
        "daily_schedule": "Daily Schedule (Gantt) - PROPOSED",
        "daily_schedule_note": "⚠️ **Note:** Schedule below is a **PROPOSAL** based on actual capacity. Tasks with infeasible due_dates are auto-extended.",
        "daily_total": "**Daily Total**",
        "gantt_legend": "**Legend:** ✅ = on-time | ⚠️ = late (past due) | ↑Xh = need X more hours | **📅 BOLD** = proposed schedule",
        "schedule_truncated": "*Schedule truncated to 14 days. Full range extends to {end}*",

        # Task table GAP note
        "task_gap_note": "**Gap:** Available hours until due_date minus remaining hours. Positive = buffer time, Negative = not enough time.",

        # Capacity exceeded
        "capacity_exceeded": "🚨 Capacity Exceeded - Re-scheduling Required",
        "total_workload": "Total Workload",
        "available_capacity": "Available Capacity",
        "deficit": "Deficit",
        "unscheduled_desc": "The following tasks **cannot be fully scheduled** within sprint capacity:",
        "need": "Need",
        "scheduled": "Scheduled",
        "shortfall": "Shortfall",

        # Priority question
        "priority_question_title": "📋 Please Specify Task Priority",
        "priority_question_desc": "To create a feasible schedule, please answer:",
        "priority_q1": "1. **Which tasks are highest priority?** (must complete this sprint)",
        "priority_q2": "2. **Which tasks can be moved to next sprint?**",
        "priority_q3": "3. **Can any team member work overtime?** (increase hours_per_day)",
        "priority_q4": "4. **Can tasks be reassigned?** (to members with surplus capacity)",
        "priority_footer": "*Update task priorities in Backlog or provide feedback to re-generate schedule.*",
    },

    "vi": {
        # Report header
        "report_title": "Báo Cáo Tiến Độ Dự Án",
        "date": "Ngày",
        "project": "Dự án",
        "sprint_end": "Kết thúc Sprint",

        # Summary section
        "summary": "Tổng quan",
        "metric": "Chỉ số",
        "value": "Giá trị",
        "estimated_hours": "Giờ dự kiến",
        "actual_hours": "Giờ thực tế",
        "progress": "Tiến độ",
        "total_issues": "Tổng số issue",
        "closed": "Đã đóng",
        "by_status": "Theo trạng thái",
        "status": "Trạng thái",
        "count": "Số lượng",

        # Executive Summary / Action Items
        "action_items": "⚡ Cần hành động ngay",
        "action_items_note": "Các issue cần xử lý ngay:",
        "no_action_items": "✅ Không có issue nào cần xử lý ngay",
        "issue_overdue": "🔴 Đã trễ hạn",
        "issue_impossible": "🔴 Lịch bất khả thi",
        "issue_needs_reest": "🔴 Cần đánh giá lại",
        "issue_needs_overtime": "⚠️ Cần overtime",
        "issue_will_miss": "📅 Sẽ trễ deadline",
        "overdue_detail": "Trễ {days} ngày",
        "impossible_detail": "Cần {hours}h nhưng chỉ 1 ngày (start=due)",
        "reest_detail": "Thực tế ({actual}h) >= Dự kiến ({est}h)",
        "overtime_detail": "Cần {velocity}h/ngày, năng lực {capacity}h/ngày",
        "will_miss_detail": "Hạn {due} → Xong {completion}",
        "status_ok_overdue": "✅ Không có task trễ hạn",
        "status_ok_overtime": "✅ Không có task cần overtime",
        "status_ok_impossible": "✅ Không có lịch bất khả thi",
        "status_ok_reest": "✅ Không có task cần đánh giá lại",

        # At-risk tasks (renamed for clarity)
        "at_risk_tasks": "Task cần overtime để kịp deadline",
        "no_at_risk_tasks": "Không có task nào cần overtime.",
        "issue": "Issue",
        "required": "Yêu cầu",
        "capacity": "Năng lực",
        "days": "Ngày",
        "reason": "Lý do",
        "at_risk_reason": "Cần {velocity:.1f}h/ngày > {capacity:.1f}h năng lực (+{gap:.1f}h/ngày vượt)",

        # Late tasks
        "late_tasks": "Task trễ hạn",
        "no_late_tasks": "Không có task trễ hạn.",
        "assignee": "Người thực hiện",
        "days_overdue": "Số ngày trễ",
        "unassigned": "Chưa giao",

        # BrSE Insights
        "brse_insights_title": "BrSE Insights - Năng lực thành viên",
        "analysis_date": "Ngày phân tích",
        "gap_note": "**Ghi chú:** Gap = Năng lực - Khối lượng công việc. Dương = dư, Âm = thiếu (cần điều chỉnh).",
        "capacity_overview": "Tổng quan năng lực",
        "member": "Thành viên",
        "tasks": "Task",
        "workload": "Khối lượng",
        "gap": "Gap",
        "velocity": "Tốc độ",

        # Member status
        "status_surplus": "✅ Dư",
        "status_on_track": "🟢 Đúng tiến độ",
        "status_at_risk": "⚠️ Rủi ro",
        "status_overloaded": "🔴 Quá tải",

        # Member details
        "tasks_open": "{count} đang mở",
        "workload_remaining": "{hours:.0f}h còn lại",
        "capacity_detail": "{hours:.0f}h ({days} ngày × {per_day:.0f}h/ngày)",
        "gap_surplus": "+{gap:.0f}h (có thể hỗ trợ)",
        "gap_deficit": "{gap:.0f}h (**cần điều chỉnh**)",
        "due_range": "Phạm vi deadline",

        # Task table
        "est": "DK",
        "act": "TT",
        "due": "Hạn",
        "alert": "Cảnh báo",
        "alert_resched": "⚠️ RESCHED",
        "alert_reest": "🔴 CẦN ĐG LẠI",
        "alert_deficit": "🔴 Thiếu",
        "alert_ok": "✅",

        # Re-estimation section
        "reest_title": "🔴 Cần hành động - Task cần đánh giá lại",
        "reest_desc": "Các task này có giờ thực tế >= giờ dự kiến.",
        "reest_action": "**Không thể lập lịch nếu chưa đánh giá lại.** Vui lòng ước lượng lại công việc còn lại.",
        "over_pct": "Vượt%",

        # Reschedule section (impossible schedules)
        "resched_title": "⚠️ Cần hành động - Task cần điều chỉnh lịch",
        "resched_desc": "Các task này có start_date = due_date nhưng công việc còn lại vượt năng lực/ngày.",
        "resched_action": "**Không thể hoàn thành trong 1 ngày.** Vui lòng kéo dài due_date hoặc giảm scope.",

        # Recommendations
        "recommendations": "💡 Khuyến nghị",
        "on_track_msg": "- Dự án đang đúng tiến độ. Không cần hành động.",
        "urgent_resched": "- **⚠️ KHẨN CẤP:** {count} task có lịch bất khả thi (start=due, cần kéo dài due_date)",
        "urgent_reest": "- **🔴 KHẨN CẤP:** {count} task cần đánh giá lại trước khi lập lịch",
        "available_support": "- **Có thể hỗ trợ:** {names} dư +{hours:.0f}h năng lực",
        "needs_help": "- **Cần hỗ trợ:** {name} thiếu {hours:.0f}h",
        "suggested_action": "**Đề xuất:** Chuyển task từ người quá tải sang người có năng lực dư",

        # Schedule warnings
        "schedule_warnings": "⚠️ Cảnh báo lịch",
        "schedule_warnings_desc": "Các task sau có ngày rơi vào **ngày nghỉ**.",
        "schedule_warnings_action": "Vui lòng xác nhận hoặc điều chỉnh nếu cần.",
        "date_type": "Loại ngày",
        "action_required": "**Cần hành động:** Xem lại các ngày này và cập nhật nếu cần.",

        # Gantt schedule
        "daily_schedule": "Lịch làm việc hàng ngày (Gantt) - ĐỀ XUẤT",
        "daily_schedule_note": "⚠️ **Lưu ý:** Lịch dưới đây là **ĐỀ XUẤT** dựa trên năng lực thực tế. Task có due_date bất khả thi sẽ được tự động kéo dài.",
        "daily_total": "**Tổng ngày**",
        "gantt_legend": "**Chú thích:** ✅ = đúng hạn | ⚠️ = trễ (vượt due) | ↑Xh = cần thêm X giờ | **📅 IN ĐẬM** = lịch đề xuất",
        "schedule_truncated": "*Lịch cắt ngắn còn 14 ngày. Phạm vi đầy đủ đến {end}*",

        # Task table GAP note
        "task_gap_note": "**Gap:** Số giờ khả dụng đến due_date trừ số giờ còn lại. Dương = còn dư thời gian, Âm = không đủ thời gian.",

        # Capacity exceeded
        "capacity_exceeded": "🚨 Vượt năng lực - Cần điều chỉnh lịch",
        "total_workload": "Tổng khối lượng",
        "available_capacity": "Năng lực khả dụng",
        "deficit": "Thiếu",
        "unscheduled_desc": "Các task sau **không thể lập lịch đầy đủ** trong sprint:",
        "need": "Cần",
        "scheduled": "Đã lập",
        "shortfall": "Thiếu",

        # Priority question
        "priority_question_title": "📋 Vui lòng xác định độ ưu tiên",
        "priority_question_desc": "Để tạo lịch khả thi, vui lòng trả lời:",
        "priority_q1": "1. **Task nào ưu tiên cao nhất?** (phải hoàn thành sprint này)",
        "priority_q2": "2. **Task nào có thể chuyển sang sprint sau?**",
        "priority_q3": "3. **Thành viên nào có thể làm thêm giờ?** (tăng hours_per_day)",
        "priority_q4": "4. **Có thể chuyển task không?** (sang người có năng lực dư)",
        "priority_footer": "*Cập nhật độ ưu tiên trong Backlog hoặc phản hồi để tạo lại lịch.*",
    },

    "ja": {
        # Report header
        "report_title": "プロジェクト進捗レポート",
        "date": "日付",
        "project": "プロジェクト",
        "sprint_end": "スプリント終了",

        # Summary section
        "summary": "概要",
        "metric": "指標",
        "value": "値",
        "estimated_hours": "見積もり時間",
        "actual_hours": "実績時間",
        "progress": "進捗",
        "total_issues": "総課題数",
        "closed": "完了",
        "by_status": "ステータス別",
        "status": "ステータス",
        "count": "件数",

        # Executive Summary / Action Items
        "action_items": "⚡ 要対応",
        "action_items_note": "即座の対応が必要な課題:",
        "no_action_items": "✅ 即座の対応が必要な課題はありません",
        "issue_overdue": "🔴 期限超過",
        "issue_impossible": "🔴 実行不可能なスケジュール",
        "issue_needs_reest": "🔴 再見積必要",
        "issue_needs_overtime": "⚠️ 残業必要",
        "issue_will_miss": "📅 期限超過予定",
        "overdue_detail": "{days}日超過",
        "impossible_detail": "{hours}h必要だが1日のみ（開始=期限）",
        "reest_detail": "実績({actual}h) >= 見積({est}h)",
        "overtime_detail": "{velocity}h/日必要、キャパ{capacity}h/日",
        "will_miss_detail": "期限 {due} → 完了 {completion}",
        "status_ok_overdue": "✅ 期限超過タスクなし",
        "status_ok_overtime": "✅ 残業必要タスクなし",
        "status_ok_impossible": "✅ 実行不可能スケジュールなし",
        "status_ok_reest": "✅ 再見積必要タスクなし",

        # At-risk tasks (renamed for clarity)
        "at_risk_tasks": "残業が必要なタスク",
        "no_at_risk_tasks": "残業が必要なタスクはありません。",
        "issue": "課題",
        "required": "必要",
        "capacity": "キャパシティ",
        "days": "日数",
        "reason": "理由",
        "at_risk_reason": "{velocity:.1f}h/日必要 > {capacity:.1f}hキャパ (+{gap:.1f}h/日超過)",

        # Late tasks
        "late_tasks": "遅延タスク",
        "no_late_tasks": "遅延タスクはありません。",
        "assignee": "担当者",
        "days_overdue": "遅延日数",
        "unassigned": "未割当",

        # BrSE Insights
        "brse_insights_title": "BrSEインサイト - メンバーキャパシティ",
        "analysis_date": "分析日",
        "gap_note": "**注:** Gap = 利用可能キャパ - 作業量。正 = 余裕あり、負 = 不足（調整必要）。",
        "capacity_overview": "キャパシティ概要",
        "member": "メンバー",
        "tasks": "タスク",
        "workload": "作業量",
        "gap": "Gap",
        "velocity": "速度",

        # Member status
        "status_surplus": "✅ 余裕",
        "status_on_track": "🟢 順調",
        "status_at_risk": "⚠️ リスク",
        "status_overloaded": "🔴 過負荷",

        # Member details
        "tasks_open": "{count}件オープン",
        "workload_remaining": "{hours:.0f}h残り",
        "capacity_detail": "{hours:.0f}h ({days}日 × {per_day:.0f}h/日)",
        "gap_surplus": "+{gap:.0f}h (サポート可能)",
        "gap_deficit": "{gap:.0f}h (**調整必要**)",
        "due_range": "期限範囲",

        # Task table
        "est": "見積",
        "act": "実績",
        "due": "期限",
        "alert": "警告",
        "alert_resched": "⚠️ 要調整",
        "alert_reest": "🔴 再見積",
        "alert_deficit": "🔴 不足",
        "alert_ok": "✅",

        # Re-estimation section
        "reest_title": "🔴 アクション必要 - 再見積が必要なタスク",
        "reest_desc": "これらのタスクは実績時間 >= 見積時間です。",
        "reest_action": "**再見積なしではスケジュール不可。** 残作業を再見積してください。",
        "over_pct": "超過%",

        # Reschedule section (impossible schedules)
        "resched_title": "⚠️ アクション必要 - スケジュール調整が必要なタスク",
        "resched_desc": "これらのタスクは開始日 = 期限日ですが、残作業が1日のキャパシティを超えています。",
        "resched_action": "**1日で完了不可能。** 期限日を延長するかスコープを縮小してください。",

        # Recommendations
        "recommendations": "💡 推奨事項",
        "on_track_msg": "- プロジェクトは順調です。アクション不要。",
        "urgent_resched": "- **⚠️ 緊急:** {count}件のタスクが実行不可能なスケジュール（開始=期限、期限延長が必要）",
        "urgent_reest": "- **🔴 緊急:** {count}件のタスクがスケジュール前に再見積必要",
        "available_support": "- **サポート可能:** {names}は+{hours:.0f}hの余裕あり",
        "needs_help": "- **サポート必要:** {name}は{hours:.0f}h不足",
        "suggested_action": "**提案:** 過負荷メンバーから余裕のあるメンバーへタスクを移動",

        # Schedule warnings
        "schedule_warnings": "⚠️ スケジュール警告",
        "schedule_warnings_desc": "以下のタスクの日付が**非稼働日**に設定されています。",
        "schedule_warnings_action": "意図的かどうか確認し、必要に応じて調整してください。",
        "date_type": "日付種別",
        "action_required": "**アクション必要:** これらの日付を確認し、必要に応じて更新してください。",

        # Gantt schedule
        "daily_schedule": "日別スケジュール（ガント） - 提案",
        "daily_schedule_note": "⚠️ **注:** 以下のスケジュールは実際のキャパシティに基づく**提案**です。実行不可能な期限のタスクは自動延長されます。",
        "daily_total": "**日計**",
        "gantt_legend": "**凡例:** ✅ = 期限内 | ⚠️ = 遅延（期限超過） | ↑Xh = X時間追加必要 | **📅 太字** = 提案スケジュール",
        "schedule_truncated": "*スケジュールは14日に短縮。全期間は{end}まで*",

        # Task table GAP note
        "task_gap_note": "**Gap:** 期限日までの利用可能時間から残り時間を引いた値。正 = 余裕あり、負 = 時間不足。",

        # Capacity exceeded
        "capacity_exceeded": "🚨 キャパシティ超過 - リスケジュール必要",
        "total_workload": "総作業量",
        "available_capacity": "利用可能キャパ",
        "deficit": "不足",
        "unscheduled_desc": "以下のタスクはスプリント内で**フルスケジュール不可**:",
        "need": "必要",
        "scheduled": "スケジュール済",
        "shortfall": "不足",

        # Priority question
        "priority_question_title": "📋 タスク優先度の指定をお願いします",
        "priority_question_desc": "実行可能なスケジュールを作成するため、以下にお答えください:",
        "priority_q1": "1. **最優先タスクは？** (このスプリント必須)",
        "priority_q2": "2. **次スプリントに移動可能なタスクは？**",
        "priority_q3": "3. **残業可能なメンバーは？** (hours_per_dayを増加)",
        "priority_q4": "4. **タスクの再割当は可能？** (余裕のあるメンバーへ)",
        "priority_footer": "*Backlogで優先度を更新するか、フィードバックしてスケジュールを再生成してください。*",
    }
}


def get_text(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """Get translated text by key.

    Args:
        key: Translation key
        lang: Language code (en, vi)
        **kwargs: Format arguments for string interpolation

    Returns:
        Translated string, or key if not found
    """
    if lang not in TRANSLATIONS:
        lang = DEFAULT_LANG

    text = TRANSLATIONS[lang].get(key, TRANSLATIONS[DEFAULT_LANG].get(key, key))

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def get_lang_from_master_yaml(yaml_path: Optional[Path] = None) -> str:
    """Get language setting from master.yaml.

    Args:
        yaml_path: Path to master.yaml (default: brsekit/master.yaml)

    Returns:
        Language code (default: "en")
    """
    import yaml

    if yaml_path is None:
        skill_dir = Path(__file__).parent.parent.parent  # .claude/skills
        yaml_path = skill_dir / "brsekit" / "master.yaml"

    if not yaml_path.exists():
        return DEFAULT_LANG

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("lang", DEFAULT_LANG)
    except Exception:
        return DEFAULT_LANG


class Translator:
    """Helper class for translating report text."""

    def __init__(self, lang: str = DEFAULT_LANG):
        """Initialize translator.

        Args:
            lang: Language code (en, vi)
        """
        self.lang = lang if lang in SUPPORTED_LANGS else DEFAULT_LANG

    def t(self, key: str, **kwargs) -> str:
        """Translate key to current language.

        Args:
            key: Translation key
            **kwargs: Format arguments

        Returns:
            Translated string
        """
        return get_text(key, self.lang, **kwargs)

    @classmethod
    def from_master_yaml(cls, yaml_path: Optional[Path] = None) -> "Translator":
        """Create translator from master.yaml config.

        Args:
            yaml_path: Path to master.yaml

        Returns:
            Translator instance
        """
        lang = get_lang_from_master_yaml(yaml_path)
        return cls(lang)
