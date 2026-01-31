# BrseKit v2 Test Plan

## Overview

| Item | Value |
|------|-------|
| Plan | [260129-2135-brsekit-v2-refactor](../260129-2135-brsekit-v2-refactor/plan.md) |
| Current Progress | ~58% |
| Missing Tests | Phase 0-7 (tất cả phases đều thiếu tests) |
| Test Framework | pytest (Python) |
| Mock Strategy | unittest.mock, pytest-mock |

---

## Test Strategy

### 1. Test Pyramid
```
        /  E2E Tests  \         (10%) - Full workflow tests
       /   Integration \        (30%) - Cross-module tests
      /    Unit Tests    \      (60%) - Individual functions
```

### 2. Test Categories

| Category | Purpose | Tools |
|----------|---------|-------|
| Unit | Isolated function testing | pytest, unittest.mock |
| Integration | Module interactions | pytest, fixtures |
| E2E | Full skill workflow | subprocess, tempfile |
| Contract | API compatibility | schema validation |
| Regression | Backward compatibility | output diff |

### 3. Mock Strategy

| External Dependency | Mock Approach |
|---------------------|---------------|
| Gemini API (embeddings) | Mock responses with fixed vectors |
| Backlog API | Mock HTTP responses with sample data |
| Gmail API | Mock OAuth + IMAP responses |
| Slack API | Mock conversations API |
| File system | tempfile, pytest fixtures |

---

## Phase 0: Vault Infrastructure

### Test Files
```
.claude/skills/lib/vault/tests/
├── test_db.py
├── test_embedder.py
├── test_store.py
├── test_search.py
└── test_sync_tracker.py
```

### Test Cases

#### test_db.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_init_schema_creates_tables` | Verify vault_items và sync_state tables được tạo | P0 |
| `test_get_connection_thread_safe` | Nhiều threads gọi get_connection() không conflict | P1 |
| `test_sqlite_vec_extension_loading` | Load sqlite-vec extension thành công | P1 |
| `test_fallback_without_sqlite_vec` | Graceful degradation khi không có sqlite-vec | P0 |
| `test_db_path_configurable` | Custom DB path hoạt động | P2 |

#### test_embedder.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_embed_single_text` | Embed 1 text, verify 768 dimensions | P0 |
| `test_embed_batch` | Embed nhiều texts cùng lúc | P1 |
| `test_rate_limit_handling` | Exponential backoff khi bị rate limit | P1 |
| `test_empty_text_handling` | Edge case: empty string | P2 |
| `test_long_text_truncation` | Text quá dài được truncate đúng | P2 |
| `test_api_key_missing_error` | Clear error khi GOOGLE_API_KEY không có | P0 |

#### test_store.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_add_item_with_embedding` | Add item, verify embedding được lưu | P0 |
| `test_get_item_by_id` | Get item bằng ID | P0 |
| `test_update_item` | Update partial fields | P1 |
| `test_delete_item` | Delete và verify không còn | P1 |
| `test_list_by_source` | Filter items theo source | P1 |
| `test_duplicate_id_handling` | Xử lý duplicate ID | P2 |
| `test_metadata_json_storage` | Metadata JSON serialize/deserialize | P1 |

#### test_search.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_query_returns_relevant_results` | Semantic search trả về kết quả liên quan | P0 |
| `test_query_by_source_filter` | Filter kết quả theo source | P1 |
| `test_top_k_limit` | Verify top_k limit đúng | P1 |
| `test_empty_vault_search` | Search khi vault rỗng | P2 |
| `test_brute_force_fallback` | Cosine similarity khi không có sqlite-vec | P0 |
| `test_search_performance_10k_items` | <100ms cho 10k items | P2 |

#### test_sync_tracker.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_get_last_sync_new_source` | New source trả về None | P1 |
| `test_update_sync_state` | Update và get lại đúng | P0 |
| `test_sync_config_storage` | Lưu và đọc sync config | P1 |

---

## Phase 1: bk-recall

### Test Files
```
.claude/skills/bk-recall/tests/
├── test_sync_manager.py
├── test_sources/
│   ├── test_email_sync.py
│   ├── test_slack_sync.py
│   └── test_backlog_sync.py
├── test_search_handler.py
└── test_summarizer.py
```

