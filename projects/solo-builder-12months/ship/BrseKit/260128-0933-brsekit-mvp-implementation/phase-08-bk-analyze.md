# Phase 8: bk-analyze - BA Assistant with Business Context

## Overview
- **Priority:** P2
- **Status:** pending
- **Skill:** `bk-analyze`
- **Approach:** TDD
- **Dependencies:** project-context.yaml (business context)

## Pain Point
> "BrSE kiêm BA, skill BA yếu. Cần hỗ trợ phân tích requirements, hiểu business khách hàng"

## Input
```
/bk-analyze <customer-email.txt>       # Analyze customer communication
/bk-analyze <requirements.md>          # Analyze existing docs
/bk-analyze --project                  # Analyze entire project context
/bk-analyze feature "<description>"    # Analyze specific feature
/bk-analyze feature --from-issue PROJ-123

# Focus outputs
/bk-analyze <input> --questions        # Only clarification questions
/bk-analyze <input> --stories          # Only user stories
/bk-analyze <input> --requirements     # Only requirements list
```

## Expected Output
- Full BA toolkit: Questions + User Stories + Requirements
- Business-level context understanding
- Risk/consideration identification

## Key Features

### 1. Input Sources

| Source | Description |
|--------|-------------|
| Customer communication | Email, chat, meeting notes |
| Existing Backlog issues | Analyze issues in project |
| Documents | Specs, requirements docs |
| Feature description | Free text or from issue |

### 2. Context Loading

```
┌─────────────────────────────────────┐
│        Context Loader               │
├─────────────────────────────────────┤
│ 1. Load project-context.yaml        │
│    - Customer business info         │
│    - Project type & methodology     │
│    - Focus areas                    │
│                                     │
│ 2. Load Backlog project overview    │
│    - Existing issues                │
│    - Milestones                     │
│    - Team members                   │
│                                     │
│ 3. Build analysis context           │
└─────────────────────────────────────┘
```

### 3. Analysis Engine

| Analysis Type | Description |
|---------------|-------------|
| **Gap detection** | What's missing? Incomplete requirements? |
| **Ambiguity detection** | Vague terms? Multiple interpretations? |
| **Business alignment** | Does this align with customer's business? |
| **Risk identification** | Technical/business risks? |

### 4. Output: Full BA Report

```markdown
# Feature Analysis: Bulk Export CSV

## 📊 BUSINESS CONTEXT
- **Customer:** ABC Corp (Manufacturing)
- **Business Goal:** Reduce manual data entry, speed up reporting
- **Project Type:** Project-based (Waterfall)

## ❓ CLARIFICATION QUESTIONS (5)

### High Priority
1. **Max records per export?**
   - Impact: Performance, UX design
   - Suggest: Start with 10K limit

2. **Which fields are required in export?**
   - Impact: Data mapping, security (PII?)
   - Suggest: Provide field checklist

### Medium Priority
3. **Schedule export or on-demand only?**
4. **Export format: CSV only or also Excel?**
5. **Who can access this feature? (RBAC)**

## 📝 USER STORIES (3)

### Core Stories
```
As an admin,
I want to export transaction data to CSV,
So that I can import into our accounting system.
```

```
As a manager,
I want to filter data before export,
So that I get only relevant records.
```

### Edge Case Stories
```
As a user,
I want to see export progress,
So that I know how long to wait.
```

## 📋 REQUIREMENTS

### Functional Requirements
| ID | Description | Priority |
|----|-------------|----------|
| FR1 | Export up to 10K records | Must |
| FR2 | Select columns for export | Must |
| FR3 | Filter by date range | Should |
| FR4 | Schedule recurring export | Could |

### Non-Functional Requirements
| ID | Description | Target |
|----|-------------|--------|
| NFR1 | Export completion time | <30s for 10K records |
| NFR2 | Concurrent exports | 3 per user |

## ⚠️ RISKS & CONSIDERATIONS

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Large dataset memory | High | Stream processing, pagination |
| Timeout on slow export | Medium | Background job, notify on complete |

### Business Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| PII in export | High | Add permission check, audit log |
| Scope creep (Excel, PDF) | Medium | Document as CR if requested |

## 🔗 RELATED ISSUES
- PROJ-45: Data export API (backend)
- PROJ-67: Export UI component
```

### 5. Context-Aware Analysis

**Project-based (Waterfall):**
- Highlight CR/scope implications
- Check budget/schedule alignment
- Formal requirements format

**Labor (Agile):**
- Focus on sprint-sized stories
- Priority-based ordering
- Flexible requirements

## Architecture

```
brsekit/skills/bk-analyze/
├── SKILL.md
├── scripts/
│   ├── main.py
│   ├── context_builder.py      # Build analysis context
│   ├── requirement_parser.py   # Parse input
│   ├── gap_analyzer.py         # Detect gaps, ambiguities
│   ├── story_generator.py      # Generate user stories
│   ├── question_generator.py   # Generate clarification questions
│   └── report_generator.py     # Generate BA report
└── tests/
    ├── fixtures/
    │   ├── sample_customer_email.txt
    │   ├── sample_feature_request.txt
    │   └── expected_analysis_output.md
    ├── test_context_builder.py
    ├── test_gap_analyzer.py
    └── test_story_generator.py
```

## Key Test Cases

1. Load project context correctly
2. Parse customer email → extract requirements
3. Detect gaps and ambiguities
4. Generate clarification questions (prioritized)
5. Generate user stories (core + edge cases)
6. Generate requirements (FR + NFR)
7. Context-aware: different output for waterfall vs agile

## Dependencies

- `lib/context_loader.py`: Load project-context.yaml
- `lib/backlog_client.py`: Fetch existing issues
- Nulab Backlog API: Get project info, issues

## Success Criteria

- [ ] Load and understand business context
- [ ] Generate relevant clarification questions
- [ ] Generate user stories từ feature description
- [ ] Generate structured requirements (FR + NFR)
- [ ] Identify risks and considerations
- [ ] Context-aware output based on project type

## Detailed plan: TBD after Phase 7 (bk-minutes) complete
