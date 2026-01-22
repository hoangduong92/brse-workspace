# Phase 06: Testing & Validation

**Context**: Parent plan [../plan.md](plan.md)

## Overview

**Date**: 2026-01-22
**Description**: Comprehensive testing, validation, and documentation of the Nulab Backlog Automation skill
**Priority**: P1
**Status**: pending
**Effort**: 2h

## Key Insights

- Test with real tickets from HB21373
- Validate translation quality manually
- Test all three task types
- Document usage and troubleshooting

## Requirements

### Functional
- Test all three task types (feature dev, upload scenario, investigate issue)
- Test JA → VI translation
- Test VI → JA translation
- Test error scenarios
- Measure execution time
- Validate created tickets match templates

### Non-Functional
- Translation accuracy > 90%
- Execution time < 10 seconds
- Zero test failures
- Complete documentation

## Test Scenarios

### 1. Feature Development Ticket (JA → VI)
**Input:** HB21373-XXX (Japanese feature request)
**Expected:**
- Translated summary and description
- 4 subtasks created (Analysis, Implementation, Testing, Code Review)
- Normal priority

### 2. Upload Scenario Ticket (JA → VI)
**Input:** HB21373-XXX (Japanese scenario upload)
**Expected:**
- Translated content
- No subtasks
- High priority
- [Scenario] prefix

### 3. Investigate Issue Ticket (VI → JA)
**Input:** HB21373-XXX (Vietnamese bug report)
**Expected:**
- Translated to Japanese
- No subtasks
- Urgent priority
- [Investigate] prefix

### 4. Error Scenarios
- Invalid ticket ID format
- Non-existent ticket
- API authentication failure
- Translation API failure

## Related Code Files

### Modify
- `.claude/skills/backlog/README.md` (create)
- `.claude/skills/backlog/CHANGELOG.md` (create)

### Create
- `.claude/skills/backlog/tests/test_real_tickets.py`
- `.claude/skills/backlog/docs/TROUBLESHOOTING.md`

## Implementation Steps

1. **Create test suite** (`test_real_tickets.py`)
   ```python
   import pytest
   from main import create_ticket

   @pytest.mark.integration
   def test_feature_dev_ja_to_vi():
       """Test feature development ticket translation JA → VI"""
       result = create_ticket("HB21373-TEST-001", dry_run=True)
       assert result["success"]
       assert result["data"]["summary"].startswith("[KH-")

   @pytest.mark.integration
   def test_upload_scenario_ja_to_vi():
       """Test scenario upload JA → VI"""
       result = create_ticket("HB21373-TEST-002", dry_run=True)
       assert result["success"]
       assert result["data"]["summary"].startswith("[Scenario]")

   @pytest.mark.integration
   def test_investigate_issue_vi_to_ja():
       """Test issue investigation VI → JA"""
       result = create_ticket("HB21373-TEST-003", dry_run=True)
       assert result["success"]
       assert result["data"]["summary"].startswith("[Investigate]")
   ```

2. **Run unit tests**
   ```bash
   cd .claude/skills
   .venv/Scripts/python -m pytest backlog/tests/ -v
   ```

3. **Run integration tests with real tickets**
   - Get real ticket IDs from HB21373
   - Run with dry-run first
   - Review generated output
   - Run actual creation with test tickets
   - Verify in destination backlog

4. **Manual validation checklist**
   - [ ] Translation accuracy (review 10+ tickets)
   - [ ] Task type detection accuracy
   - [ ] Template application correctness
   - [ ] Subtask creation (for dev tasks)
   - [ ] Priority mapping
   - [ ] Assignee handling
   - [ ] Error messages clarity

5. **Measure performance**
   ```python
   import time

   start = time.time()
   result = create_ticket("HB21373-123")
   duration = time.time() - start

   assert duration < 10, f"Too slow: {duration:.2f}s"
   print(f"Execution time: {duration:.2f}s")
   ```

6. **Create documentation** (`README.md`)
   ```markdown
   # Backlog Automation Skill

   Automate ticket creation from customer backlog to internal backlog.

   ## Setup

   1. Copy `.env.example` to `.env`
   2. Fill in API keys and project IDs
   3. Install dependencies: `pip install -r requirements.txt`

   ## Usage

   Via Claude Code:
   ```
   /backlog create-ticket HB21373-123
   ```

   Or directly:
   ```bash
   python scripts/main.py HB21373-123
   ```

   Dry run:
   ```bash
   python scripts/main.py HB21373-123 --dry-run
   ```

   ## Task Types

   - **Feature Development**: Creates 4 subtasks (Analysis, Implementation, Testing, Code Review)
   - **Upload Scenario**: No subtasks, high priority
   - **Investigate Issue**: No subtasks, urgent priority

   ## Troubleshooting

   See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
   ```

7. **Create troubleshooting guide**
   ```markdown
   # Troubleshooting

   ## Common Issues

   ### API Key Errors
   - Verify API key in `.env`
   - Check API key permissions

   ### Ticket Not Found
   - Verify ticket ID format
   - Check ticket exists in source project

   ### Translation Fails
   - Check Anthropic API key
   - Verify API quota not exceeded

   ### Rate Limiting
   - Wait 60 seconds and retry
   - Check Nulab API usage
   ```

8. **Create CHANGELOG.md**
   ```markdown
   # Changelog

   ## [1.0.0] - 2026-01-22

   ### Added
   - Initial release
   - JA ↔ VI translation
   - Dynamic task templates
   - Auto subtask creation for dev tasks
   - Support for 3 task types
   ```

## Todo List

- [ ] Create integration test suite
- [ ] Run all unit tests
- [ ] Test with real tickets (dry-run)
- [ ] Test with real tickets (actual creation)
- [ ] Validate translation quality manually
- [ ] Measure execution time
- [ ] Create README.md
- [ ] Create TROUBLESHOOTING.md
- [ ] Create CHANGELOG.md
- [ ] Document all environment variables
- [ ] Create example test tickets

## Success Criteria

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Translation accuracy > 90% (manual review)
- [ ] Task type detection > 90% accuracy
- [ ] Execution time < 10 seconds
- [ ] Zero errors in logs
- [ ] Complete documentation
- [ ] Real tickets created successfully

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Translation quality issues | Medium | Human review, iterative prompt improvement |
| Test ticket cleanup | Low | Use separate test project, delete after |
| API quota exhaustion | Low | Use Haiku model, monitor usage |

## Security Considerations

- Never commit real API keys
- Sanitize ticket data before logging
- Use test tickets for validation
- Remove sensitive data from documentation

## Next Steps

After successful testing and validation:
1. Deploy to production environment
2. Train users on usage
3. Monitor for issues
4. Gather feedback for improvements

---

**Dependencies**: All previous phases must be complete
**Blocks**: None (final phase)
