# Phase 9: bk-tester

## Overview

| Attribute | Value |
|-----------|-------|
| **Priority** | P1 |
| **Status** | pending |
| **Depends on** | bk-analyze (input source) |
| **Description** | Generate test documentation từ requirements |

## Purpose

Create formal test documents (テスト計画書, テスト観点表, テストケース, テスト報告書) commonly required by Japan customers.

## Input Sources

| Source | Description |
|--------|-------------|
| Requirements doc | Direct input (Markdown, text) |
| bk-analyze output | Refined specs, user stories |
| Backlog issues | Issues từ project |

## Output Documents (MVP = Markdown)

| Document | Japanese | Structure |
|----------|----------|-----------|
| Test Plan | テスト計画書 | Scope, schedule, resources, environments, risks |
| Test Viewpoint | テスト観点表 | Viewpoint matrix - functional, non-functional, boundary |
| Test Cases | テストケース一覧 | ID, viewpoint, steps, expected result, priority |
| Test Report | テスト報告書 | Execution summary, pass/fail stats, issues found |

**Post-MVP:** Excel export với 3-4 sheets (common format in Japan)

## Commands

| Command | Description |
|---------|-------------|
| `/bk-tester <input>` | Generate all test docs từ input |
| `/bk-tester plan` | Generate test plan only |
| `/bk-tester viewpoint` | Generate viewpoint matrix only |
| `/bk-tester cases` | Generate test cases only |
| `/bk-tester report` | Generate test report template |

## Test Viewpoint Categories

| Category | Japanese | Examples |
|----------|----------|----------|
| Functional | 機能テスト | Input/output validation, business rules |
| Boundary | 境界値テスト | Min/max values, edge cases |
| Error | 異常系テスト | Invalid input, error handling |
| Security | セキュリティテスト | Auth, injection, XSS |
| Performance | 性能テスト | Load, response time |
| Usability | ユーザビリティ | UI/UX, accessibility |

## Architecture

```
bk-tester/
├── SKILL.md
├── scripts/
│   ├── main.py
│   ├── test_plan_generator.py
│   ├── viewpoint_extractor.py
│   ├── test_case_generator.py
│   └── report_generator.py
├── templates/
│   ├── test_plan_template.md
│   ├── viewpoint_template.md
│   ├── test_cases_template.md
│   └── test_report_template.md
└── tests/
    ├── test_viewpoint_extractor.py
    ├── test_case_generator.py
    └── fixtures/
        ├── sample_requirements.md
        ├── expected_viewpoint.md
        └── expected_cases.md
```

## Implementation Steps

### 1. Setup & Templates (TDD)
- [ ] Create skill folder structure
- [ ] Define test fixtures (sample requirements, expected outputs)
- [ ] Create base templates

### 2. Viewpoint Extractor
- [ ] Write tests for viewpoint extraction
- [ ] Implement extraction từ requirements
- [ ] Map to Japanese categories (機能, 境界値, 異常系, etc.)

### 3. Test Case Generator
- [ ] Write tests for case generation
- [ ] Generate cases từ viewpoints
- [ ] Include: ID, category, steps, expected result, priority

### 4. Test Plan Generator
- [ ] Write tests for plan structure
- [ ] Generate scope, schedule, resources sections
- [ ] Include risk assessment

### 5. Test Report Template
- [ ] Create report template
- [ ] Support manual entry of execution results
- [ ] Generate summary stats

### 6. Integration
- [ ] Link với bk-analyze output
- [ ] Traceability: requirement → viewpoint → case
- [ ] SKILL.md documentation

## Success Criteria

| Criteria | Description |
|----------|-------------|
| Viewpoint extraction | Extract relevant viewpoints từ requirements |
| Japanese output | Correct Japanese terminology (テスト観点, テストケース) |
| Traceability | Each test case links to requirement |
| Template compliance | Output matches common Japan test doc format |
| MVP format | Markdown tables (Excel deferred) |

## Test Fixtures

| Fixture | Purpose |
|---------|---------|
| `sample_requirements.md` | Input requirements for testing |
| `expected_viewpoint.md` | Expected viewpoint matrix |
| `expected_cases.md` | Expected test cases output |
| `expected_plan.md` | Expected test plan |

## Dependencies

- `bk-analyze` output (optional but recommended)
- Requirements document (required)
- Project context từ `bk-init`

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Viewpoint coverage gaps | Medium | Use standard checklist as base |
| Japanese terminology errors | Low | Review by native speaker |
| Over-generation | Medium | Allow user to select categories |

## Notes

- Japan customers often expect Excel format → Post-MVP feature
- テスト観点表 format varies by company → Provide customizable template
- Link với Backlog issues for traceability (future)
