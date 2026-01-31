# Phase 4: bk-spec (Merge analyze + tester)

## Context Links
- [bk-tester SKILL.md](c:/Users/duongbibo/brse-workspace/.claude/skills/bk-tester/SKILL.md)
- [Phase 1: bk-recall](./phase-01-bk-recall.md)
- [Original Plan - bk-analyze](c:/Users/duongbibo/brse-workspace/projects/solo-builder-12months/ship/BrseKit/260128-0933-brsekit-mvp-implementation/plan.md)

## Overview
- **Priority:** P1
- **Status:** 100% complete (modules + tests done)
- **Effort:** 3h
- **Description:** Merge bk-analyze (BA assistant) and bk-tester; query bk-recall for context

## Key Insights
- bk-analyze: Requirement analysis, user stories, questions, specs
- bk-tester: Test plan, viewpoint table, test cases, test report
- Natural flow: analyze → spec → test (bk-spec covers all)
- New: Query bk-recall for project context enrichment

## Requirements

### Functional
- `/bk-spec analyze <input>` - Requirement analysis (questions, user stories)
- `/bk-spec test <input>` - Generate test docs (plan, viewpoint, cases, report)
- `/bk-spec feature "<desc>"` - Feature-specific analysis
- Auto-query bk-recall for context enrichment

### Non-Functional
- Japanese output following JSTQB standards
- Context retrieval <500ms
- Same output quality as bk-tester

## Architecture

```
.claude/skills/bk-spec/
├── SKILL.md
├── requirements.txt
├── scripts/
│   ├── main.py                  # CLI router
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── requirements_analyzer.py
│   │   ├── user_story_generator.py
│   │   └── gap_detector.py
│   ├── tester/
│   │   ├── __init__.py
│   │   ├── viewpoint_extractor.py    # From bk-tester
│   │   ├── test_case_generator.py    # From bk-tester
│   │   ├── test_plan_generator.py    # From bk-tester
│   │   └── report_generator.py       # From bk-tester
│   ├── context_enricher.py      # Query bk-recall
│   └── prompt_builder.py        # Build Claude prompts
├── templates/
│   ├── test_plan_template.md
│   ├── viewpoint_template.md
│   ├── test_cases_template.md
│   └── test_report_template.md
└── tests/
    ├── test_analyzer.py
    └── test_tester.py
```

### Data Flow with Context
```
User: /bk-spec test requirements.md
         ↓
    main.py (parse command)
         ↓
    context_enricher.py → bk-recall search ← NEW
         ↓
    tester/viewpoint_extractor.py + context
         ↓
    tester/test_case_generator.py
         ↓
    Output: Test docs with enriched context
```

## Related Code Files

### Create
- `.claude/skills/bk-spec/SKILL.md`
- `.claude/skills/bk-spec/requirements.txt`
- `.claude/skills/bk-spec/scripts/main.py`
- `.claude/skills/bk-spec/scripts/analyzer/__init__.py`
- `.claude/skills/bk-spec/scripts/analyzer/requirements_analyzer.py`
- `.claude/skills/bk-spec/scripts/analyzer/user_story_generator.py`
- `.claude/skills/bk-spec/scripts/analyzer/gap_detector.py`
- `.claude/skills/bk-spec/scripts/context_enricher.py`
- `.claude/skills/bk-spec/scripts/prompt_builder.py`

### Move/Refactor
- `.claude/skills/bk-tester/scripts/viewpoint_extractor.py` → `.claude/skills/bk-spec/scripts/tester/`
- `.claude/skills/bk-tester/scripts/test_case_generator.py` → `.claude/skills/bk-spec/scripts/tester/`
- `.claude/skills/bk-tester/scripts/test_plan_generator.py` → `.claude/skills/bk-spec/scripts/tester/`
- `.claude/skills/bk-tester/scripts/report_generator.py` → `.claude/skills/bk-spec/scripts/tester/`
- `.claude/skills/bk-tester/templates/*` → `.claude/skills/bk-spec/templates/`

### Reuse
- `.claude/skills/bk-recall/` (context search)
- `.claude/skills/common/backlog/client.py`

### Delete (after alias layer)
- `.claude/skills/bk-tester/` (Phase 6)

## Implementation Steps

1. **Create bk-spec skill structure**
   - Create directories
   - Write SKILL.md with unified interface

2. **Migrate tester modules (preserve ~90%)**
   - Copy viewpoint_extractor.py, test_case_generator.py, etc.
   - Adjust imports
   - Keep all templates

3. **Implement context_enricher.py (60 lines)**
   - `enrich_context(input_text: str) -> EnrichedContext`
   - Extract keywords from input
   - Query bk-recall for related items
   - Return: original + related context

4. **Implement requirements_analyzer.py (80 lines)**
   - `analyze(requirements: str) -> AnalysisResult`
   - Extract functional/non-functional requirements
   - Identify ambiguities
   - Generate clarifying questions

5. **Implement user_story_generator.py (50 lines)**
   - `generate_stories(requirements: str) -> list[UserStory]`
   - Format: As a [role], I want [feature], so that [benefit]
   - Japanese output support

6. **Implement gap_detector.py (40 lines)**
   - `detect_gaps(requirements: str) -> list[Gap]`
   - Missing acceptance criteria
   - Undefined edge cases
   - Security/performance not specified

7. **Implement prompt_builder.py (50 lines)**
   - Build prompts for Claude/Gemini
   - Include context from bk-recall
   - Template-based prompt construction

8. **Implement main.py CLI (70 lines)**
   - Subcommands: analyze, test, feature
   - Flags: --type (plan|viewpoint|cases|report|all)
   - Context enrichment toggle: --context/--no-context

9. **Write tests**
   - Migrate from bk-tester/tests/
   - Add analyzer tests
   - Mock bk-recall for context tests

## Todo List

- [ ] Create bk-spec skill directory
- [ ] Write SKILL.md documentation
- [ ] Migrate bk-tester modules (viewpoint, test_case, plan, report)
- [ ] Migrate bk-tester templates
- [ ] Implement context_enricher.py
- [ ] Implement requirements_analyzer.py
- [ ] Implement user_story_generator.py
- [ ] Implement gap_detector.py
- [ ] Implement prompt_builder.py
- [ ] Implement CLI (main.py)
- [ ] Migrate tests
- [ ] Integration test with bk-recall

## Success Criteria

- [ ] `/bk-spec test` produces same output as `/bk-tester`
- [ ] `/bk-spec analyze` generates questions, user stories, specs
- [ ] Context enrichment adds relevant project history
- [ ] Japanese output quality maintained
- [ ] All existing test cases pass

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Context noise | Medium | Relevance threshold, top-k limit |
| bk-recall unavailable | Low | Graceful degradation (skip context) |
| Prompt complexity | Medium | Start simple, iterate |

## Security Considerations

- No auto-execution of generated specs
- Context from vault is read-only
- Prompts don't include sensitive data

## Next Steps

- Phase 6: Create alias for bk-tester
- Future: Excel export for test docs
