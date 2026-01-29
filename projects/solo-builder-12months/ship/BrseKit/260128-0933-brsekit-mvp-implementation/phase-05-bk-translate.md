# Phase 5: bk-translate - JA↔VI Translation

## Overview
- **Priority:** P2
- **Status:** pending
- **Skill:** `bk-translate`
- **Approach:** TDD

## Pain Point
> "Tốn thời gian hiểu nội dung dev nói (queue, instance, routing)"

## Input
```
/bk-translate "機能テストを実施しました"
/bk-glossary add
/bk-glossary list
```

## Expected Output
- Translation với technical terms preserved
- Glossary management

## Key Test Cases
1. Translate JA→VI với glossary lookup
2. Translate VI→JA
3. Preserve code blocks, URLs, technical terms
4. Add/list/remove glossary terms

## Architecture
```
brsekit/skills/bk-translate/
├── SKILL.md
├── scripts/
│   ├── translator.py
│   └── glossary_manager.py
├── glossaries/
│   └── default-it-terms.json
└── tests/
```

## Detailed plan: TBD after Phase 4 complete
