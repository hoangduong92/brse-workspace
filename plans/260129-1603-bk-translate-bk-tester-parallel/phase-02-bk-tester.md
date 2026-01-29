# Phase 2: bk-tester Implementation

## Overview
- **Priority:** P1
- **Status:** pending
- **Approach:** TDD
- **Directory:** `.claude/skills/bk-tester/`

## Purpose

Generate Japanese test documentation from requirements:
- テスト計画書 (Test Plan)
- テスト観点表 (Test Viewpoint Matrix)
- テストケース一覧 (Test Cases)
- テスト報告書 (Test Report)

## Architecture

```
.claude/skills/bk-tester/
├── SKILL.md
├── requirements.txt
├── .env.example
├── scripts/
│   ├── __init__.py
│   ├── main.py
│   ├── viewpoint_extractor.py
│   ├── test_case_generator.py
│   ├── test_plan_generator.py
│   └── report_generator.py
├── templates/
│   ├── test_plan_template.md
│   ├── viewpoint_template.md
│   ├── test_cases_template.md
│   └── test_report_template.md
└── tests/
    ├── __init__.py
    ├── test_viewpoint_extractor.py
    ├── test_case_generator.py
    └── fixtures/
        ├── sample_requirements.md
        ├── expected_viewpoint.md
        ├── expected_cases.md
        └── expected_plan.md
```

## Implementation Steps

### 1. Setup & Fixtures (TDD)
- [ ] Create directory structure
- [ ] Create sample_requirements.md fixture
- [ ] Create expected output fixtures
- [ ] Create templates
- [ ] Write failing tests

### 2. Viewpoint Extractor
- [ ] `ViewpointExtractor` class
  - `extract(requirements_text)` - Extract viewpoints
  - Map to Japanese categories:
    - 機能テスト (Functional)
    - 境界値テスト (Boundary)
    - 異常系テスト (Error)
    - セキュリティテスト (Security)
    - 性能テスト (Performance)
    - ユーザビリティ (Usability)
  - Return structured viewpoint list

### 3. Test Case Generator
- [ ] `TestCaseGenerator` class
  - `generate(viewpoints)` - Generate cases from viewpoints
  - Each case has:
    - ID (TC-001, TC-002, ...)
    - テスト観点 (Viewpoint category)
    - テスト項目 (Test item)
    - 前提条件 (Preconditions)
    - 手順 (Steps)
    - 期待結果 (Expected result)
    - 優先度 (Priority: High/Medium/Low)
  - Link to requirement ID for traceability

### 4. Test Plan Generator
- [ ] `TestPlanGenerator` class
  - `generate(requirements, viewpoints)` - Generate plan
  - Sections:
    - テスト概要 (Overview)
    - テスト範囲 (Scope)
    - テスト環境 (Environment)
    - テストスケジュール (Schedule - template)
    - リソース (Resources - template)
    - リスク (Risks)

### 5. Report Generator
- [ ] `ReportGenerator` class
  - `generate(test_cases, results)` - Generate report
  - Sections:
    - 実施概要 (Summary)
    - テスト結果 (Results: Pass/Fail stats)
    - 検出不具合 (Issues found)
    - 結論 (Conclusion)
  - Support empty results (template mode)

### 6. Main Entry Point
- [ ] CLI: `main.py --input requirements.md [--type all|plan|viewpoint|cases|report]`
- [ ] Output to `./test-docs/` directory

### 7. SKILL.md
- [ ] Usage documentation
- [ ] Commands: `/bk-tester`, subcommands

## Test Cases

| Test | Input | Expected |
|------|-------|----------|
| Extract viewpoints | Requirements with login feature | Functional, Security viewpoints |
| Generate cases | Viewpoint list | Test cases with ID, steps |
| Generate plan | Requirements | Structured plan document |
| Report template | Empty results | Template with placeholders |
| Japanese output | Any input | Japanese terminology correct |

## Templates

### viewpoint_template.md
```markdown
# テスト観点表

| No | 大分類 | 中分類 | テスト観点 | 要件ID |
|----|--------|--------|------------|--------|
| 1  | 機能テスト | ログイン | 正常系ログイン | REQ-001 |
```

### test_cases_template.md
```markdown
# テストケース一覧

| ID | テスト観点 | テスト項目 | 前提条件 | 手順 | 期待結果 | 優先度 |
|----|------------|------------|----------|------|----------|--------|
| TC-001 | 機能テスト | ログイン成功 | ユーザー登録済み | 1. IDを入力... | ダッシュボード表示 | High |
```

### test_plan_template.md
```markdown
# テスト計画書

## 1. テスト概要
{overview}

## 2. テスト範囲
### 2.1 対象範囲
{in_scope}

### 2.2 対象外
{out_scope}

## 3. テスト環境
{environment}

## 4. テストスケジュール
| フェーズ | 開始日 | 終了日 | 担当 |
|----------|--------|--------|------|

## 5. リスク
{risks}
```

### test_report_template.md
```markdown
# テスト報告書

## 1. 実施概要
- 実施期間: {period}
- 対象: {target}

## 2. テスト結果サマリー
| 項目 | 件数 |
|------|------|
| 総テストケース数 | {total} |
| 成功 | {passed} |
| 失敗 | {failed} |
| 未実施 | {not_run} |

## 3. 検出不具合
| No | 内容 | 重要度 | ステータス |
|----|------|--------|------------|

## 4. 結論
{conclusion}
```

## Sample Requirements Fixture

```markdown
# ユーザー認証機能 要件定義

## REQ-001: ログイン機能
- ユーザーはメールアドレスとパスワードでログインできる
- パスワードは8文字以上必須
- 3回連続失敗でアカウントロック

## REQ-002: ログアウト機能
- ログアウトボタンでセッション終了
- ログアウト後はログイン画面にリダイレクト

## REQ-003: パスワードリセット
- メールアドレスでパスワードリセット依頼可能
- リセットリンクは24時間有効
```

## Dependencies

- No external APIs required
- Claude prompting for intelligent extraction
- Templates in Markdown format

## Viewpoint Extraction Strategy

Use Claude to:
1. Parse requirements text
2. Identify testable items
3. Categorize into test types
4. Generate structured viewpoint list

Prompt pattern:
```
以下の要件から、テスト観点を抽出してください。
カテゴリ: 機能テスト、境界値テスト、異常系テスト、セキュリティテスト

要件:
{requirements}

出力形式:
- カテゴリ: ...
- 要件ID: ...
- テスト観点: ...
```

## Success Criteria

- [ ] Viewpoint extraction works
- [ ] Test cases generated with proper structure
- [ ] Test plan follows template
- [ ] Report template ready
- [ ] Japanese terminology correct
- [ ] Traceability: requirement → viewpoint → case
- [ ] All tests pass