### Test Cases

#### test_sync_manager.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_sync_single_source` | Sync 1 source cụ thể | P0 |
| `test_sync_all_sources` | Sync tất cả configured sources | P1 |
| `test_sync_progress_callback` | Progress reporting hoạt động | P2 |
| `test_sync_error_recovery` | 1 source fail không block others | P1 |

#### test_email_sync.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_fetch_emails_since_last_sync` | Chỉ fetch emails mới | P0 |
| `test_email_to_vault_item_conversion` | Convert email → VaultItem đúng | P0 |
| `test_oauth_token_refresh` | Token refresh khi expired | P1 |
| `test_large_mailbox_pagination` | Handle mailbox lớn | P2 |
| `test_email_body_extraction` | Extract body từ multipart | P1 |

#### test_slack_sync.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_fetch_messages_since_last_sync` | Chỉ fetch messages mới | P0 |
| `test_thread_handling` | Handle thread replies | P1 |
| `test_message_to_vault_item_conversion` | Convert message → VaultItem | P0 |

#### test_backlog_sync.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_fetch_recent_comments` | Fetch comments từ Backlog | P0 |
| `test_issue_update_sync` | Sync issue updates | P1 |
| `test_backlog_client_reuse` | Reuse common/backlog/client.py | P1 |

#### test_search_handler.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_search_returns_markdown` | Output format là Markdown | P0 |
| `test_search_with_source_filter` | Filter by source hoạt động | P1 |
| `test_search_includes_metadata` | Kết quả có source, title, date | P1 |
| `test_search_empty_results` | Handle 0 kết quả gracefully | P2 |

#### test_summarizer.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_summarize_general` | Summary không topic | P0 |
| `test_summarize_with_topic` | Summary cho topic cụ thể | P1 |
| `test_summary_uses_search_results` | Summary dựa trên search | P1 |
| `test_summary_output_structure` | Format output đúng | P1 |

---

## Phase 2: bk-track

### Test Files
```
.claude/skills/bk-track/tests/
├── test_status_analyzer.py
├── test_report_generator.py
├── test_formatters/
│   ├── test_markdown_formatter.py
│   └── test_pptx_formatter.py
└── test_cli.py
```

### Test Cases

#### test_status_analyzer.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_identify_late_tasks` | Phát hiện tasks quá hạn | P0 |
| `test_identify_overloaded_members` | Phát hiện members quá tải | P0 |
| `test_health_summary_generation` | Tạo health summary | P1 |
| `test_threshold_configuration` | Custom threshold hoạt động | P1 |
| `test_output_matches_bk_status` | Output giống bk-status cũ | P0 |

#### test_report_generator.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_generate_weekly_report` | Tạo weekly report | P0 |
| `test_period_configuration` | Custom period hoạt động | P1 |
| `test_sections_complete` | Có đủ sections: overview, accomplished, etc. | P1 |
| `test_output_matches_bk_report` | Output giống bk-report cũ | P0 |
| `test_language_support_ja_vi_en` | Multi-language output | P1 |

#### test_markdown_formatter.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_status_markdown_format` | Status output format đúng | P1 |
| `test_report_markdown_format` | Report output format đúng | P1 |
| `test_template_rendering` | Template rendering hoạt động | P1 |

#### test_pptx_formatter.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_generate_valid_pptx` | Output là valid PPTX | P0 |
| `test_slide_count` | Có đủ 6 slides | P1 |
| `test_japanese_text_rendering` | Japanese text hiển thị đúng | P1 |
| `test_html_template_rendering` | HTML templates render đúng | P1 |
| `test_pptx_generation_time` | <30s generation time | P2 |

#### test_cli.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_status_subcommand` | `/bk-track status` hoạt động | P0 |
| `test_report_subcommand` | `/bk-track report` hoạt động | P0 |
| `test_format_flag` | `--format md|pptx` hoạt động | P1 |
| `test_summary_subcommand` | `/bk-track summary` hoạt động | P1 |

---

## Phase 3: bk-capture

