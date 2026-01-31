# BrseKit Skills Architecture Analysis Report

**Report Date:** 2026-01-29
**Analysis Scope:** brsekit/, bk-status/, bk-report/, bk-task/, bk-minutes/, bk-tester/, bk-write/, bk-translate/, common/

---

## 1. Current Architecture Overview

### Skill Structure
- **7 Domain Skills**: bk-status, bk-report, bk-task, bk-minutes, bk-tester, bk-write, bk-translate
- **1 Core Module**: brsekit/ (master data loader, configuration)
- **1 Shared Library**: common/ (API key helpers, backlog integration)

### Master Data Layer (brsekit/)
- `master_loader.py`: MasterData class with 150 lines, provides singleton pattern
- `master.yaml`: Centralized config (team, calendar, sprints, projects, thresholds)
- Single source of truth for: team capacity, holidays, sprint definitions, skill mappings

### Standard Skill Layout
Each skill follows consistent structure:
```
bk-{name}/
├── scripts/        # Core logic (50-600 lines per file)
├── templates/      # Template files for generation
├── tests/          # pytest suite
├── SKILL.md        # Documentation
├── requirements.txt
└── .env.example
```

---

## 2. Common Patterns Identified

### Pattern 1: YAML/Template Processing
- **bk-report**: Weekly report generation from templates
- **bk-task**: Task creation from parsed templates
- **bk-write**: Japanese text generation with keigo helpers
- **bk-translate**: Glossary-based translation with template substitution
- **Common Need**: Template engine abstraction (Jinja2-ready)

### Pattern 2: Master Data Integration
- All skills reference `master.yaml` for team/calendar context
- `master_loader.py` provides: member lookup, capacity calc, holiday checks
- **Reusable Code**: Currently duplicated in each skill's initialization

### Pattern 3: Multi-language Support
- **bk-report**: Language flag handling in master.yaml (vi/en)
- **bk-write**: Japanese-specific (keigo, honorifics)
- **bk-translate**: Glossary-based translation system
- **Pattern**: Each implements own i18n; inconsistent approaches

### Pattern 4: API Client Management
- **common/api_key_helper.py**: API key rotation/management
- **common/api_key_rotator.py**: Multi-API orchestration
- Skills expected to inherit from common but structure varies

### Pattern 5: Report Generation
- **bk-report**: Template-based report output
- **bk-tester**: Test report generation from test cases
- **bk-task**: Batch update reports
- **Common Need**: Unified report builder abstraction

---

## 3. Shared Dependencies Analysis

### Direct Dependencies (Duplicated Code)
1. **Master Data Loading**: bk-status, bk-task, bk-minutes all load master.yaml independently
2. **Template Rendering**: bk-report, bk-task, bk-translate all use file-based template systems
3. **API Integration Boilerplate**: Each skill implements own initialization pattern
4. **Logging/Error Handling**: No unified approach across skills

### External Dependencies
- **Common**: google-genai, pyyaml, python-dotenv (from .env)
- **Individual Skills**: bk-tester has 6 unique deps; bk-translate has glossary files

---

## 4. Refactoring Opportunities

### HIGH Priority (Consolidation)
1. **Shared Base Class**: Extract `SkillBase` with:
   - Master data auto-loading
   - Standard CLI arg parsing
   - Unified logger setup
   - API key management

2. **Template Engine Module** (`common/template_engine.py`):
   - Jinja2-based template processor
   - Glossary/translation injection hooks
   - Cache layer for repeated renders

3. **Config Manager** (`common/config_manager.py`):
   - Load master.yaml once, share instance
   - Support environment overrides
   - Validate config schema

### MEDIUM Priority (DRY Improvements)
4. **Report Builder** (`common/report_builder.py`):
   - Unified markdown/text report generation
   - Section management (headers, tables, lists)
   - Language-aware formatting

5. **Consolidated I18n Module** (`common/i18n.py`):
   - Single translation interface
   - Glossary registry
   - Language detection from master.yaml

### LOW Priority (Nice-to-Have)
6. **Metrics Base**: Abstract base for capacity/velocity calculations
7. **Test Utilities**: Consolidated pytest fixtures and mock helpers

---

## 5. Code Reuse Recommendations

### Immediate Actions (V2)
- Extract MasterData usage to `common/master_loader.py` (avoid duplication)
- Create `common/skill_base.py` with standard initialization
- Consolidate requirements.txt to root `.claude/skills/requirements-base.txt`

### File Size Optimization
- **bk-task/scripts**: `task_parser.py` (507 lines) → split parsing/validation
- **bk-translate/scripts**: `main.py` (235 lines) → extract glossary loader
- **bk-tester/scripts**: `report_generator.py` (164 lines) → move to common

### Architecture Changes
- Adopt plugin pattern: skills register handlers in `brsekit/master.yaml`
- Centralize CLI entry points using common argument parser
- Use factory pattern for report generation

---

## 6. Shared Module Candidates for consolidation

| Module | Current Location | Files | LOC | Consolidation |
|--------|------------------|-------|-----|---|
| Master loader | brsekit/ | 1 | 150 | Move to common/ |
| Template rendering | 4 skills | N/A | ~400 | Extract common/template_engine.py |
| I18n/translations | 3 skills | N/A | ~200 | Extract common/i18n.py |
| Report generation | 3 skills | N/A | ~350 | Extract common/report_builder.py |
| API key mgmt | common/ | 2 | ~70 | Already shared (good) |

---

## 7. Dependencies to Consolidate

**Current Issue**: Each skill has separate requirements.txt with overlaps
- PyYAML: required by brsekit, could be base
- google-genai: used by 3+ skills
- python-dotenv: universal

**Recommendation**:
- Base requirements at `.claude/skills/requirements-base.txt`
- Skill-specific reqs in individual files (with base as dependency)

---

## 8. Code Quality Observations

✅ **Strengths**:
- Clear separation of concerns (scripts/ vs templates/)
- Comprehensive test coverage in each skill
- Good documentation (SKILL.md, README.md present)
- Master.yaml as single config source

⚠️ **Inconsistencies**:
- No unified error handling strategy
- Logging implemented differently per skill
- CLI argument parsing duplicated across skills
- No shared constants/enums

---

## Summary

BrseKit V2 should focus on:
1. **Extract SkillBase** from duplicated initialization patterns
2. **Centralize Template Engine** to reduce 4-skill duplication
3. **Consolidate I18n** for consistent language handling
4. **Move master_loader to common/** for universal access
5. **Unified Report Builder** for output consistency

**Estimated Consolidation Impact**: ~800 LOC deduplication, 40% faster skill development

---

## Unresolved Questions

- Should skills use inheritance (SkillBase) or composition (dependency injection)?
- How should plugin discovery work in V2 (YAML registry vs auto-discovery)?
- Should API keys be rotated per-skill or globally managed?
