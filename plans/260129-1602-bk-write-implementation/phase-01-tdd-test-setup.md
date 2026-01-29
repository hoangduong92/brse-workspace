---
phase: 1
title: "TDD Test Setup"
status: pending
effort: 1.5h
---

# Phase 1: TDD Test Fixtures & Test Cases

## Context Links

- Pattern ref: `.claude/skills/bk-task/tests/test_task_parser.py`
- Fixtures ref: `.claude/skills/bk-task/tests/fixtures/sample_inputs.json`

## Overview

Setup test infrastructure before implementation. Write failing tests that define expected behavior.

## Key Insights

- Follow `bk-task` test patterns: pytest fixtures, JSON test data
- Test keigo conversion accuracy with real Japanese examples
- Test template rendering produces consistent output

## Requirements

### Functional
- Test fixtures in JSON format
- Test cases cover all keigo levels (casual/polite/honorific)
- Test cases cover all document types (email-client, email-internal, report-issue, design-doc)

### Non-functional
- Tests run in <5s total
- No external dependencies in tests (mock data only)

## Files to Create

```
.claude/skills/bk-write/
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   └── sample_inputs.json
│   ├── test_keigo_helper.py
│   └── test_japanese_writer.py
```

## Implementation Steps

### 1. Create Directory Structure (5 min)
```bash
mkdir -p .claude/skills/bk-write/tests/fixtures
touch .claude/skills/bk-write/tests/__init__.py
```

### 2. Create Test Fixtures (30 min)

**File:** `tests/fixtures/sample_inputs.json`

```json
{
  "keigo_conversions": {
    "casual_to_polite": [
      {"casual": "する", "polite": "します", "honorific": "いたします"},
      {"casual": "行く", "polite": "行きます", "honorific": "参ります"},
      {"casual": "見る", "polite": "見ます", "honorific": "拝見します"},
      {"casual": "言う", "polite": "言います", "honorific": "申し上げます"},
      {"casual": "もらう", "polite": "もらいます", "honorific": "いただきます"},
      {"casual": "ある", "polite": "あります", "honorific": "ございます"}
    ],
    "greetings": {
      "casual": "お疲れ",
      "polite": "お疲れ様です",
      "honorific": "いつもお世話になっております"
    },
    "closings": {
      "casual": "よろしく",
      "polite": "よろしくお願いします",
      "honorific": "何卒よろしくお願い申し上げます"
    }
  },
  "test_cases": {
    "TC-BW01_email_client_polite": {
      "input": {
        "doc_type": "email-client",
        "level": "polite",
        "recipient": "田中様",
        "subject": "プロジェクト進捗報告",
        "content_points": ["設計完了", "開発開始予定"]
      },
      "expected": {
        "has_greeting": true,
        "greeting_contains": "お世話になっております",
        "has_closing": true,
        "closing_contains": "よろしくお願いいたします"
      }
    },
    "TC-BW02_email_client_honorific": {
      "input": {
        "doc_type": "email-client",
        "level": "honorific",
        "recipient": "山田部長",
        "subject": "ご報告"
      },
      "expected": {
        "greeting_contains": "いつも大変お世話になっております",
        "closing_contains": "何卒よろしくお願い申し上げます"
      }
    },
    "TC-BW03_email_internal_casual": {
      "input": {
        "doc_type": "email-internal",
        "level": "casual",
        "recipient": "佐藤さん",
        "subject": "MTG確認"
      },
      "expected": {
        "greeting_contains": "お疲れ様",
        "closing_contains": "よろしく"
      }
    },
    "TC-BW04_report_issue_polite": {
      "input": {
        "doc_type": "report-issue",
        "level": "polite",
        "issue_title": "ログイン不具合",
        "environment": "本番環境",
        "steps": ["トップページアクセス", "ログインボタンクリック"]
      },
      "expected": {
        "has_sections": ["概要", "環境", "再現手順", "期待動作", "実際の動作"]
      }
    },
    "TC-BW05_design_doc_polite": {
      "input": {
        "doc_type": "design-doc",
        "level": "polite",
        "feature_name": "ユーザー認証機能",
        "overview": "OAuth2.0による認証"
      },
      "expected": {
        "has_sections": ["概要", "仕様", "技術構成", "スケジュール"]
      }
    },
    "TC-BW06_same_template_consistency": {
      "input_1": {
        "doc_type": "email-client",
        "level": "polite",
        "recipient": "A様",
        "subject": "テスト"
      },
      "input_2": {
        "doc_type": "email-client",
        "level": "polite",
        "recipient": "B様",
        "subject": "別のテスト"
      },
      "expected": "Same structure, different content placeholders"
    }
  }
}
```

