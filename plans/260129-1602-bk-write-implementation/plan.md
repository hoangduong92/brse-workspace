---
title: "bk-write - Japanese Business Writing Skill"
description: "Template-based Japanese business document generator with consistent keigo levels"
status: pending
priority: P2
effort: 8h
branch: main
tags: [bk-write, japanese, keigo, templates, brsekit]
created: 2026-01-29
---

# bk-write - Japanese Business Writing

## Pain Point
> "4 nguoi lam file thiet ke, cach hanh van tieng Nhat khac nhau"

Inconsistent Japanese business writing style across team members.

## Phases

| Phase | Description | Effort | Status |
|-------|-------------|--------|--------|
| [Phase 1](./phase-01-tdd-test-setup.md) | TDD test fixtures & test cases | 1.5h | pending |
| [Phase 2](./phase-02-keigo-helper.md) | Keigo helper module | 1.5h | pending |
| [Phase 3](./phase-03-japanese-writer.md) | Japanese writer core module | 2h | pending |
| [Phase 4](./phase-04-templates.md) | JSON templates for document types | 1.5h | pending |
| [Phase 5](./phase-05-skill-integration.md) | SKILL.md & main.py integration | 1.5h | pending |

## Architecture

```
.claude/skills/bk-write/
├── SKILL.md                          # Skill definition
├── .env.example                      # Environment template
├── requirements.txt                  # Dependencies
├── scripts/
│   ├── __init__.py
│   ├── main.py                       # Entry point
│   ├── keigo_helper.py               # Keigo level conversion
│   └── japanese_writer.py            # Document generation
├── templates/
│   ├── email-client-ja.json          # Client email template
│   ├── email-internal-ja.json        # Internal email template
│   ├── report-issue-ja.json          # Issue report template
│   └── design-doc-ja.json            # Design document template
└── tests/
    ├── __init__.py
    ├── fixtures/
    │   └── sample_inputs.json        # Test fixtures
    ├── test_keigo_helper.py          # Keigo helper tests
    └── test_japanese_writer.py       # Writer tests
```

## Key Features

1. **3 Keigo Levels**: casual, polite, honorific
2. **4 Document Types**: email-client, email-internal, report-issue, design-doc
3. **JSON Templates**: Easy customization without code changes
4. **TDD Approach**: Tests first, implementation follows

## Success Criteria

- [ ] Same template + same input = same output structure
- [ ] Keigo conversion accurate (casual/polite/honorific)
- [ ] All tests pass
- [ ] SKILL.md follows existing pattern (bk-task, bk-status)

## Dependencies

- Follows patterns from: `bk-task/`, `bk-status/`, `bk-report/`
- Python venv: `.claude/skills/.venv/`
