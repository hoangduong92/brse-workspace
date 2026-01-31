# Test Implementation Roadmap

**Generated:** 2026-01-30 09:57 AM
**Status:** Planning for next phases
**Context:** Follow-up to BrseKit v2 Test Execution Report

---

## Summary of Current State

### ✅ Completed & Passing
- **Phase 0 (Vault):** 56/56 tests passing ✅
- **Phase 5 (bk-init):** 99/99 tests passing ✅
- **Phase 3 (bk-capture):** 4/4 tests passing ✅

### ⚠️ Partially Completed
- **Phase 1 (bk-recall):** 35/63 tests passing (blocked by import issues)
- **Phase 2 (bk-track):** 55/91 tests passing (blocked by import issues)

### ❌ Not Yet Implemented
- **Phase 4 (bk-spec):** 0/0 tests (no test files exist)
- **Phase 6 (Alias Layer):** 0/0 tests (no test files exist)
- **Phase 7 (PPTX Integration):** 0/0 tests (no test files exist)

---

## Immediate Next Steps

### 1️⃣ FIX: Import Issues (BLOCKING)
**Time:** 1-2 hours
**Files Affected:** 2 conftest.py + 9 source files
**Status:** ⚠️ CRITICAL - Must fix before continuing
**See:** `tester-260130-0957-fix-import-issues-phase1-phase2.md`

**After fix:** Phase 1 & 2 should have 90%+ pass rate

---

## Testing Roadmap: Months View

```
JAN 30          FEB 3           FEB 10          FEB 17          FEB 28
  |               |               |               |               |
  +---Phase 1/2---+---Phase 3/4---+---Phase 6/7---+---Integration--+
    (fix imports)   (expand tests) (new tests)      (end-to-end)
```

---

## Phase-by-Phase Implementation Plan

### PHASE 3: Expand bk-capture Coverage 🔨

**Current State:**
- 4 tests implemented (basic parsers)
- 40+ tests planned but not implemented

**Required Tests (from test plan):**

#### test_task_parser.py (8 tests)
```python
def test_parse_japanese_input()
def test_extract_deadline()
def test_extract_priority()
def test_output_matches_bk_task()
def test_multiple_tasks_extraction()
def test_empty_input_handling()
def test_unicode_support()
def test_whitespace_handling()
```

#### test_minutes_parser.py (6 tests)
```python
def test_parse_meeting_transcript()
def test_extract_action_items()
def test_output_matches_bk_minutes()
def test_video_input_support()
def test_timestamp_extraction()
def test_participant_extraction()
```

#### test_classifiers.py (12 tests)
```python
# PM Classifier Tests
def test_classify_task()
def test_classify_issue()
def test_classify_risk()
def test_classify_question()
def test_multilingual_keywords()
def test_confidence_score()

# Priority Detector Tests
def test_detect_high_priority()
def test_detect_deadline()
def test_detect_medium_priority()
def test_detect_low_priority()
def test_default_priority()
def test_multilingual_priority()
```

#### test_vault_saver.py (5 tests)
```python
def test_save_to_vault()
def test_dedup_by_content_hash()
def test_async_non_blocking()
def test_metadata_preservation()
def test_error_handling()
```

#### test_backlog_creator.py (6 tests)
```python
def test_create_single_task()
def test_batch_creation()
def test_human_approval_required()
def test_duplicate_task_detection()
def test_api_error_handling()
def test_field_mapping()
```

#### test_cli.py (7 tests)
```python
def test_cli_task_command()
def test_cli_minutes_command()
def test_cli_help_text()
def test_cli_with_file_input()
def test_cli_with_stdin()
def test_cli_output_format()
def test_cli_error_messages()
```

**Total Tests Needed:** 44 tests
**Estimated Time:** 4-6 hours
**Priority:** HIGH - Core parsing functionality

---

### PHASE 4: Implement bk-spec Tests 🆕

**Current State:**
- 0 tests implemented
- 50+ tests planned

**Directory Structure to Create:**
```
.claude/skills/bk-spec/tests/
├── __init__.py
├── conftest.py
├── test_analyzer/
│   ├── __init__.py
│   ├── test_requirements_analyzer.py
│   ├── test_user_story_generator.py
│   └── test_gap_detector.py
├── test_tester/
│   ├── __init__.py
│   ├── test_viewpoint_extractor.py
│   ├── test_test_case_generator.py
│   ├── test_test_plan_generator.py
│   └── test_report_generator.py
├── test_context_enricher.py
└── test_cli.py
```

**Required Tests:**