### 3. Create Keigo Helper Tests (25 min)

**File:** `tests/test_keigo_helper.py`

```python
"""Tests for keigo_helper.py - TDD approach."""

import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Will fail until keigo_helper.py is implemented
from keigo_helper import (
    KeigoLevel,
    KeigoHelper,
    convert_verb,
    get_greeting,
    get_closing,
)


@pytest.fixture
def fixtures():
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_inputs.json"
    with open(fixtures_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def helper():
    return KeigoHelper()


class TestKeigoLevel:
    """Test KeigoLevel enum."""

    def test_levels_exist(self):
        assert KeigoLevel.CASUAL.value == "casual"
        assert KeigoLevel.POLITE.value == "polite"
        assert KeigoLevel.HONORIFIC.value == "honorific"

    def test_from_string(self):
        assert KeigoLevel.from_string("casual") == KeigoLevel.CASUAL
        assert KeigoLevel.from_string("polite") == KeigoLevel.POLITE
        assert KeigoLevel.from_string("honorific") == KeigoLevel.HONORIFIC


class TestVerbConversion:
    """Test verb keigo conversion."""

    def test_suru_to_polite(self, helper):
        assert helper.convert_verb("する", KeigoLevel.POLITE) == "します"

    def test_suru_to_honorific(self, helper):
        assert helper.convert_verb("する", KeigoLevel.HONORIFIC) == "いたします"

    def test_miru_to_honorific(self, helper):
        assert helper.convert_verb("見る", KeigoLevel.HONORIFIC) == "拝見します"

    def test_morau_to_honorific(self, helper):
        assert helper.convert_verb("もらう", KeigoLevel.HONORIFIC) == "いただきます"


class TestGreetings:
    """Test greeting generation by keigo level."""

    def test_casual_greeting(self, helper):
        result = helper.get_greeting(KeigoLevel.CASUAL)
        assert "お疲れ" in result

    def test_polite_greeting(self, helper):
        result = helper.get_greeting(KeigoLevel.POLITE)
        assert "お世話になっております" in result

    def test_honorific_greeting(self, helper):
        result = helper.get_greeting(KeigoLevel.HONORIFIC)
        assert "大変お世話になっております" in result


class TestClosings:
    """Test closing phrase generation by keigo level."""

    def test_casual_closing(self, helper):
        result = helper.get_closing(KeigoLevel.CASUAL)
        assert "よろしく" in result

    def test_polite_closing(self, helper):
        result = helper.get_closing(KeigoLevel.POLITE)
        assert "よろしくお願いします" in result or "よろしくお願いいたします" in result

    def test_honorific_closing(self, helper):
        result = helper.get_closing(KeigoLevel.HONORIFIC)
        assert "何卒" in result
        assert "申し上げます" in result
```

### 4. Create Japanese Writer Tests (25 min)

**File:** `tests/test_japanese_writer.py`

