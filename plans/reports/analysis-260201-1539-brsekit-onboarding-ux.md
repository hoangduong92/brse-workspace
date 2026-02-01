# BrseKit Onboarding UX Analysis & Redesign

**Date**: 2026-02-01
**Context**: Comparing BrseKit onboarding with ClaudeKit reference implementation

---

## Problem Statement

Current BrseKit onboarding feels like a "thick tutorial from last century":
1. Shows installation commands for user to run manually
2. No interactive wizard
3. Doesn't auto-discover project info
4. Focuses on "how to install" instead of "what can I do for you"

---

## ClaudeKit Reference Analysis

### What Works Well

1. **ck-help.py Pattern**:
   - Intent detection (`detect_intent()`)
   - Task recommendations based on keywords
   - Category workflows with step-by-step guidance
   - Disambiguation when multiple intents match
   - LLM output type markers for presentation

2. **Workflow-First Approach**:
   ```
   # Example: User asks "how do I start"

   BAD (BrseKit current):
   "Step 1: cd .claude/skills
    Step 2: python -m venv .venv
    Step 3: pip install..."

   GOOD (ClaudeKit):
   "What do you want to do?
    1. Implement feature → /cook
    2. Fix bug → /fix
    3. Setup project → /bootstrap
    Reply with number or describe your task"
   ```

3. **Category Guides**:
   ```python
   CATEGORY_GUIDES = {
       "fix": {
           "title": "Fixing Issues",
           "workflow": [
               ("Start", "`/fix` 'describe issue'"),
               ("If stuck", "`/debug` 'more details'"),
               ("Verify", "`/test`"),
           ],
           "tip": "Include error messages for better results"
       }
   }
   ```

---

## Proposed BrseKit Redesign

### 1. Interactive Onboarding Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    BrseKit Onboarding                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Phase 1: Environment Check (AUTO)                          │
│  ├─ Check Python version                                    │
│  ├─ Check/create venv                                       │
│  ├─ Install dependencies (pip install -r requirements.txt) │
│  └─ Result: ✓ Environment ready                            │
│                                                             │
│  Phase 2: Credentials (INTERACTIVE)                         │
│  ├─ Check existing .env                                     │
│  ├─ If missing: "Paste your Backlog API key below"         │
│  └─ Validate credentials with API call                     │
│                                                             │
│  Phase 3: Project Discovery (AUTO)                          │
│  ├─ Fetch Backlog project info via API                     │
│  ├─ Get project members, categories, milestones            │
│  └─ Store in .bk.json / vault                              │
│                                                             │
│  Phase 4: Project Context (INTERACTIVE)                     │
│  ├─ "What's unique about this project?"                    │
│  │   - Customer personality (strict/flexible)              │
│  │   - Communication style (formal/casual)                 │
│  │   - Key deadlines (PoC in 3 months)                     │
│  └─ Store in project config                                │
│                                                             │
│  Phase 5: Quick Start (GUIDE)                               │
│  ├─ "What do you want to do now?"                          │
│  │   1. Check project status → /bk-track status            │
│  │   2. Parse tasks from email → /bk-capture               │
│  │   3. Search project context → /bk-recall                │
│  │   4. Explore more skills → /brsekit help                │
│  └─ Run selected action immediately                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. New Help Response Pattern (bk-help.py)

Similar to ck-help.py but for BrSE workflows:

```python
TASK_MAPPINGS = {
    "track": ["status", "progress", "report", "weekly", "tiến độ", "báo cáo"],
    "capture": ["task", "meeting", "email", "parse", "minutes", "議事録"],
    "spec": ["requirement", "test", "analyze", "yêu cầu", "テスト"],
    "recall": ["search", "find", "context", "tìm", "検索"],
    "convert": ["translate", "dịch", "翻訳", "JA", "VI"],
    "write": ["email", "document", "keigo", "敬語", "ビジネス"],
    "morning": ["brief", "unread", "overnight", "朝会"],
}

CATEGORY_GUIDES = {
    "track": {
        "title": "Project Tracking & Reporting",
        "workflow": [
            ("Check health", "`/bk-track status`"),
            ("Weekly report", "`/bk-track report --format pptx`"),
            ("Quick summary", "`/bk-track summary`"),
        ],
        "tip": "Use --threshold 2 for stricter late detection"
    },
    "capture": {
        "title": "Task & Meeting Parser",
        "workflow": [
            ("Parse task", "`/bk-capture task 'text here'`"),
            ("Meeting notes", "`/bk-capture meeting transcript.txt`"),
            ("Email tasks", "`/bk-capture email inbox.txt`"),
        ],
        "tip": "Auto-detects JA/EN/VI and extracts deadlines"
    }
}
```

### 3. Key UX Principles

| Principle | Implementation |
|-----------|----------------|
| **Auto-run commands** | Never ask user to run pip/venv commands |
| **Validate then proceed** | Check API key works before moving on |
| **Fetch what's fetchable** | Auto-get project info, members, milestones |
| **Ask only unknowables** | Customer personality, project goals, deadlines |
| **Action-oriented** | "What do you want to DO now?" |
| **Language-aware** | Support JA/VI/EN in help responses |

---

## Implementation Plan

### Phase 1: bk-help.py Script
- Create `scripts/bk-help.py` similar to ck-help.py
- Intent detection for BrSE workflows
- Task recommendations with JA/VI support
- Category guides for each skill

### Phase 2: Interactive Onboarding
- Modify `/bk-init` skill to use interactive wizard
- Auto-run environment setup
- Only ask for API keys via AskUserQuestion
- Auto-fetch and store project info

### Phase 3: CLI Enhancement
- Update `brsekit-cli` post-install handler
- Auto-run install scripts silently
- Show progress instead of instructions
- Verify installation with actual API call

### Phase 4: Response Templates
- Create response templates for common questions
- "How to start" → Interactive wizard, not docs
- "What can you do" → Skill showcase with examples
- "Help with X" → Route to appropriate skill

---

## Files to Modify

1. `experiments/brsekit-starter_v1.2/.claude/skills/brsekit/` - Main skill
2. `experiments/brsekit-starter_v1.2/.claude/scripts/bk-help.py` - New help script
3. `experiments/brsekit-cli/src/commands/init/phases/post-install-handler.ts`
4. `experiments/brsekit-starter_v1.2/.claude/skills/bk-init/` - Onboarding wizard

---

## Success Metrics

1. **User never runs manual commands** for setup
2. **First useful action within 2 minutes** after providing API key
3. **Project context auto-discovered** (members, milestones, categories)
4. **Interactive Q&A for unknowables** (customer style, project goals)
5. **Help responses focus on actions** not installation

---

## Unresolved Questions

1. Should we support multiple Backlog projects per workspace?
2. How to handle API key rotation/expiry?
3. Store customer personality in .bk.json or separate vault?
