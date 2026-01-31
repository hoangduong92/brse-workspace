---
name: bk-spec
description: Requirement analysis and test document generation. Use when analyzing specs, generating test plans, viewpoint tables, or test cases.
argument-hint: "<analyze|test|feature> <file or text> [--type viewpoint|cases|plan|all]"
---

# bk-spec

Unified spec skill - requirement analysis and test document generation. Queries bk-recall for context enrichment.

## Usage

```bash
# Analyze requirements
/bk-spec analyze requirements.md
/bk-spec analyze "ログイン機能の仕様"

# Generate test documents
/bk-spec test requirements.md
/bk-spec test --type viewpoint  # Viewpoint table only
/bk-spec test --type cases      # Test cases only
/bk-spec test --type plan       # Test plan only
/bk-spec test --type all        # All documents

# Feature-specific analysis
/bk-spec feature "user authentication"
```

## Features

- Requirement analysis with clarifying questions
- User story generation
- Gap detection (missing requirements)
- Test plan generation (JSTQB standard)
- Viewpoint table creation
- Test case generation
- Context enrichment via bk-recall

## Output Format

All outputs follow Japanese testing standards:
- テスト計画書 (Test Plan)
- 観点表 (Viewpoint Table)
- テストケース (Test Cases)
- テスト結果報告書 (Test Report)

## Migration

```bash
# Old: /bk-tester requirements.md
# New: /bk-spec test requirements.md
```
