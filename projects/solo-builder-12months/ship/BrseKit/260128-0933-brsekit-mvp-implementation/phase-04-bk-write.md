# Phase 4: bk-write - Japanese Business Writing

## Overview
- **Priority:** P2
- **Status:** pending
- **Skill:** `bk-write`
- **Approach:** TDD

## Pain Point
> "4 người làm file thiết kế, cách hành văn tiếng Nhật khác nhau"

## Input
```
/bk-write email-client --level=polite
/bk-write report-issue
/bk-write email-internal
```

## Expected Output
Template-based Japanese business document với consistent style.

## Key Test Cases
1. Generate client email với polite keigo
2. Generate internal email với casual tone
3. Apply same template → same output structure
4. Keigo level correct (casual/polite/honorific)

## Architecture
```
brsekit/skills/bk-write/
├── SKILL.md
├── scripts/
│   ├── japanese_writer.py
│   └── keigo_helper.py
├── templates/
│   ├── email-client-ja.json
│   ├── email-internal-ja.json
│   └── report-issue-ja.json
└── tests/
```

## Detailed plan: TBD after Phase 3 complete