#### test_requirements_analyzer.py (4 tests)
```python
def test_extract_functional_requirements()
def test_extract_non_functional_requirements()
def test_identify_ambiguities()
def test_generate_clarifying_questions()
```

#### test_user_story_generator.py (2 tests)
```python
def test_generate_user_stories()
def test_japanese_output()
```

#### test_gap_detector.py (3 tests)
```python
def test_detect_missing_acceptance_criteria()
def test_detect_undefined_edge_cases()
def test_detect_security_gaps()
```

#### test_viewpoint_extractor.py (2 tests)
```python
def test_extract_viewpoints()
def test_output_matches_bk_tester()
```

#### test_test_case_generator.py (2 tests)
```python
def test_generate_test_cases()
def test_jstqb_format()
```

#### test_context_enricher.py (3 tests)
```python
def test_enrich_with_vault_context()
def test_graceful_degradation()
def test_relevance_threshold()
```

#### test_cli.py (5 tests)
```python
def test_spec_command()
def test_analyzer_subcommand()
def test_tester_subcommand()
def test_output_format_flag()
def test_help_text()
```

**Total Tests Needed:** 21 tests
**Estimated Time:** 3-4 hours
**Priority:** MEDIUM - New analysis module

---

### PHASE 6: Implement Alias Layer Tests ⭐ CRITICAL

**Current State:**
- 0 tests implemented
- 9 tests planned
- **BACKWARD COMPATIBILITY CRITICAL**

**File to Create:**
```
.claude/skills/tests/
├── __init__.py
├── conftest.py
└── test_alias_routing.py
```

**Required Tests:**

#### test_alias_routing.py (9 tests)
```python
def test_bk_status_routes_to_bk_track()
    # Command: bk-status → bk-track status
    # Verify: Same output, flags passed through

def test_bk_report_routes_to_bk_track()
    # Command: bk-report → bk-track report
    # Verify: Same output, date range preserved

def test_bk_task_routes_to_bk_capture()
    # Command: bk-task → bk-capture task
    # Verify: Same output, priority preserved

def test_bk_minutes_routes_to_bk_capture()
    # Command: bk-minutes → bk-capture meeting
    # Verify: Same output, transcript parsed

def test_bk_tester_routes_to_bk_spec()
    # Command: bk-tester → bk-spec test
    # Verify: Same output, viewpoints extracted

def test_bk_translate_routes_to_bk_convert()
    # Command: bk-translate → bk-convert
    # Verify: Same output, language flags preserved

def test_flags_preserved()
    # Verify all flags pass through unchanged
    # Examples: --format, --language, --output, etc.

def test_deprecation_notice_shown()
    # Verify deprecation warning displayed
    # Suggest new command name

def test_output_identical()
    # Compare old command output with new command output
    # Normalize and verify 100% match
```

**Total Tests Needed:** 9 tests
**Estimated Time:** 2-3 hours
**Priority:** ⭐ CRITICAL - Must pass for backward compatibility

---

### PHASE 7: Implement PPTX Tests 🎨

**Current State:**
- 0 dedicated tests
- Expected in bk-track tests but not found

**File to Create:**
```
.claude/skills/bk-track/tests/
├── test_pptx_formatter.py
└── test_slide_templates.py
```

**Required Tests:**

#### test_pptx_formatter.py (6 tests)
```python
def test_generate_valid_pptx_file()
    # Verify output file is valid PPTX format
    # Can be opened by python-pptx library

def test_pptx_opens_in_libreoffice()
    # Verify file can be opened with LibreOffice
    # Windows: Use COM automation or subprocess

def test_all_6_slides_present()
    # Verify: Title, Summary, Accomplished, In Progress, Risks, Health

def test_title_slide_content()
    # Verify: Project name, date range, team info

def test_summary_slide_metrics()
    # Verify: Health score, completion %, overdue count

def test_japanese_font_rendering()
    # Verify: Japanese text renders correctly
    # Check: Noto Sans CJK font available
```

#### test_slide_templates.py (5 tests)
```python
def test_html_to_pptx_conversion()
    # Verify: html2pptx.js works correctly
    # Check: Template variables substituted

def test_generation_time_under_30s()
    # Measure: Generation time
    # Assert: < 30 seconds

def test_thumbnail_validation()
    # Verify: Thumbnail image generated
    # Check: Correct dimensions

def test_multilingual_template()
    # Test: JA/VI/EN output
    # Verify: Correct language in slides

def test_theme_colors_applied()
    # Verify: Brand colors applied to slides
    # Check: Accent colors consistent
```

**Total Tests Needed:** 11 tests
**Estimated Time:** 2-3 hours
**Priority:** MEDIUM - Presentation feature

