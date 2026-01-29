"""Tests for japanese_writer.py - TDD approach."""

import json
import re
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from japanese_writer import JapaneseWriter, DocumentType
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
            steps=tc["input"]["steps"],
            expected_behavior=tc["input"]["expected_behavior"],
            actual_behavior=tc["input"]["actual_behavior"]
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
            overview=tc["input"]["overview"],
            tech_stack=tc["input"]["tech_stack"],
            schedule=tc["input"]["schedule"]
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

        def extract_structure(text):
            return re.findall(r'^#+\s+.+$|^-{3,}$', text, re.MULTILINE)

        struct_1 = extract_structure(result_1)
        struct_2 = extract_structure(result_2)
        assert len(struct_1) == len(struct_2)