### Test Files
```
.claude/skills/bk-capture/tests/
├── test_task_parser.py
├── test_minutes_parser.py
├── test_classifiers/
│   ├── test_pm_classifier.py
│   └── test_priority_detector.py
├── test_vault_saver.py
├── test_backlog_creator.py
└── test_cli.py
```

### Test Cases

#### test_task_parser.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_parse_japanese_input` | Parse Japanese text → tasks | P0 |
| `test_extract_deadline` | Extract deadline từ text | P1 |
| `test_extract_priority` | Extract priority từ text | P1 |
| `test_output_matches_bk_task` | Output giống bk-task cũ | P0 |
| `test_multiple_tasks_extraction` | Extract nhiều tasks từ 1 input | P1 |

#### test_minutes_parser.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_parse_meeting_transcript` | Parse transcript → structured doc | P0 |
| `test_extract_action_items` | Extract action items | P1 |
| `test_output_matches_bk_minutes` | Output giống bk-minutes cũ | P0 |
| `test_video_input_support` | Support video/audio input (via ai-multimodal) | P2 |

#### test_pm_classifier.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_classify_task` | Classify item as Task | P0 |
| `test_classify_issue` | Classify item as Issue | P0 |
| `test_classify_risk` | Classify item as Risk | P1 |
| `test_classify_question` | Classify item as Question | P1 |
| `test_multilingual_keywords` | JA/VI/EN keywords hoạt động | P1 |
| `test_confidence_score` | Return confidence score | P2 |

#### test_priority_detector.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_detect_high_priority` | Detect 高い, 緊急, urgent | P1 |
| `test_detect_deadline` | Extract date từ text | P1 |
| `test_default_priority` | Default khi không detect được | P2 |

#### test_vault_saver.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_save_to_vault` | Save items to vault | P0 |
| `test_dedup_by_content_hash` | Không lưu duplicates | P1 |
| `test_async_non_blocking` | Save không block output | P1 |

#### test_backlog_creator.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_create_single_task` | Create 1 task trên Backlog | P0 |
| `test_batch_creation` | Create nhiều tasks cùng lúc | P1 |
| `test_human_approval_required` | Require confirmation trước khi create | P0 |

---

## Phase 4: bk-spec

### Test Files
```
.claude/skills/bk-spec/tests/
├── test_analyzer/
│   ├── test_requirements_analyzer.py
│   ├── test_user_story_generator.py
│   └── test_gap_detector.py
├── test_tester/
│   ├── test_viewpoint_extractor.py
│   ├── test_test_case_generator.py
│   ├── test_test_plan_generator.py
│   └── test_report_generator.py
├── test_context_enricher.py
└── test_cli.py
```

### Test Cases

#### test_requirements_analyzer.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_extract_functional_requirements` | Extract FR từ spec | P0 |
| `test_extract_non_functional_requirements` | Extract NFR từ spec | P1 |
| `test_identify_ambiguities` | Phát hiện ambiguous statements | P1 |
| `test_generate_clarifying_questions` | Tạo câu hỏi clarification | P1 |

#### test_user_story_generator.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_generate_user_stories` | Generate format: As a [role]... | P0 |
| `test_japanese_output` | Output bằng tiếng Nhật | P1 |

#### test_gap_detector.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_detect_missing_acceptance_criteria` | Phát hiện thiếu AC | P1 |
| `test_detect_undefined_edge_cases` | Phát hiện edge cases chưa define | P1 |
| `test_detect_security_gaps` | Phát hiện thiếu security requirements | P2 |

#### test_viewpoint_extractor.py (migrate từ bk-tester)
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_extract_viewpoints` | Extract test viewpoints từ spec | P0 |
| `test_output_matches_bk_tester` | Output giống bk-tester cũ | P0 |

#### test_test_case_generator.py (migrate từ bk-tester)
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_generate_test_cases` | Generate test cases từ viewpoints | P0 |
| `test_jstqb_format` | Format theo JSTQB standards | P1 |

#### test_context_enricher.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_enrich_with_vault_context` | Query bk-recall và add context | P0 |
| `test_graceful_degradation` | Hoạt động khi bk-recall unavailable | P1 |
| `test_relevance_threshold` | Filter irrelevant results | P2 |