---

## Integration Tests (New Category)

**Not in original plan but needed:**

#### test_vault_to_recall.py
```python
def test_vault_store_and_search_workflow()
    # 1. Add items to vault
    # 2. Embed items
    # 3. Search vault
    # 4. Verify results

def test_sync_and_search_workflow()
    # 1. Sync from email/slack
    # 2. Items stored in vault
    # 3. Search returns synced items
```

#### test_capture_to_vault.py
```python
def test_parse_task_and_save_to_vault()
    # 1. Parse task from text
    # 2. Save to vault
    # 3. Retrieve from vault
    # 4. Verify metadata

def test_minutes_to_vault()
    # 1. Parse minutes
    # 2. Extract action items
    # 3. Save to vault
    # 4. Search vault for items
```

#### test_track_to_report.py
```python
def test_analyze_issues_and_generate_report()
    # 1. Fetch issues from Backlog
    # 2. Analyze status
    # 3. Generate report
    # 4. Verify output format

def test_report_to_pptx()
    # 1. Generate report
    # 2. Convert to PPTX
    # 3. Verify valid file
```

**Total Tests Needed:** 6 tests
**Estimated Time:** 3-4 hours
**Priority:** HIGH - Cross-module validation

---

## E2E Tests (Future)

**Full workflow tests not yet planned:**

- Command line invocation
- File input/output handling
- Real API calls (if available)
- Error recovery scenarios
- Performance benchmarks

**Estimated Time:** 10-15 hours
**Priority:** LOW - After unit/integration tests pass

---

## Test Coverage Matrix

| Phase | Unit | Integration | E2E | Total | Status |
|-------|------|-------------|-----|-------|--------|
| 0     | 50   | 6           | -   | 56    | ✅ Done |
| 1     | 45   | 10          | -   | 55    | ⚠️ Blocked |
| 2     | 70   | 15          | 6   | 91    | ⚠️ Blocked |
| 3     | 40   | 5           | -   | 45    | 🔨 In Progress |
| 4     | 21   | 5           | -   | 26    | 🆕 To Implement |
| 5     | 95   | 4           | -   | 99    | ✅ Done |
| 6     | 9    | -           | -   | 9     | 🆕 To Implement |
| 7     | 11   | 5           | -   | 16    | 🆕 To Implement |
| Integ | -    | 6           | -   | 6     | 🔨 To Add |
| E2E   | -    | -           | 10  | 10    | 🆕 To Add |
| **TOTAL** | **341** | **56** | **16** | **413** | |

---

## Timeline & Effort Estimate

### Week 1 (This Week)
- [ ] Fix Phase 1 & 2 import issues (1-2 hrs)
- [ ] Expand Phase 3 coverage (4-6 hrs)
- [ ] Implement Phase 6 alias tests (2-3 hrs)
- **Total:** 7-11 hours

### Week 2
- [ ] Implement Phase 4 tests (3-4 hrs)
- [ ] Implement Phase 7 PPTX tests (2-3 hrs)
- [ ] Add integration tests (3-4 hrs)
- **Total:** 8-11 hours

### Week 3
- [ ] Refine based on Phase 1 & 2 results
- [ ] Add E2E tests (10-15 hrs)
- [ ] Performance benchmarking (2-3 hrs)
- **Total:** 12-18 hours

### Month 1 Total
**Estimated:** 30-40 hours of test implementation and refinement

---

## Quality Gates

### Unit Test Coverage Targets
- Phase 0: 90% ✅
- Phase 1: 85% ⚠️
- Phase 2: 80% ⚠️
- Phase 3: 85% 🎯
- Phase 4: 80% 🎯
- Phase 5: 90% ✅
- Phase 6: 90% 🎯
- Phase 7: 75% 🎯

### Integration Test Targets
- Core workflows: 100% coverage
- Cross-module communication: 100%
- Error scenarios: 80%

### E2E Test Targets
- Happy path: 100%
- Alternative paths: 60%
- Error scenarios: 40%

---

## Testing Tools & Infrastructure

### Current Setup
- ✅ pytest 9.0.2
- ✅ Python 3.11.9
- ✅ unittest.mock
- ⚠️ pytest-cov (needs installation for coverage reports)
- ⚠️ pytest-mock (needs verification)

### Needed
```bash
pip install pytest-cov>=4.1
pip install pytest-xdist>=3.5  # For parallel testing
pip install python-pptx>=0.6   # For PPTX validation
pip install responses>=0.21    # For HTTP mocking
```

