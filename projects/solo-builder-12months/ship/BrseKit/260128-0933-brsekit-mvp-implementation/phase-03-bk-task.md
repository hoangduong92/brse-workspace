# Phase 3: bk-task - Create Task từ Unstructured Input

## Overview
- **Priority:** P1
- **Status:** pending
- **Skill:** `bk-task`
- **Approach:** TDD

## Pain Point
> "Tạo task với input unstructured từ khách hàng tốn effort parse và structure"

## Input
```
/bk-task
```
Then paste customer message (Japanese unstructured text)

## Expected Output
```markdown
## Parsed Task

**Summary:** ログイン機能の不具合修正
**Type:** Bug
**Priority:** High
**Description:**
- 現象: ログインボタンが反応しない
- 環境: Chrome 120
- 再現手順: 1. トップページ → 2. ログインクリック

**Create on Backlog?** [Yes] [No] [Edit first]
```

## Key Test Cases
1. Parse Japanese customer email → structured task
2. Detect task type (bug/feature/question)
3. Extract priority keywords
4. Generate Backlog-ready format

## Architecture
```
brsekit/skills/bk-task/
├── SKILL.md
├── scripts/
│   ├── task_parser.py
│   └── task_creator.py
└── tests/
    └── test_task_parser.py
```

## Dependencies
- `lib/backlog_client.py` for creating tasks
- `lib/language_detector.py` for JP detection

## Detailed plan: TBD after Phase 2 complete