---

## Phase 5: bk-init

### Test Files
```
.claude/skills/bk-init/tests/
├── test_wizard.py
├── test_validator.py
└── test_config_generator.py
```

### Test Cases

#### test_wizard.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_wizard_prompts_all_steps` | Prompt đủ 5 steps | P0 |
| `test_wizard_accepts_valid_input` | Accept valid input | P0 |
| `test_wizard_rejects_invalid_input` | Reject invalid input với retry | P1 |

#### test_validator.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_validate_backlog_connection` | Test Backlog API connectivity | P0 |
| `test_validate_config_schema` | Config schema validation | P1 |
| `test_clear_error_messages` | Error messages clear và actionable | P2 |

#### test_config_generator.py
| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_generate_valid_yaml` | Output là valid YAML | P0 |
| `test_merge_with_template` | Merge user input với template | P1 |
| `test_vault_section_included` | Vault config section có | P1 |

---

## Phase 6: Alias Layer

### Test Files
```
.claude/skills/tests/
└── test_alias_routing.py
```

### Test Cases

| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_bk_status_routes_to_bk_track` | `/bk-status` → `/bk-track status` | P0 |
| `test_bk_report_routes_to_bk_track` | `/bk-report` → `/bk-track report` | P0 |
| `test_bk_task_routes_to_bk_capture` | `/bk-task` → `/bk-capture task` | P0 |
| `test_bk_minutes_routes_to_bk_capture` | `/bk-minutes` → `/bk-capture meeting` | P0 |
| `test_bk_tester_routes_to_bk_spec` | `/bk-tester` → `/bk-spec test` | P0 |
| `test_bk_translate_routes_to_bk_convert` | `/bk-translate` → `/bk-convert` | P0 |
| `test_flags_preserved` | All flags pass through đúng | P0 |
| `test_deprecation_notice_shown` | Deprecation notice hiển thị | P1 |
| `test_output_identical` | Output old command = new command | P0 |

---

## Phase 7: PPTX Integration

### Test Files
```
.claude/skills/bk-track/tests/
├── test_pptx_formatter.py
└── test_slide_templates.py
```

### Test Cases

| Test Case | Description | Priority |
|-----------|-------------|----------|
| `test_generate_valid_pptx_file` | Output file valid | P0 |
| `test_pptx_opens_in_libreoffice` | Có thể mở trong LibreOffice | P1 |
| `test_all_6_slides_present` | Đủ 6 slides | P1 |
| `test_title_slide_content` | Title slide có project name, date range | P1 |
| `test_summary_slide_metrics` | Summary slide có metrics đúng | P1 |
| `test_japanese_font_rendering` | Japanese text render đúng | P1 |
| `test_html_to_pptx_conversion` | html2pptx.js hoạt động | P0 |
| `test_generation_time_under_30s` | Generation time <30s | P2 |
| `test_thumbnail_validation` | Thumbnail validation passes | P2 |

---

## Test Implementation Approach

### 1. Fixtures (pytest)

```python
# conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_vault_db():
    """Temporary vault DB for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        yield Path(f.name)

@pytest.fixture
def mock_gemini_embedder(mocker):
    """Mock Gemini API with fixed embeddings."""
    mock = mocker.patch('lib.vault.embedder.GeminiEmbedder.embed')
    mock.return_value = [0.1] * 768  # Fixed 768-dim vector
    return mock

@pytest.fixture
def mock_backlog_client(mocker):
    """Mock Backlog API responses."""
    mock = mocker.patch('common.backlog.client.BacklogClient')
    mock.return_value.get_issues.return_value = [...]
    return mock

@pytest.fixture
def sample_vault_items():
    """Sample VaultItem objects for testing."""
    return [
        VaultItem(id="1", source="email", title="Subject", content="Body"),
        VaultItem(id="2", source="slack", title="Thread", content="Message"),
    ]
```

### 2. Mock External APIs

