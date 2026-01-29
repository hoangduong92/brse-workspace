"""Tests for task_parser.py - TDD approach."""

import json
import pytest
from datetime import date, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from task_parser import (
    TaskParser,
    ParsedTask,
    TaskType,
    Priority,
    DeadlineType,
    parse_task,
    parse_multiple_tasks,
)


# Load test fixtures
@pytest.fixture
def fixtures():
    """Load sample inputs from fixtures."""
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_inputs.json"
    with open(fixtures_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def parser():
    """Create TaskParser instance."""
    return TaskParser()


class TestTaskTypeDetection:
    """Test task type detection from Japanese keywords."""

    def test_bug_keywords(self, parser):
        """Detect bug type from keywords: 不具合, バグ, エラー."""
        assert parser.detect_task_type("ログインでエラーが発生") == TaskType.BUG
        assert parser.detect_task_type("バグ修正お願いします") == TaskType.BUG
        assert parser.detect_task_type("不具合があります") == TaskType.BUG

    def test_feature_keywords(self, parser):
        """Detect feature type from keywords: 機能追加, 実装, 作成."""
        assert parser.detect_task_type("ログイン機能を実装") == TaskType.FEATURE
        assert parser.detect_task_type("新規画面を作成") == TaskType.FEATURE
        assert parser.detect_task_type("機能追加お願いします") == TaskType.FEATURE

    def test_question_keywords(self, parser):
        """Detect question type from keywords: 質問, 確認, ?."""
        assert parser.detect_task_type("仕様について質問があります") == TaskType.QUESTION
        assert parser.detect_task_type("これで問題ないか確認したい") == TaskType.QUESTION
        assert parser.detect_task_type("APIの仕様は？") == TaskType.QUESTION

    def test_improvement_keywords(self, parser):
        """Detect improvement type from keywords: 改善, 最適化."""
        assert parser.detect_task_type("パフォーマンス改善") == TaskType.IMPROVEMENT
        assert parser.detect_task_type("コードを最適化") == TaskType.IMPROVEMENT
        assert parser.detect_task_type("リファクタリング") == TaskType.IMPROVEMENT

    def test_default_to_feature(self, parser):
        """Default to feature when no keywords match."""
        assert parser.detect_task_type("ダッシュボード") == TaskType.FEATURE


class TestPriorityDetection:
    """Test priority detection from Japanese keywords."""

    def test_high_priority_keywords(self, parser):
        """Detect high priority from: 至急, 緊急, ASAP."""
        assert parser.detect_priority("至急対応お願いします") == Priority.HIGH
        assert parser.detect_priority("緊急で対応が必要") == Priority.HIGH
        assert parser.detect_priority("ASAP please") == Priority.HIGH

    def test_low_priority_keywords(self, parser):
        """Detect low priority from: 時間あれば, 余裕あれば."""
        assert parser.detect_priority("時間あれば対応") == Priority.LOW
        assert parser.detect_priority("余裕があればお願いします") == Priority.LOW
        assert parser.detect_priority("できれば早めに") == Priority.LOW

    def test_default_normal_priority(self, parser):
        """Default to normal priority."""
        assert parser.detect_priority("機能を実装してください") == Priority.NORMAL


class TestDeadlineDetection:
    """Test deadline detection from Japanese text."""

    def test_today_deadline(self, parser):
        """Detect today deadline from: 本日, 今日, 至急."""
        result = parser.detect_deadline("本日中に対応")
        assert result.deadline_type == DeadlineType.TODAY

        result = parser.detect_deadline("今日までにお願いします")
        assert result.deadline_type == DeadlineType.TODAY

    def test_tomorrow_deadline(self, parser):
        """Detect tomorrow deadline from: 明日まで."""
        result = parser.detect_deadline("明日までに完了")
        assert result.deadline_type == DeadlineType.TOMORROW

    def test_end_of_week_deadline(self, parser):
        """Detect end of week from: 今週中."""
        result = parser.detect_deadline("今週中に対応お願いします")
        assert result.deadline_type == DeadlineType.END_OF_WEEK

    def test_end_of_next_week_deadline(self, parser):
        """Detect end of next week from: 来週まで."""
        result = parser.detect_deadline("来週までにレビュー")
        assert result.deadline_type == DeadlineType.END_OF_NEXT_WEEK

    def test_specific_date_yyyymmdd(self, parser):
        """Parse specific date: 2026年2月15日."""
        result = parser.detect_deadline("2026年2月15日までに実装")
        assert result.deadline_type == DeadlineType.SPECIFIC
        assert result.deadline_date == date(2026, 2, 15)

    def test_specific_date_mmdd(self, parser):
        """Parse specific date: 1月30日."""
        result = parser.detect_deadline("1月30日までに完了")
        assert result.deadline_type == DeadlineType.SPECIFIC
        # Year should be inferred as current/next year
        assert result.deadline_date.month == 1
        assert result.deadline_date.day == 30

    def test_specific_date_slash_format(self, parser):
        """Parse specific date: 1/30."""
        result = parser.detect_deadline("1/30までに対応")
        assert result.deadline_type == DeadlineType.SPECIFIC
        assert result.deadline_date.month == 1
        assert result.deadline_date.day == 30

    def test_unclear_deadline(self, parser):
        """Detect unclear deadline."""
        result = parser.detect_deadline("時間あれば対応お願いします")
        assert result.deadline_type == DeadlineType.UNCLEAR


class TestEstimatedHoursExtraction:
    """Test estimated hours extraction."""

    def test_hours_with_kanji(self, parser):
        """Extract hours: 8時間."""
        assert parser.extract_estimated_hours("作業時間は8時間") == 8.0

    def test_hours_with_h(self, parser):
        """Extract hours: 4h."""
        assert parser.extract_estimated_hours("推定4h") == 4.0

    def test_decimal_hours(self, parser):
        """Extract decimal hours: 2.5時間."""
        assert parser.extract_estimated_hours("約2.5時間かかります") == 2.5

    def test_no_hours(self, parser):
        """Return None when no hours found."""
        assert parser.extract_estimated_hours("機能を実装") is None


class TestAssigneeHintExtraction:
    """Test assignee hint extraction."""

    def test_assignee_with_san(self, parser):
        """Extract assignee: 田中さん."""
        assert parser.extract_assignee_hint("田中さんが担当") == "田中"

    def test_assignee_with_kun(self, parser):
        """Extract assignee: 山田くん."""
        assert parser.extract_assignee_hint("山田くんにお願い") == "山田"

    def test_no_assignee(self, parser):
        """Return None when no assignee found."""
        assert parser.extract_assignee_hint("機能を実装") is None


class TestSummaryGeneration:
    """Test summary generation from text."""

    def test_generate_summary_feature(self, parser):
        """Generate summary for feature."""
        text = "ログイン画面を作成してください"
        summary = parser.generate_summary(text)
        assert "ログイン画面" in summary
        assert len(summary) <= 50  # Summary should be concise

    def test_generate_summary_bug(self, parser):
        """Generate summary for bug."""
        text = "ログインボタンが反応しません"
        summary = parser.generate_summary(text)
        assert "ログインボタン" in summary or "反応しない" in summary


class TestFullStructureParsing:
    """TC-TK01: Parse full structure input."""

    def test_parse_full_structure(self, parser, fixtures):
        """Parse: 明日までにログイン画面を田中さんが作成。8時間"""
        test_case = fixtures["test_cases"]["TC-TK01_full_structure"]
        result = parser.parse(test_case["input"])

        assert result.assignee_hint == "田中"
        assert result.deadline_type == DeadlineType.TOMORROW
        assert result.estimated_hours == 8.0
        assert result.task_type == TaskType.FEATURE


class TestImplicitDeadline:
    """TC-TK02: Parse implicit deadline."""

    def test_parse_implicit_deadline(self, parser, fixtures):
        """Parse: 今週中にユーザー登録機能を実装"""
        test_case = fixtures["test_cases"]["TC-TK02_implicit_deadline"]
        result = parser.parse(test_case["input"])

        assert result.deadline_type == DeadlineType.END_OF_WEEK
        assert result.task_type == TaskType.FEATURE


class TestASAPParsing:
    """TC-TK03: Parse ASAP/urgent input."""

    def test_parse_asap(self, parser, fixtures):
        """Parse: 至急対応お願いします。ログインボタンが反応しません。"""
        test_case = fixtures["test_cases"]["TC-TK03_asap"]
        result = parser.parse(test_case["input"])

        assert result.deadline_type == DeadlineType.TODAY
        assert result.task_type == TaskType.BUG
        assert result.priority == Priority.HIGH


class TestVagueParsing:
    """TC-TK04: Parse vague input with warning."""

    def test_parse_vague(self, parser, fixtures):
        """Parse: できれば早めにダッシュボードの改善をお願いしたいです"""
        test_case = fixtures["test_cases"]["TC-TK04_vague"]
        result = parser.parse(test_case["input"])

        assert result.deadline_type == DeadlineType.UNCLEAR
        assert result.task_type == TaskType.IMPROVEMENT
        assert result.priority == Priority.LOW
        assert "deadline_unclear" in result.warnings


class TestMultipleItemsParsing:
    """TC-TK05: Parse multiple items."""

    def test_parse_multiple_items(self, parser, fixtures):
        """Parse bullet list with 5 items."""
        test_case = fixtures["test_cases"]["TC-TK05_multiple_items"]
        results = parse_multiple_tasks(test_case["input"])

        assert len(results) == 5
        summaries = [r.summary for r in results]
        assert any("デザイン修正" in s for s in summaries)
        assert any("パスワードリセット" in s for s in summaries)


class TestEmailSourceParsing:
    """TC-TK07: Parse email source."""

    def test_parse_email(self, parser, fixtures):
        """Parse forwarded email."""
        test_case = fixtures["test_cases"]["TC-TK07_email_source"]
        result = parser.parse(test_case["input"], source_type="email")

        assert result.task_type == TaskType.BUG
        assert "Chrome 120" in result.description or "再現手順" in result.description


class TestChatSourceParsing:
    """TC-TK08: Parse chat/informal source."""

    def test_parse_chat(self, parser, fixtures):
        """Parse informal chat message."""
        test_case = fixtures["test_cases"]["TC-TK08_chat_source"]
        result = parser.parse(test_case["input"], source_type="chat")

        assert result.task_type == TaskType.QUESTION


class TestMinutesSourceParsing:
    """TC-TK09: Parse meeting minutes with 宿題."""

    def test_parse_minutes(self, parser, fixtures):
        """Parse meeting minutes with assigned tasks."""
        test_case = fixtures["test_cases"]["TC-TK09_minutes_source"]
        results = parse_multiple_tasks(test_case["input"], source_type="minutes")

        assert len(results) == 3

        # Check first task
        task1 = next((t for t in results if "田中" in (t.assignee_hint or "")), None)
        assert task1 is not None
        assert "仕様書" in task1.summary or "ログイン" in task1.summary


class TestMixedLanguageParsing:
    """TC-TK10: Parse mixed Japanese/English."""

    def test_parse_mixed(self, parser, fixtures):
        """Parse mixed JA/EN input."""
        test_case = fixtures["test_cases"]["TC-TK10_mixed_ja_en"]
        result = parser.parse(test_case["input"])

        assert result.task_type == TaskType.BUG


class TestSpecificDateParsing:
    """TC-TK11: Parse specific date."""

    def test_parse_specific_date(self, parser, fixtures):
        """Parse: 2026年2月15日までに"""
        test_case = fixtures["test_cases"]["TC-TK11_specific_date"]
        result = parser.parse(test_case["input"])

        assert result.deadline_type == DeadlineType.SPECIFIC
        assert result.deadline_date == date(2026, 2, 15)
        assert result.task_type == TaskType.FEATURE


class TestNextWeekDeadline:
    """TC-TK12: Parse next week deadline."""

    def test_parse_next_week(self, parser, fixtures):
        """Parse: 来週までに"""
        test_case = fixtures["test_cases"]["TC-TK12_next_week"]
        result = parser.parse(test_case["input"])

        assert result.deadline_type == DeadlineType.END_OF_NEXT_WEEK


class TestHighPriorityEmergency:
    """TC-TK13: Parse high priority emergency."""

    def test_parse_emergency(self, parser, fixtures):
        """Parse: 緊急：本番環境でデータが消失"""
        test_case = fixtures["test_cases"]["TC-TK13_high_priority_keywords"]
        result = parser.parse(test_case["input"])

        assert result.task_type == TaskType.BUG
        assert result.priority == Priority.HIGH
        assert result.deadline_type == DeadlineType.TODAY


class TestParsedTaskDataclass:
    """Test ParsedTask dataclass."""

    def test_to_dict(self):
        """Convert ParsedTask to dict."""
        task = ParsedTask(
            summary="Test task",
            task_type=TaskType.FEATURE,
            priority=Priority.NORMAL,
            deadline_type=DeadlineType.TOMORROW,
            deadline_date=date(2026, 1, 30),
            estimated_hours=8.0,
            assignee_hint="田中",
            description="Description here",
            warnings=[]
        )

        d = task.to_dict()
        assert d["summary"] == "Test task"
        assert d["task_type"] == "feature"
        assert d["priority"] == "normal"
        assert d["deadline_date"] == "2026-01-30"

    def test_to_markdown(self):
        """Generate markdown preview."""
        task = ParsedTask(
            summary="ログイン機能を実装",
            task_type=TaskType.FEATURE,
            priority=Priority.HIGH,
            deadline_type=DeadlineType.TOMORROW,
            deadline_date=date(2026, 1, 30),
            estimated_hours=8.0,
            assignee_hint="田中",
            description="実装内容の詳細",
            warnings=[]
        )

        md = task.to_markdown()
        assert "## Parsed Task" in md
        assert "ログイン機能を実装" in md
        assert "Feature" in md
        assert "High" in md
        assert "田中" in md
