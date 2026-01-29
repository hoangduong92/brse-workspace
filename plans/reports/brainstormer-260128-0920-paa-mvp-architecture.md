# PAA (Project AI Assistant) - Brainstorm Report

**Date:** 2026-01-28
**Author:** Solution Brainstormer
**Status:** Completed

---

## Executive Summary

PAA nhằm giảm workload cho BrSE trong offshore teams Japan-Vietnam. Sau khi phân tích kỹ, recommend **build PAA như ClaudeKit skill extension** thay vì standalone app, cho phép ship MVP trong 3 ngày.

**Core Insight:** Đã có `backlog` skill với Nulab API client hoạt động tốt. PAA nên leverage existing infrastructure, không build lại từ đầu.

---

## A. MVP Architecture (3 Days)

### Realistic Scope Assessment

**Brutally Honest:** 3 ngày để build production-ready tool với 3 integrations (Slack, Backlog, GDrive) là **không khả thi** nếu build from scratch.

**Solution:** Build PAA as orchestration layer trên existing skills.

### Recommended Architecture

```
┌─────────────────────────────────────────────────┐
│                 PAA Skill                        │
│  /paa report | /paa write | /paa review         │
├─────────────────────────────────────────────────┤
│           Existing Infrastructure                │
│  ┌─────────────┐  ┌─────────────┐               │
│  │   backlog   │  │  copywriting│               │
│  │   skill     │  │   skill     │               │
│  └─────────────┘  └─────────────┘               │
├─────────────────────────────────────────────────┤
│              ClaudeKit Core                      │
│  (hooks, agents, skills framework)               │
└─────────────────────────────────────────────────┘
```

### 3-Day Deliverables

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1 | `/paa report` | Progress report generation từ Backlog data |
| 2 | `/paa write` + `/paa review` | Japanese business writing templates |
| 3 | `/paa translate` + Testing | JA↔VI translation, documentation |

### What to Cut (Defer to Later)

- ❌ Slack integration → Week 2
- ❌ Google Drive sync → Week 2
- ❌ Tester/BA features → Month 2
- ❌ Team memory/context → Month 2+
- ❌ Evaluation framework → Production phase

### Technical Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Core Framework | ClaudeKit Skills | Existing infra, proven |
| Language | Python + SKILL.md | Match existing `backlog` skill |
| API Client | Existing `nulab_client.py` | Already has rate limiting, error handling |
| AI Backend | Claude API (existing) | No additional setup |

---

## B. Feature Prioritization Matrix

### P0 - MVP (3 Days) - BrSE Only

| Feature | Description | Implementation |
|---------|-------------|----------------|
| `/paa report` | Auto-generate progress report từ Backlog | Query issues → summarize → format markdown |
| `/paa write` | Japanese business writing assistant | Templates + AI polish |
| `/paa review` | Review document trước gửi khách | Check tone, grammar, completeness |
| `/paa translate` | JA↔VI translation với context | Leverage existing in-conversation translation |

### P1 - Week 2-4 (Should Have)

| Feature | Description | Dependency |
|---------|-------------|------------|
| Slack notification | Post reports to channel | Slack MCP server |
| Google Docs read | Pull specs từ shared docs | GDrive API |
| Daily standup summary | Aggregate team updates | Backlog + Slack data |
| Template library | Pre-built report formats | User feedback |

### P2 - Month 2+ (Nice to Have)

| Feature | Description | Complexity |
|---------|-------------|------------|
| Tester support | Test case generation | Domain knowledge needed |
| BA templates | Requirements checklists | Template design |
| Team memory | Shared context across sessions | RAG implementation |
| Multi-user access | Role-based permissions | Auth layer |
| Evaluation framework | Workflow optimization testing | Metrics design |

---

## C. Integration Strategy

### Backlog (P0 - MVP)

**Current capability:** Full CRUD operations via `nulab_client.py`
- `get_issue()`, `create_issue()`, `add_comment()`
- Rate limiting (1s between requests), retry logic
- Attachment handling

**New capability needed:**
- Bulk issue fetch (list issues by status/assignee)
- Progress aggregation (% done, blockers)

**Recommendation:** **Read-write** - extend existing client