```python
"""Tests for japanese_writer.py - TDD approach."""

import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from japanese_writer import (
    JapaneseWriter,
    DocumentType,
    generate_document,
)
from keigo_helper import KeigoLevel


@pytest.fixture
def fixtures():
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_inputs.json"
    with open(fixtures_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def writer():
    return JapaneseWriter()


class TestDocumentType:
    """Test DocumentType enum."""

    def test_types_exist(self):
        assert DocumentType.EMAIL_CLIENT.value == "email-client"
        assert DocumentType.EMAIL_INTERNAL.value == "email-internal"
        assert DocumentType.REPORT_ISSUE.value == "report-issue"
        assert DocumentType.DESIGN_DOC.value == "design-doc"


class TestEmailClientGeneration:
    """TC-BW01, TC-BW02: Email client document tests."""

    def test_polite_email_client(self, writer, fixtures):
        tc = fixtures["test_cases"]["TC-BW01_email_client_polite"]
        result = writer.generate(
            doc_type=DocumentType.EMAIL_CLIENT,
            level=KeigoLevel.POLITE,
            recipient=tc["input"]["recipient"],
            subject=tc["input"]["subject"],
            content_points=tc["input"]["content_points"]
        )

        assert tc["expected"]["greeting_contains"] in result
        assert tc["expected"]["closing_contains"] in result

    def test_honorific_email_client(self, writer, fixtures):
        tc = fixtures["test_cases"]["TC-BW02_email_client_honorific"]
        result = writer.generate(
            doc_type=DocumentType.EMAIL_CLIENT,
            level=KeigoLevel.HONORIFIC,
            recipient=tc["input"]["recipient"],
            subject=tc["input"]["subject"]
        )

        assert tc["expected"]["greeting_contains"] in result
        assert tc["expected"]["closing_contains"] in result


class TestEmailInternalGeneration:
    """TC-BW03: Email internal document tests."""

    def test_casual_email_internal(self, writer, fixtures):
        tc = fixtures["test_cases"]["TC-BW03_email_internal_casual"]
        result = writer.generate(
            doc_type=DocumentType.EMAIL_INTERNAL,
            level=KeigoLevel.CASUAL,
            recipient=tc["input"]["recipient"],
            subject=tc["input"]["subject"]
        )

        assert tc["expected"]["greeting_contains"] in result
        assert tc["expected"]["closing_contains"] in result


class TestReportIssueGeneration:
    """TC-BW04: Issue report document tests."""

    def test_polite_report_issue(self, writer, fixtures):
        tc = fixtures["test_cases"]["TC-BW04_report_issue_polite"]
        result = writer.generate(
            doc_type=DocumentType.REPORT_ISSUE,
            level=KeigoLevel.POLITE,
            issue_title=tc["input"]["issue_title"],
            environment=tc["input"]["environment"],
            steps=tc["input"]["steps"]
        )

        for section in tc["expected"]["has_sections"]:
            assert section in result


class TestDesignDocGeneration:
    """TC-BW05: Design document tests."""

    def test_polite_design_doc(self, writer, fixtures):
        tc = fixtures["test_cases"]["TC-BW05_design_doc_polite"]
        result = writer.generate(
            doc_type=DocumentType.DESIGN_DOC,
            level=KeigoLevel.POLITE,
            feature_name=tc["input"]["feature_name"],
            overview=tc["input"]["overview"]
        )

        for section in tc["expected"]["has_sections"]:
            assert section in result


class TestOutputConsistency:
    """TC-BW06: Same template produces consistent structure."""

    def test_same_template_same_structure(self, writer, fixtures):
        tc = fixtures["test_cases"]["TC-BW06_same_template_consistency"]

        result_1 = writer.generate(
            doc_type=DocumentType.EMAIL_CLIENT,
            level=KeigoLevel.POLITE,
            recipient=tc["input_1"]["recipient"],
            subject=tc["input_1"]["subject"]
        )

        result_2 = writer.generate(
            doc_type=DocumentType.EMAIL_CLIENT,
            level=KeigoLevel.POLITE,
            recipient=tc["input_2"]["recipient"],
            subject=tc["input_2"]["subject"]
        )

        # Extract structure (section headers)
        def extract_structure(text):
            import re
            return re.findall(r'^#+\s+.+$|^-{3,}$', text, re.MULTILINE)

        struct_1 = extract_structure(result_1)
        struct_2 = extract_structure(result_2)

        assert len(struct_1) == len(struct_2)
```

## Todo List

- [ ] Create directory structure
- [ ] Create `tests/__init__.py`
- [ ] Create `tests/fixtures/sample_inputs.json`
- [ ] Create `tests/test_keigo_helper.py` (will fail)
- [ ] Create `tests/test_japanese_writer.py` (will fail)
- [ ] Verify tests fail with ImportError (expected)

## Success Criteria

- Directory structure created
- Test fixtures contain all test cases
- Tests run and fail with ImportError (modules not yet implemented)

## Run Command

```bash
cd ".claude/skills/bk-write" && "../.venv/Scripts/python.exe" -m pytest tests/ -v
```

Expected: Tests fail with `ModuleNotFoundError: No module named 'keigo_helper'`

## Next Phase

Phase 2: Implement `keigo_helper.py` to make keigo tests pass.
