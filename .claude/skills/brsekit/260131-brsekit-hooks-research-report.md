# BrseKit Hooks Research Report

**Date:** 2026-01-31
**Context:** Nghiên cứu cơ chế hooks của Claude Code để áp dụng cho BrseKit
**Goal:** Thiết kế hooks cho BrseKit multi-project toolkit

---

## 1. Background: Tại sao cần Hooks?

### Vấn đề hiện tại của BrseKit

```
┌─────────────────────────────────────────────────────────────┐
│  User mở Claude Code                                         │
│  → Claude KHÔNG BIẾT có projects nào                         │
│  → Mỗi command phải chỉ định --project                       │
│  → Subagents không biết vault path, API keys                 │
│  → Không có context chung giữa các skill                     │
└─────────────────────────────────────────────────────────────┘
```

### Giải pháp: Hooks inject context tự động

```
┌─────────────────────────────────────────────────────────────┐
│  User mở Claude Code                                         │
│  → Hook chạy: Phát hiện projects, load active project        │
│  → Claude biết: "Có 3 projects: HB21373, HB21456, HB21789"  │
│  → Subagents biết: vault path, glossary path, API keys       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Phân tích ClaudeKit Hooks

### 2.1 Session Init Hook (session-init.cjs)

**Mục đích:** Chuẩn bị context cho session mới

**Flow:**
1. Đọc stdin JSON từ Claude Code: `{ source: "startup", session_id: "..." }`
2. Load config từ `.claude/.ck.json`
3. Detect project info (type, package manager, framework)
4. Resolve active plan từ session state hoặc branch name
5. Write env vars vào CLAUDE_ENV_FILE (cho Bash commands)
6. Output context ra stdout (cho Claude đọc)

**Output types:**

| Method | Ai đọc | Ví dụ |
|--------|--------|-------|
| `console.log()` | Claude trực tiếp | Context, coding guidelines |
| `writeEnv()` | Bash commands | `$CK_PLANS_PATH` |
| `writeSessionState()` | Hooks khác | Active plan persistence |

### 2.2 Subagent Init Hook (subagent-init.cjs)

**Mục đích:** Inject context tối giản cho subagents

**Key insight:**
- **KHÔNG đọc từ CLAUDE_ENV_FILE**
- **TÍNH LẠI** từ config và git (vì env vars không propagate)
- Output ~200 tokens (tối ưu context window)

**Flow:**
1. Đọc stdin: `{ agent_type: "planner", session_id: "..." }`
2. Load config trực tiếp
3. Resolve paths từ CWD và git
4. Output compact context

---

## 3. Thông tin cần thiết cho BrseKit

### 3.1 So sánh ClaudeKit vs BrseKit

| Thông tin | ClaudeKit | BrseKit | Lý do |
|-----------|-----------|---------|-------|
| Project Type | ✅ node/python | ❌ | Không build code |
| Package Manager | ✅ npm/pnpm | ❌ | Không build code |
| Framework | ✅ nextjs/react | ❌ | Không build code |
| Git Branch | ✅ | ⚠️ Optional | Có thể dùng để detect project |
| Coding Level | ✅ | ❌ | Không dạy code |
| Active Plan | ✅ | → Active Project | Tương đương nhưng khác tên |
| Reports Path | ✅ | ✅ | Lưu status/weekly reports |
| **Projects List** | ❌ | ✅ **CRITICAL** | Core feature |
| **Active Project** | ❌ | ✅ **CRITICAL** | Focus project |
| **API Keys** | ❌ | ✅ | BACKLOG, SLACK, GEMINI |
| **Vault Path** | ❌ | ✅ | SQLite memory |
| **Glossary Path** | ❌ | ✅ | Translation terms |

### 3.2 BrseKit-specific Context

```yaml
# Session context cần inject
projects:
  available: [HB21373, HB21456, HB21789]
  active: HB21373  # hoặc null

paths:
  projects_dir: ./projects
  knowledge_dir: ./knowledge
  vault_template: projects/{name}/vault/vault.db
  glossary_template: projects/{name}/glossary.json

env_fallback:
  1. projects/{name}/.env       # Project-specific
  2. ./.env                     # Workspace-level
  3. System environment         # Global

glossary_fallback:
  1. projects/{name}/glossary.json
  2. knowledge/glossary-it-terms.json
