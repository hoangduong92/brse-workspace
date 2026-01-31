---
name: bk-tester
description: "[DEPRECATED] Use /bk-spec test instead. Test documentation generation."
deprecated: true
redirect: bk-spec test
---

> ⚠️ **DEPRECATED**: This skill is deprecated. Use `/bk-spec test` instead.

## Migration Guide

| Old Command | New Command |
|------------|-------------|
| `/bk-tester --input req.md --type all` | `/bk-spec test --input req.md --type all` |
| `/bk-tester --input req.md --type plan` | `/bk-spec test --input req.md --type plan` |
| `/bk-tester --input req.md --type viewpoint` | `/bk-spec test --input req.md --type viewpoint` |
| `/bk-tester --input req.md --type cases` | `/bk-spec test --input req.md --type cases` |

## Why Deprecated?

bk-tester has been merged into bk-spec for a unified specification and testing experience. All functionality is preserved in the new skill.

---

# bk-tester

Generate professional Japanese test documentation (test plans, viewpoint tables, test cases, test reports) from requirements using AI-powered analysis.

## Overview

This skill analyzes requirement documents and generates comprehensive Japanese test documentation following JSTQB standards. It uses Claude prompts to extract test viewpoints and generate test cases automatically.

## Key Features

- Extract test viewpoints from requirements (functional, boundary, error, security, performance)
- Generate test plans (テスト計画書)
- Create test viewpoint tables (テスト観点表)
- Build detailed test cases (テストケース一覧)
- Generate test reports (テスト報告書)
- Output prompts for `claude -p` to generate content

## Usage

```bash
# Generate all test documents
python scripts/main.py --input requirements.md --type all

# Generate specific document types
python scripts/main.py --input requirements.md --type plan
python scripts/main.py --input requirements.md --type viewpoint
python scripts/main.py --input requirements.md --type cases
python scripts/main.py --input requirements.md --type report
```

## Output

The skill outputs prompts that can be piped to `claude -p` for generating documentation:

```bash
python scripts/main.py --input req.md --type viewpoint | claude -p > viewpoint.md
```

## Test Categories

- **機能テスト (Functional)**: Core feature testing
- **境界値テスト (Boundary)**: Boundary value testing
- **異常系テスト (Error)**: Error handling testing
- **セキュリティテスト (Security)**: Security testing
- **性能テスト (Performance)**: Performance testing

## Dependencies

- google-genai>=0.2.0
- python-dotenv>=1.0.0
- pytest>=8.0.0

## Directory Structure

```
bk-tester/
├── SKILL.md
├── requirements.txt
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
    └── fixtures/
        └── sample_requirements.md
```