```python
# tests/mocks/gemini_mock.py
MOCK_EMBEDDING = [0.1] * 768

def mock_embed_response(text: str) -> list[float]:
    """Deterministic mock embedding based on text hash."""
    import hashlib
    h = int(hashlib.md5(text.encode()).hexdigest(), 16)
    return [(h % (i+1)) / 1000 for i in range(768)]
```

### 3. Regression Tests (Output Comparison)

```python
# tests/regression/test_output_compatibility.py
def test_bk_status_output_unchanged():
    """Compare old bk-status output with new bk-track status."""
    old_output = run_skill("bk-status", "--threshold", "5")
    new_output = run_skill("bk-track", "status", "--threshold", "5")

    # Normalize và compare
    assert normalize_output(old_output) == normalize_output(new_output)
```

### 4. Integration Tests

```python
# tests/integration/test_vault_to_recall.py
def test_end_to_end_vault_search():
    """Test full flow: store → embed → search."""
    # Setup
    vault = VaultStore(db_path=":memory:")

    # Store items
    vault.add(VaultItem(source="email", title="Bug report", content="Login failed"))
    vault.add(VaultItem(source="slack", title="Discussion", content="Auth issue"))

    # Search
    search = VaultSearch(vault)
    results = search.query("authentication problem", top_k=5)

    # Verify
    assert len(results) >= 1
    assert "login" in results[0].content.lower() or "auth" in results[0].content.lower()
```

---

## Test Execution Plan

### Execution Order
1. **Phase 0 tests** (foundation) - FIRST
2. **Phase 5 tests** (bk-init) - Independent
3. **Phase 1 tests** (bk-recall) - Depends on Phase 0
4. **Phase 2 tests** (bk-track) - Depends on Phase 0
5. **Phase 3 tests** (bk-capture) - Depends on Phase 0, 1
6. **Phase 4 tests** (bk-spec) - Depends on Phase 1
7. **Phase 6 tests** (alias) - After Phase 2-5
8. **Phase 7 tests** (PPTX) - After Phase 2

### CI/CD Integration

```yaml
# .github/workflows/test-brsekit.yml
name: BrseKit Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pytest pytest-mock pytest-cov
          pip install -r .claude/skills/lib/vault/requirements.txt

      - name: Run unit tests
        run: pytest .claude/skills/*/tests/ -v --cov

      - name: Run integration tests
        run: pytest tests/integration/ -v
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
```

---

## Test Coverage Targets

| Phase | Unit | Integration | E2E | Target |
|-------|------|-------------|-----|--------|
| Phase 0 | 90% | 80% | N/A | 85% |
| Phase 1 | 80% | 70% | 50% | 75% |
| Phase 2 | 80% | 70% | 50% | 75% |
| Phase 3 | 80% | 70% | 50% | 75% |
| Phase 4 | 80% | 70% | 50% | 75% |
| Phase 5 | 80% | 60% | 50% | 70% |
| Phase 6 | 90% | 80% | 70% | 80% |
| Phase 7 | 70% | 60% | 50% | 65% |

---

## Recommendations

### 1. Priority Order
1. **Phase 0 tests** - Foundation, block mọi thứ khác
2. **Phase 6 tests** - Backward compatibility critical
3. **Phase 2-4 tests** - Core functionality

### 2. Quick Wins
- Mock all external APIs (Gemini, Backlog, Gmail, Slack)
- Use in-memory SQLite cho speed
- Parallel test execution với pytest-xdist

### 3. Risk Mitigation
- Test sqlite-vec availability check FIRST
- Test cross-platform (Windows, macOS, Linux)
- Test với real Gemini API (rate limited, separate job)

### 4. Tools Needed
```
pytest>=8.0
pytest-mock>=3.12
pytest-cov>=4.1
pytest-xdist>=3.5  # Parallel execution
python-pptx>=0.6   # PPTX validation
```

---

## Unresolved Questions

1. **sqlite-vec testing**: Cần test trên Windows với sqlite-vec build? Hay chỉ test fallback?
2. **Gemini API testing**: Có nên có separate job với real API hay chỉ mock?
3. **PPTX validation**: Cần validate với PowerPoint hay chỉ LibreOffice?
4. **Test data**: Có sample data JA/VI thực tế để test không?

---

*Generated: 2026-01-30 09:07*
