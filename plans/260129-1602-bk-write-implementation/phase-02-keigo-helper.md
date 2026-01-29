---
phase: 2
title: "Keigo Helper Module"
status: pending
effort: 1.5h
---

# Phase 2: Keigo Helper Module

## Context Links

- Tests: `.claude/skills/bk-write/tests/test_keigo_helper.py`
- Pattern ref: `.claude/skills/bk-task/scripts/task_parser.py` (Enum, dataclass patterns)

## Overview

Implement keigo conversion logic. Module handles 3 levels: casual (カジュアル), polite (丁寧), honorific (敬語).

## Key Insights

- Japanese keigo has fixed conversion patterns for common verbs
- Greetings/closings are formulaic and can be templated
- Not attempting full NLP - focus on common business patterns

## Requirements

### Functional
- `KeigoLevel` enum with CASUAL, POLITE, HONORIFIC
- Verb conversion for common business verbs (する、見る、言う、もらう、etc.)
- Greeting generation by level
- Closing phrase generation by level

### Non-functional
- Pure Python, no external NLP dependencies
- All tests from Phase 1 pass

## Files to Create

```
.claude/skills/bk-write/scripts/
├── __init__.py
└── keigo_helper.py
```

## Implementation Steps

### 1. Create Scripts Directory (5 min)

```bash
mkdir -p .claude/skills/bk-write/scripts
touch .claude/skills/bk-write/scripts/__init__.py
```

### 2. Implement keigo_helper.py (60 min)

**File:** `scripts/keigo_helper.py`

```python
"""Keigo helper for Japanese business writing.

Handles 3 formality levels:
- casual (カジュアル): Internal, familiar colleagues
- polite (丁寧語): Standard business
- honorific (敬語): Client-facing, executives
"""

from enum import Enum
from typing import Optional


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
        # Default to polite for unknown values
        return cls.POLITE


# Verb conversion dictionary: casual -> {polite, honorific}
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

# Greetings by level
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

# Closings by level
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

# Connecting phrases
CONNECTORS = {
    KeigoLevel.CASUAL: {
        "therefore": "なので",
        "regarding": "について",
        "please": "お願い",
        "confirm": "確認",
    },
    KeigoLevel.POLITE: {
        "therefore": "つきましては",
        "regarding": "に関しまして",
        "please": "お願いいたします",
        "confirm": "ご確認ください",
    },
    KeigoLevel.HONORIFIC: {
        "therefore": "つきましては",
        "regarding": "に関しまして",
        "please": "お願い申し上げます",
        "confirm": "ご確認いただけますと幸いです",
    },
}


class KeigoHelper:
    """Helper class for keigo conversions."""

    def __init__(self, default_level: KeigoLevel = KeigoLevel.POLITE):
        self.default_level = default_level

    def convert_verb(self, verb: str, level: KeigoLevel) -> str:
        """Convert casual verb to specified keigo level.

        Args:
            verb: Casual form verb (e.g., "する")
            level: Target keigo level

        Returns:
            Converted verb form
        """
        if level == KeigoLevel.CASUAL:
            return verb

        if verb not in VERB_CONVERSIONS:
            # Return as-is if no conversion available
            return verb

        return VERB_CONVERSIONS[verb].get(level.value, verb)

    def get_greeting(self, level: KeigoLevel, variant: int = 0) -> str:
        """Get greeting phrase for specified keigo level.

        Args:
            level: Keigo level
            variant: Index of greeting variant (0 = default)

        Returns:
            Greeting phrase
        """
        greetings = GREETINGS.get(level, GREETINGS[KeigoLevel.POLITE])
        idx = min(variant, len(greetings) - 1)
        return greetings[idx]

    def get_closing(self, level: KeigoLevel, variant: int = 0) -> str:
        """Get closing phrase for specified keigo level.

        Args:
            level: Keigo level
            variant: Index of closing variant (0 = default)

        Returns:
            Closing phrase
        """
        closings = CLOSINGS.get(level, CLOSINGS[KeigoLevel.POLITE])
        idx = min(variant, len(closings) - 1)
        return closings[idx]

    def get_connector(self, key: str, level: KeigoLevel) -> str:
        """Get connecting phrase for specified keigo level.

        Args:
            key: Connector key (therefore, regarding, please, confirm)
            level: Keigo level

        Returns:
            Connecting phrase
        """
        connectors = CONNECTORS.get(level, CONNECTORS[KeigoLevel.POLITE])
        return connectors.get(key, "")

    def format_recipient(self, name: str, level: KeigoLevel) -> str:
        """Format recipient name with appropriate suffix.

        Args:
            name: Recipient name (may include suffix)
            level: Keigo level

        Returns:
            Formatted name with appropriate suffix
        """
        # Remove existing suffixes
        for suffix in ["様", "さん", "殿", "部長", "課長", "さま"]:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break

        # Add appropriate suffix
        if level == KeigoLevel.CASUAL:
            return f"{name}さん"
        elif level == KeigoLevel.POLITE:
            return f"{name}様"
        else:  # HONORIFIC
            return f"{name}様"


# Convenience functions
def convert_verb(verb: str, level: KeigoLevel) -> str:
    """Convert verb to specified keigo level."""
    return KeigoHelper().convert_verb(verb, level)


def get_greeting(level: KeigoLevel, variant: int = 0) -> str:
    """Get greeting for specified keigo level."""
    return KeigoHelper().get_greeting(level, variant)


def get_closing(level: KeigoLevel, variant: int = 0) -> str:
    """Get closing for specified keigo level."""
    return KeigoHelper().get_closing(level, variant)
```

### 3. Run Tests (10 min)

```bash
cd ".claude/skills/bk-write" && "../.venv/Scripts/python.exe" -m pytest tests/test_keigo_helper.py -v
```

Expected: All keigo helper tests pass.

## Todo List

- [ ] Create `scripts/__init__.py`
- [ ] Implement `scripts/keigo_helper.py`
- [ ] `KeigoLevel` enum with from_string()
- [ ] VERB_CONVERSIONS dictionary
- [ ] GREETINGS dictionary
- [ ] CLOSINGS dictionary
- [ ] `KeigoHelper.convert_verb()`
- [ ] `KeigoHelper.get_greeting()`
- [ ] `KeigoHelper.get_closing()`
- [ ] Run tests - all pass

## Success Criteria

- All `test_keigo_helper.py` tests pass
- Verb conversions accurate for common business verbs
- Greetings match expected patterns for each level

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Missing verb conversions | Start with core 10-15 verbs, expand later |
| Incorrect keigo forms | Validate with native speaker or reference |

## Next Phase

Phase 3: Implement `japanese_writer.py` using keigo_helper.
