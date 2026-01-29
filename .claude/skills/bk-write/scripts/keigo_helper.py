"""Keigo helper for Japanese business writing.

Handles 3 formality levels:
- casual (カジュアル): Internal, familiar colleagues
- polite (丁寧語): Standard business
- honorific (敬語): Client-facing, executives
"""

from enum import Enum


class KeigoLevel(Enum):
    """Japanese formality levels."""
    CASUAL = "casual"
    POLITE = "polite"
    HONORIFIC = "honorific"

    @classmethod
    def from_string(cls, value: str) -> "KeigoLevel":
        """Parse string to KeigoLevel."""
        value = value.lower().strip()
        for level in cls:
            if level.value == value:
                return level
        return cls.POLITE


# Verb conversion: casual -> {polite, honorific}
VERB_CONVERSIONS = {
    "する": {"polite": "します", "honorific": "いたします"},
    "行く": {"polite": "行きます", "honorific": "参ります"},
    "来る": {"polite": "来ます", "honorific": "参ります"},
    "いる": {"polite": "います", "honorific": "おります"},
    "見る": {"polite": "見ます", "honorific": "拝見します"},
    "言う": {"polite": "言います", "honorific": "申し上げます"},
    "聞く": {"polite": "聞きます", "honorific": "伺います"},
    "もらう": {"polite": "もらいます", "honorific": "いただきます"},
    "あげる": {"polite": "あげます", "honorific": "差し上げます"},
    "ある": {"polite": "あります", "honorific": "ございます"},
    "知る": {"polite": "知っています", "honorific": "存じております"},
    "思う": {"polite": "思います", "honorific": "存じます"},
    "食べる": {"polite": "食べます", "honorific": "いただきます"},
    "会う": {"polite": "会います", "honorific": "お目にかかります"},
}

GREETINGS = {
    KeigoLevel.CASUAL: [
        "お疲れ様です。",
        "お疲れ。",
    ],
    KeigoLevel.POLITE: [
        "お世話になっております。",
        "いつもお世話になっております。",
    ],
    KeigoLevel.HONORIFIC: [
        "いつも大変お世話になっております。",
        "平素より格別のお引き立てを賜り、誠にありがとうございます。",
    ],
}

CLOSINGS = {
    KeigoLevel.CASUAL: [
        "よろしくお願いします。",
        "よろしく。",
    ],
    KeigoLevel.POLITE: [
        "よろしくお願いいたします。",
        "ご確認のほど、よろしくお願いいたします。",
    ],
    KeigoLevel.HONORIFIC: [
        "何卒よろしくお願い申し上げます。",
        "ご査収のほど、何卒よろしくお願い申し上げます。",
    ],
}


class KeigoHelper:
    """Helper class for keigo conversions."""

    def __init__(self, default_level: KeigoLevel = KeigoLevel.POLITE):
        self.default_level = default_level

    def convert_verb(self, verb: str, level: KeigoLevel) -> str:
        """Convert casual verb to specified keigo level."""
        if level == KeigoLevel.CASUAL:
            return verb
        if verb not in VERB_CONVERSIONS:
            return verb
        return VERB_CONVERSIONS[verb].get(level.value, verb)

    def get_greeting(self, level: KeigoLevel, variant: int = 0) -> str:
        """Get greeting phrase for specified keigo level."""
        greetings = GREETINGS.get(level, GREETINGS[KeigoLevel.POLITE])
        idx = min(variant, len(greetings) - 1)
        return greetings[idx]

    def get_closing(self, level: KeigoLevel, variant: int = 0) -> str:
        """Get closing phrase for specified keigo level."""
        closings = CLOSINGS.get(level, CLOSINGS[KeigoLevel.POLITE])
        idx = min(variant, len(closings) - 1)
        return closings[idx]

    def format_recipient(self, name: str, level: KeigoLevel) -> str:
        """Format recipient name with appropriate suffix."""
        for suffix in ["様", "さん", "殿", "部長", "課長", "さま"]:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break
        if level == KeigoLevel.CASUAL:
            return f"{name}さん"
        return f"{name}様"