```python
# Add to nulab_client.py
def get_issues_by_project(self, project_id: str, status: list = None) -> list[Issue]:
    """Fetch all issues for progress report"""
    params = {"projectId[]": project_id}
    if status:
        params["statusId[]"] = status
    response = self._request("GET", "/issues", params=params)
    return [Issue.from_dict(i) for i in response.json()]
```

### Slack (P1 - Week 2)

**Available options:**
1. [Slack MCP Server](https://mcpservers.org/servers/atlasfutures/claude-mcp-slack) - read messages, post replies
2. [Claude Code Slack Bot](https://github.com/mpociot/claude-code-slack-bot) - standalone integration
3. [Composio Slack Toolkit](https://composio.dev/toolkits/slack/framework/claude-code) - managed service

**Recommendation:** Slack MCP Server (option 1) - fits existing MCP architecture

**Use cases:**
- Post daily report to #project channel
- Alert on blocked tickets
- Respond to @mention questions

### Google Workspace (P1 - Week 2)

**Priority order:**
1. **Google Docs** (read-only first) - pull specs, requirements
2. **Google Sheets** - timeline tracking, resource allocation
3. **Google Slides** - not MVP priority

**Sync strategy:**
```
Google Drive API → Download to ./data/gdrive-cache/ → Process locally
                   ↑
           Triggered by /paa sync command (manual) or cron (auto)
```

**Security note:** Cache files in container, not persistent storage. Clear after 24h.

---

## D. Data Architecture

### Local Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Container                      │
├─────────────────────────────────────────────────────────┤
│  ./data/                                                 │
│  ├── gdrive-cache/     # Synced from Google Drive       │
│  │   ├── specs/                                          │
│  │   └── requirements/                                   │
│  ├── reports/          # Generated reports              │
│  │   ├── 2026-01-28-progress.md                         │
│  │   └── ...                                            │
│  └── sessions/         # Session state (context)        │
│      └── brse-session.json                              │
├─────────────────────────────────────────────────────────┤
│  Read-only mount: /host-data (original files)           │
│  Write: only to ./data/ inside container                │
└─────────────────────────────────────────────────────────┘
```

### Context/Memory Management

**MVP (Simple):**
```json
// sessions/brse-session.json
{
  "project_id": "HB21373",
  "last_report_date": "2026-01-27",
  "key_decisions": [
    {"date": "2026-01-25", "topic": "API design", "decision": "REST over GraphQL"}
  ],
  "blockers": ["DB migration pending approval"]
}
```

**Production (RAG-based):**
- Vector store (ChromaDB local) for document search
- Conversation history với sliding window
- Per-user context isolation

### Security Boundaries

| Concern | Mitigation |
|---------|------------|
| Data leakage | Container isolation, no persistent write to host |
| API key exposure | `.env` file, never commit |
| Deletion prevention | PreToolUse hook (existing) |
| Access control | MVP: single user; Production: JWT tokens |

---

## E. Evaluation Framework (Production Phase)

### Metrics to Measure "BrSE Effectiveness"

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Time per weekly report | 2 hours | 30 min | Self-reported |
| Report quality score | N/A | 4/5 | Manager review |
| Response time to customer | 4 hours | 1 hour | Slack timestamps |
| Errors in documents | 5/week | 1/week | Revision count |

### Test Case Structure

Reference: [Anthropic Eval Guide](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

```yaml
# evals/report_generation.yaml
name: Progress Report Generation
category: document_generation
cases:
  - id: "report-001"
    input:
      project_id: "HB21373"
      date_range: "2026-01-21 to 2026-01-27"
    expected:
      sections: ["Summary", "Completed", "In Progress", "Blockers", "Next Week"]
      mentions_all_closed_tickets: true
      japanese_tone: "keigo"
    scoring:
      completeness: 0.4
      accuracy: 0.4
      tone: 0.2
```

### A/B Testing Workflow Approach

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Workflow A │    │  Workflow B │    │  Workflow C │
│  (Baseline) │    │ (New prompt)│    │ (New model) │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────────────────────────────────────────┐
│              Same Test Cases                     │
│         (evals/report_generation.yaml)           │
└──────────────────────────────────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────────────────────────────────────────┐
│              Scoring & Comparison                │
│  Workflow A: 78% | Workflow B: 82% | C: 75%     │
└─────────────────────────────────────────────────┘
```

---

## F. Risk Analysis

### 3-Day MVP Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | Delay | Strict P0 only, no feature additions |
| Backlog API issues | Medium | Blockers | Fallback to manual ticket input |
| AI output quality | Medium | User trust | 20% error rate acceptable, iterate |
| Testing time squeeze | High | Bugs in prod | Accept rough edges, fix post-launch |

### Scale Risks (Production)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Context limits | High | Incomplete responses | Chunking, summarization |
| Multi-user conflicts | Medium | Data corruption | Per-user session files |
| API costs | Medium | Budget overrun | Usage monitoring, caching |
| Integration fragility | High | Feature breakage | Circuit breakers, fallbacks |

### Security Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Sensitive data in prompts | High | Data leak | Data sanitization pre-send |
| Container escape | Low | Host compromise | Minimal permissions, no sudo |
| API key theft | Low | Account takeover | Rotate keys, monitor usage |

---

## G. Competitive Positioning

### Existing Tools in This Space

| Tool | Strength | Weakness for BrSE Use Case |
|------|----------|---------------------------|
| [ClickUp Brain](https://clickup.com) | All-in-one PM + AI | No Backlog integration, overkill |
| [Monday.com AI](https://monday.com) | Sprint forecasting | No JA↔VI translation |
| [Fireflies.ai](https://fireflies.ai) | Meeting transcription | No PM integration |
| [Glean](https://www.glean.com) | Enterprise search | Too expensive, not PM-focused |

### PAA Unique Value Proposition

```
"PAA is the only AI assistant purpose-built for Japan-Vietnam
offshore teams, with native Nulab Backlog integration and
JA↔VI translation optimized for technical contexts."
```

**Differentiators:**
1. **Backlog-native** - No other AI tool integrates with Nulab Backlog
2. **JA↔VI specialized** - Not generic translation, understands IT context
3. **BrSE workflow** - Built for bridge engineer pain points, not generic PM
4. **On-premise option** - Data stays in container, not cloud

---

## H. Implementation Roadmap

### Week 1 (MVP)

```
Day 1: /paa report
├── Extend nulab_client.py với get_issues_by_project()
├── Create report generation logic
├── Output: markdown report với Summary, Progress, Blockers
└── Test với real Backlog project

Day 2: /paa write + /paa review
├── Japanese business writing templates
├── Document review workflow (grammar, tone, completeness)
└── Keigo level selection (formal/semi-formal)

Day 3: /paa translate + Polish
├── JA↔VI translation với technical term preservation
├── Documentation
├── Basic testing
└── Ship MVP
```

### Week 2-4 (P1)

```
Week 2: Integrations
├── Slack MCP server setup
├── Google Docs read-only access
└── Daily summary automation

Week 3-4: Refinement
├── Template library expansion
├── User feedback incorporation
├── Error rate reduction (target: <10%)
```

### Month 2+ (P2)

```
├── Tester support (test case generation)
├── BA templates
├── Multi-user access
├── Evaluation framework
└── Team memory (RAG)
```

---

## I. Recommended Next Steps

1. **Immediate (Today):** Finalize P0 scope, no additions
2. **Day 1:** Implement `/paa report` - highest BrSE value
3. **Day 2:** Implement `/paa write` + `/paa review`
4. **Day 3:** Implement `/paa translate`, test, document
5. **Week 2:** Add Slack integration, gather feedback

---

## Unresolved Questions

1. **Backlog project scope:** MVP chỉ support 1 project hay multiple?
2. **Report language:** Output report bằng JA, VI, hay cả hai?
3. **Review approval flow:** AI review cần human approval trước gửi?
4. **Template customization:** User có thể custom templates hay fixed?
5. **Error handling UX:** Khi AI sai, fallback UI như thế nào?

---

## Sources

- [Best AI Project Management Tools 2026 - Zapier](https://zapier.com/blog/best-ai-project-management-tools/)
- [AI in Project Management - Monday.com](https://monday.com/blog/project-management/ai-project-management/)
- [Agentic Software Project Management Vision - arXiv](https://arxiv.org/html/2601.16392)
- [Slack MCP Server](https://mcpservers.org/servers/atlasfutures/claude-mcp-slack)
- [Claude Code Slack Bot](https://github.com/mpociot/claude-code-slack-bot)
- [Composio Slack Toolkit](https://composio.dev/toolkits/slack/framework/claude-code)
- [Demystifying Evals for AI Agents - Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
