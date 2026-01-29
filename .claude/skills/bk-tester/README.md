# bk-tester

Generate professional Japanese test documentation from requirements using AI-powered analysis.

## Overview

This skill analyzes requirement documents and generates comprehensive Japanese test documentation following JSTQB standards. It outputs prompts that can be piped to Claude for generating high-quality test documents.

## Features

- Extract test viewpoints from requirements (functional, boundary, error, security, performance)
- Generate test plans (テスト計画書)
- Create test viewpoint tables (テスト観点表)
- Build detailed test cases (テストケース一覧)
- Generate test reports (テスト報告書)
- Output prompts for `claude -p` to generate content

## Installation

The skill is installed as part of the `.claude/skills` directory. Dependencies are managed via the shared virtual environment.

```bash
cd .claude/skills
pip install -r bk-tester/requirements.txt
```

## Usage

### Basic Commands

```bash
# Show all generation commands
python scripts/main.py --input requirements.md --type all

# Generate test plan
python scripts/main.py --input requirements.md --type plan

# Generate test viewpoints
python scripts/main.py --input requirements.md --type viewpoint

# Generate test cases
python scripts/main.py --input requirements.md --type cases

# Generate test report
python scripts/main.py --input requirements.md --type report
```

### With Claude Integration

Pipe the output to `claude -p` for AI-powered generation:

```bash
# Generate viewpoints
python scripts/main.py --input req.md --type viewpoint | claude -p > viewpoints.md

# Generate test plan with custom project name
python scripts/main.py --input req.md --type plan --project "認証システム" | claude -p > plan.md

# Generate test cases with viewpoints
python scripts/main.py --input req.md --type cases --viewpoints viewpoints.md | claude -p > cases.md

# Generate test report with results
python scripts/main.py --input req.md --type report --results results.md | claude -p > report.md
```

### Options

- `--input`, `-i`: Path to requirements document (required)
- `--type`, `-t`: Type of document to generate (required)
  - `all`: Show commands for all document types
  - `plan`: Test plan
  - `viewpoint`: Test viewpoints
  - `cases`: Test cases
  - `report`: Test report
- `--project`, `-p`: Project name (default: プロジェクト)
- `--viewpoints`, `-v`: Path to viewpoints document (for test cases generation)
- `--results`, `-r`: Path to test results (for report generation)

## Test Categories

The skill generates test cases across five categories:

1. **機能テスト (Functional)**: Core feature testing
2. **境界値テスト (Boundary)**: Boundary value testing
3. **異常系テスト (Error)**: Error handling testing
4. **セキュリティテスト (Security)**: Security testing
5. **性能テスト (Performance)**: Performance testing

## Output Documents

### Test Plan (テスト計画書)
- Test objectives and scope
- Test strategy (levels, types, methods)
- Test schedule
- Test environment
- Exit criteria
- Risks and mitigation
- Roles and responsibilities
- Deliverables

### Test Viewpoints (テスト観点表)
- Categorized test viewpoints
- Purpose and verification items
- Priority levels
- Coverage across all test categories

### Test Cases (テストケース一覧)
- Detailed test case tables
- Test case IDs, categories, items
- Prerequisites and test steps
- Expected results and priorities
- Markdown table format

### Test Report (テスト報告書)
- Executive summary
- Test execution overview
- Test case execution status
- Defect summary
- Test coverage metrics
- Quality evaluation
- Release decision
- Recommendations

## Examples

### Sample Requirements

```markdown
# ユーザー認証機能 要件定義

## REQ-001: ログイン機能
- メールアドレスとパスワードでログイン
- パスワードは8文字以上
- 3回失敗でロック
```

### Generated Viewpoint Example

```markdown
## 機能テスト

### FT-001: ログイン成功確認
- **目的**: 正しい認証情報でログインできることを確認
- **確認項目**: メールアドレスとパスワードでログイン可能
- **優先度**: 高

## 境界値テスト

### BT-001: パスワード最小文字数
- **目的**: パスワードの最小文字数制約を確認
- **確認項目**: 8文字未満のパスワードが拒否されること
- **優先度**: 中
```

## Testing

Run the test suite:

```bash
cd .claude/skills/bk-tester
python -m pytest tests/ -v
```

Test coverage:
- Viewpoint extraction: 7 tests
- Test case generation: 7 tests
- Test plan generation: 8 tests
- Test report generation: 10 tests
- Main entry point: 3 tests

Total: 35 tests

## Directory Structure

```
bk-tester/
├── SKILL.md                    # Skill metadata
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── scripts/
│   ├── __init__.py
│   ├── main.py                # Entry point
│   ├── viewpoint_extractor.py # Extract test viewpoints
│   ├── test_case_generator.py # Generate test cases
│   ├── test_plan_generator.py # Generate test plan
│   └── report_generator.py    # Generate test report
├── templates/
│   ├── test_plan_template.md
│   ├── viewpoint_template.md
│   ├── test_cases_template.md
│   └── test_report_template.md
└── tests/
    ├── __init__.py
    ├── test_main.py
    ├── test_viewpoint_extractor.py
    ├── test_test_case_generator.py
    ├── test_test_plan_generator.py
    ├── test_report_generator.py
    └── fixtures/
        └── sample_requirements.md
```

## Dependencies

- google-genai>=0.2.0
- python-dotenv>=1.0.0
- pytest>=8.0.0

## Notes

- Designed for Japanese test documentation
- Follows JSTQB standards
- Outputs prompts for AI generation (not final documents)
- UTF-8 encoding support for Windows
- Template-based output for consistency

## License

Part of the brse-workspace project.