### CI/CD Integration
- [ ] GitHub Actions workflow for test execution
- [ ] Coverage report generation
- [ ] Test result artifacts
- [ ] Failure notifications

---

## Mock Data & Fixtures

### Sample Data Needed

**Language Samples:**
```
Japanese:
- "タスク: 〇〇の実装 (期限: 2月15日) 優先度: 高"
- "会議記録: プロジェクト進捗確認 15:00-16:00"

Vietnamese:
- "Nhiệm vụ: Triển khai tính năng 〇〇 (Thời hạn: 15/2) Ưu tiên: Cao"

English:
- "Task: Implement feature 〇〇 (Deadline: Feb 15) Priority: High"
```

**Backlog Sample Data:**
```json
{
  "issues": [
    {
      "id": 1,
      "summary": "Fix login bug",
      "assignee": {"name": "John"},
      "dueDate": "2026-02-15",
      "status": {"name": "Open"}
    }
  ]
}
```

**Email Sample:**
```
From: user@example.com
Subject: Weekly Update
Date: 2026-01-30T09:00:00Z
Body: "Completed task X, working on task Y. Blocked by issue Z."
```

**Slack Sample:**
```json
{
  "messages": [
    {
      "text": "FYI: Project update - 80% complete",
      "user": "U12345",
      "ts": "1643548800"
    }
  ]
}
```

---

## Success Criteria

### Phase Completion (For Each Phase)
- ✅ All planned tests implemented
- ✅ Pass rate >= 90%
- ✅ Code coverage >= 80%
- ✅ No flaky tests
- ✅ Execution time < 5 minutes per phase

### Release Readiness
- ✅ All 7 phases passing
- ✅ 400+ tests passing
- ✅ Integration tests passing
- ✅ 80%+ code coverage
- ✅ Backward compatibility verified (Phase 6)
- ✅ CI/CD pipeline green

---

## Known Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Import issues block Phase 1 & 2 | HIGH | Fix immediately (see dedicated doc) |
| External API rate limiting | MEDIUM | Use mocks, separate real-API tests |
| Windows-specific issues (sqlite-vec, PPTX fonts) | MEDIUM | Test on CI/CD (Linux), add platform-specific tests |
| Missing test data (JA/VI samples) | MEDIUM | Create comprehensive fixtures |
| PPTX generation time exceeds 30s | LOW | Optimize template rendering, parallelize |
| Flaky synchronization tests | MEDIUM | Add timeout handling, use in-memory DBs |

---

## Next Actions (Priority Order)

1. **TODAY (HIGH PRIORITY)**
   - [ ] Fix Phase 1 & 2 import issues
   - [ ] Re-run tests to verify fix

2. **THIS WEEK (HIGH PRIORITY)**
   - [ ] Expand Phase 3 to 44 tests
   - [ ] Implement Phase 6 alias tests (critical for backward compat)
   - [ ] Run all phases, target 90%+ pass rate

3. **NEXT WEEK (MEDIUM PRIORITY)**
   - [ ] Implement Phase 4 bk-spec tests
   - [ ] Implement Phase 7 PPTX tests
   - [ ] Add integration tests

4. **WEEK 3 (MEDIUM PRIORITY)**
   - [ ] Add E2E tests
   - [ ] Performance benchmarking
   - [ ] Setup CI/CD pipeline

5. **ONGOING**
   - [ ] Monitor test quality metrics
   - [ ] Keep coverage above 80%
   - [ ] Add regression tests for bugs

---

## Reports & Documentation

### Generated Reports
- `tester-260130-0957-brsekit-v2-test-execution.md` - Main test execution results
- `tester-260130-0957-fix-import-issues-phase1-phase2.md` - Detailed fix plan
- `tester-260130-0957-test-implementation-roadmap.md` - This document

### Original Documentation
- `plans/reports/tester-260130-0907-brsekit-v2-test-plan.md` - Master test plan
- `plans/260129-2135-brsekit-v2-refactor/plan.md` - Refactoring plan

---

## Questions & Open Items

1. **Import Strategy:** Should we use absolute imports or sys.path manipulation?
2. **Test Data:** Where are JA/VI sample data files located?
3. **Real APIs:** Should Phase 1 & 2 tests use real APIs or just mocks?
4. **PPTX Validation:** Should tests validate with PowerPoint or just LibreOffice?
5. **Performance Thresholds:** Are <30s PPTX generation and <100ms search acceptable?
6. **Parallel Testing:** Should we enable pytest-xdist for faster test runs?

---

*Report Generated: 2026-01-30 09:57 AM*
*Next Review: After Phase 1 & 2 import fixes*
*Prepared by: QA Team*
