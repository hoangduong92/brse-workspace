# Phase 2: bk-track (Merge status + report)

## Context Links
- [bk-status SKILL.md](c:/Users/duongbibo/brse-workspace/.claude/skills/bk-status/SKILL.md)
- [bk-report SKILL.md](c:/Users/duongbibo/brse-workspace/.claude/skills/bk-report/SKILL.md)
- [PPTX Skill](c:/Users/duongbibo/brse-workspace/.claude/skills/document-skills/pptx/SKILL.md)

## Overview
- **Priority:** P0
- **Status:** 100% complete (74 tests passing)
- **Effort:** 3h
- **Description:** Merge bk-status and bk-report into unified tracking skill with PPTX support

## Key Insights
- bk-status: late tasks, overloaded members, health summary
- bk-report: weekly report with sections (overview, accomplished, in-progress, next week, risks)
- ~70% code reuse: shared Backlog client, models, analyzers
- PPTX generation via existing pptx skill (html2pptx workflow)

## Requirements

### Functional
- `/bk-track status` - Project health check (current bk-status)
- `/bk-track report [--period X]` - Weekly report (current bk-report)
- `/bk-track --format md|pptx` - Output format selection
- `/bk-track summary` - Quick one-liner status

### Non-Functional
- Backward compatible with bk-status/bk-report flags
- PPTX generation <30s for typical report
- Same output quality as existing skills

## Architecture

```
.claude/skills/bk-track/
├── SKILL.md
├── requirements.txt
├── scripts/
│   ├── main.py              # CLI router
│   ├── status_analyzer.py   # From bk-status (refactored)
│   ├── report_generator.py  # From bk-report (refactored)
│   ├── formatters/
│   │   ├── __init__.py
│   │   ├── markdown.py      # MD output
│   │   └── pptx_formatter.py # PPTX via html2pptx
│   └── models.py            # Shared data models
├── templates/
│   ├── status_template.md
│   ├── report_template.md
│   └── report_slides.html   # For PPTX
└── tests/
    ├── test_status.py
    └── test_report.py
```

### Merge Strategy
```
bk-status/scripts/status_analyzer.py  → bk-track/scripts/status_analyzer.py
bk-status/scripts/models.py           → bk-track/scripts/models.py
bk-report/scripts/report_generator.py → bk-track/scripts/report_generator.py
bk-report/templates/*                 → bk-track/templates/
```

## Related Code Files

### Create
- `.claude/skills/bk-track/SKILL.md`
- `.claude/skills/bk-track/requirements.txt`
- `.claude/skills/bk-track/scripts/main.py`
- `.claude/skills/bk-track/scripts/formatters/__init__.py`
- `.claude/skills/bk-track/scripts/formatters/markdown.py`
- `.claude/skills/bk-track/scripts/formatters/pptx_formatter.py`
- `.claude/skills/bk-track/templates/report_slides.html`

### Move/Refactor
- `.claude/skills/bk-status/scripts/status_analyzer.py` → `.claude/skills/bk-track/scripts/`
- `.claude/skills/bk-status/scripts/models.py` → `.claude/skills/bk-track/scripts/`
- `.claude/skills/bk-report/scripts/report_generator.py` → `.claude/skills/bk-track/scripts/`
- `.claude/skills/bk-report/templates/` → `.claude/skills/bk-track/templates/`

### Reuse
- `.claude/skills/common/backlog/client.py`
- `.claude/skills/common/backlog/calendar_utils.py`
- `.claude/skills/document-skills/pptx/scripts/html2pptx.js`

### Delete (after alias layer)
- `.claude/skills/bk-status/` (Phase 6)
- `.claude/skills/bk-report/` (Phase 6)

## Implementation Steps

1. **Create bk-track skill structure**
   - Create directories
   - Write SKILL.md with unified interface

2. **Migrate status_analyzer.py (preserve ~90%)**
   - Copy from bk-status
   - Extract shared models to models.py
   - Adjust imports

3. **Migrate report_generator.py (preserve ~80%)**
   - Copy from bk-report
   - Integrate with shared models
   - Refactor template loading

4. **Implement main.py CLI (60 lines)**
   - Subcommands: status, report, summary
   - Flags: --format, --lang, --period, --threshold
   - Route to analyzers

5. **Implement formatters/markdown.py (40 lines)**
   - `StatusMarkdownFormatter` - format status report
   - `ReportMarkdownFormatter` - format weekly report
   - Template-based rendering

6. **Implement formatters/pptx_formatter.py (80 lines)**
   - `ReportPptxFormatter` class
   - Generate HTML slides from report data
   - Call html2pptx.js via subprocess
   - Save to output path

7. **Create report_slides.html template**
   - Title slide: Project name, date range
   - Summary slide: Key metrics
   - Accomplishments slide: Completed tasks
   - In-progress slide: Current work
   - Risks slide: Late/at-risk items

8. **Write tests**
   - test_status.py: migrate from bk-status
   - test_report.py: migrate from bk-report
   - test_pptx.py: PPTX generation

## Todo List

- [ ] Create bk-track skill directory
- [ ] Write SKILL.md documentation
- [ ] Migrate status_analyzer.py
- [ ] Migrate report_generator.py
- [ ] Extract shared models.py
- [ ] Implement CLI (main.py)
- [ ] Implement markdown formatter
- [ ] Implement pptx_formatter
- [ ] Create HTML slide template
- [ ] Migrate and update tests
- [ ] Integration test

## Success Criteria

- [ ] `/bk-track status` produces same output as `/bk-status`
- [ ] `/bk-track report` produces same output as `/bk-report`
- [ ] `/bk-track report --format pptx` generates valid PPTX
- [ ] All existing test cases pass
- [ ] Language support (ja/vi/en) works

## Risk Assessment

| Risk | Probability | Mitigation |
|------|-------------|------------|
| PPTX rendering issues | Medium | Use existing pptx skill workflow |
| Breaking existing output | Low | Compare outputs before/after |
| Template complexity | Low | Start with simple slides |

## Security Considerations

- Same as bk-status/bk-report (API key handling)
- PPTX generated locally (no cloud service)

## Next Steps

- Phase 6: Create aliases for bk-status/bk-report
- Phase 7: Enhanced PPTX templates