```

---

## 4. Proposed Implementation

### 4.1 File Structure

```
.claude/
├── hooks/
│   ├── brsekit-session-init.cjs    # NEW: BrseKit session hook
│   ├── brsekit-subagent-init.cjs   # NEW: BrseKit subagent hook
│   └── lib/
│       ├── ck-config-utils.cjs     # Existing ClaudeKit utils
│       └── bk-config-utils.cjs     # NEW: BrseKit utils
└── settings.json                    # Add BrseKit hooks
```

### 4.2 Session Init Hook

```javascript
/**
 * BrseKit Session Init Hook
 *
 * Purpose: Inject multi-project context at session start
 * Output: ~300 tokens
 */

// Key functions needed:
// - detectProjects(): Scan projects/ directory
// - loadActiveProject(): Read from session state
// - loadProjectEnv(): Load .env with fallback chain
// - buildProjectContext(): Format context for Claude
```

**Output format:**

```
BrseKit Session startup. Projects: 3 available

## Active Project: HB21373
- Vault: projects/HB21373/vault/
- Glossary: 45 terms loaded
- Backlog: Connected (yourspace.backlog.com)

## Available Projects
- HB21373 (active)
- HB21456
- HB21789

## Quick Commands
- /bk-track status HB21373
- /bk-morning HB21373
- /bk-recall search "query" --project HB21373
```

### 4.3 Subagent Init Hook

```javascript
/**
 * BrseKit Subagent Init Hook
 *
 * Purpose: Minimal context for subagents
 * Output: ~100 tokens
 */
```

**Output format:**

```
## BrseKit Context
- Agent: researcher
- Project: HB21373
- Vault: projects/HB21373/vault/vault.db
- Glossary: projects/HB21373/glossary.json
- API: BACKLOG_API_KEY available
```

### 4.4 Settings Configuration

```json
// .claude/settings.json additions
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          { "type": "command", "command": "node .claude/hooks/brsekit-session-init.cjs" }
        ]
      }
    ],
    "SubagentStart": [
      {
        "matcher": "*",
        "hooks": [
          { "type": "command", "command": "node .claude/hooks/brsekit-subagent-init.cjs" }
        ]
      }
    ]
  }
}
```

---

## 5. Open Questions

### 5.1 Architecture Decisions

1. **Separate hooks hay extend ClaudeKit hooks?**
   - Option A: Riêng biệt (brsekit-session-init.cjs)
   - Option B: Extend (thêm vào session-init.cjs)
   - **Recommendation:** Option A - tách biệt để maintainability

2. **Active project persistence:**
   - Option A: Session state (như ClaudeKit active plan)
   - Option B: File `.active` trong projects/
   - Option C: Luôn require explicit `--project`
   - **Current design:** Option C (explicit) - theo SKILL.md

3. **API keys handling:**
   - Có nên expose vào CLAUDE_ENV_FILE?
   - Risk: Claude có thể log/expose keys
   - **Recommendation:** Chỉ flag "available/missing", không expose values

### 5.2 Integration Questions

1. Làm sao phân biệt khi chạy trong BrseKit context vs ClaudeKit context?
2. Có cần namespace env vars? (BK_ vs CK_)
3. Hooks có nên check existence của projects/ directory?

### 5.3 Performance Considerations

1. Scanning projects/ directory có slow không nếu có nhiều projects?
2. SQLite vault connection check có cần thiết ở session init?
3. API connectivity check (Backlog) nên làm ở đâu?

---

## 6. Next Steps

1. [ ] Review và finalize architecture decisions
2. [ ] Implement `bk-config-utils.cjs` với core functions
3. [ ] Implement `brsekit-session-init.cjs`
4. [ ] Implement `brsekit-subagent-init.cjs`
5. [ ] Update `.claude/settings.json` với BrseKit hooks
6. [ ] Test với multi-project setup thực tế
7. [ ] Document trong BrseKit SKILL.md

---

## 7. References

- [ClaudeKit session-init.cjs](.claude/hooks/session-init.cjs)
- [ClaudeKit subagent-init.cjs](.claude/hooks/subagent-init.cjs)
- [ClaudeKit config utils](.claude/hooks/lib/ck-config-utils.cjs)
- [BrseKit SKILL.md](.claude/skills/brsekit/SKILL.md)
- [Claude Code Hooks Docs](https://docs.claude.com/en/docs/claude-code/hooks)
