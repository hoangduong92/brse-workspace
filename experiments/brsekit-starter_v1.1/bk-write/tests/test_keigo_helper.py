"""Tests for keigo_helper.py - TDD approach."""

import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from keigo_helper import KeigoLevel, KeigoHelper


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
