# 💡 Product Ideas Backlog

## How to Use This File

1. Add ideas as they come
2. Validate using PM agent framework
3. Move to "Building" when starting
4. Move to "Shipped" when launched
5. Move to "Abandoned" with reason if stopping

---

## Validation Framework (Quick Reference)

| Category   | Score 0-3                                                      |
| ---------- | -------------------------------------------------------------- |
| Pain Point | +2 you have it, +1 talked to others, +1 they pay for solutions |
| Market     | +1 can reach them, +1 search volume, +1 competitors exist      |
| Build      | +1 MVP 2 weeks, +1 uses advantage, +1 one-sentence explain     |

**Total 7-9**: 🟢 Build | **4-6**: 🟡 Validate more | **0-3**: 🔴 Skip

---

## 🟢 Validated Ideas (Ready to Build)

### 1. BrSE Spec Generator

**One-liner**: AI generates technical specs from requirements in JP-VN format

| Criterion  | Score   | Notes                        |
| ---------- | ------- | ---------------------------- |
| Pain Point | 3/3     | I write specs daily, painful |
| Market     | 2/3     | BrSEs exist, hard to reach   |
| Build      | 3/3     | AI + template, 2 weeks       |
| **Total**  | **8/9** | 🟢                           |

**MVP Features**:

- Input requirements (text/voice)
- Generate spec in company format
- JP-VN bilingual output

**Advantage Used**: BrSE experience, JP market

---

### 2. WinActor Scenario Debugger

**One-liner**: Visual debugger for WinActor RPA scenarios

| Criterion  | Score   | Notes                       |
| ---------- | ------- | --------------------------- |
| Pain Point | 3/3     | Debug WinActor is nightmare |
| Market     | 2/3     | Niche but paying customers  |
| Build      | 2/3     | Need WinActor expertise     |
| **Total**  | **7/9** | 🟢                          |

**MVP Features**:

- Import scenario file
- Visual flow diagram
- Highlight error points

**Advantage Used**: RPA domain expertise

---

### 3. BiziJP - Business Keigo AI

**One-liner**: AI helps write proper business Japanese (keigo)

| Criterion  | Score   | Notes                          |
| ---------- | ------- | ------------------------------ |
| Pain Point | 3/3     | Keigo is hard for non-native   |
| Market     | 3/3     | All foreigners in JP need this |
| Build      | 3/3     | LLM + prompts                  |
| **Total**  | **9/9** | 🟢                             |

**MVP Features**:

- Input casual Japanese
- Output proper keigo
- Explain why (learning)

**Advantage Used**: Japanese market knowledge

---

## 🟡 Needs Validation

### 4. Kintone Plugin Starter Kit

**One-liner**: Templates and tools for Kintone plugin development

| Criterion  | Score   | Notes                 |
| ---------- | ------- | --------------------- |
| Pain Point | 2/3     | I had this pain       |
| Market     | ?/3     | Need to research size |
| Build      | 3/3     | Just templates        |
| **Total**  | **?/9** | 🟡                    |

**To Validate**:

- [ ] Search volume for "Kintone plugin"
- [ ] Talk to 3 Kintone devs
- [ ] Check existing solutions

---

### 5. Meeting Notes → Tasks

**One-liner**: AI extracts action items from meeting recordings

| Criterion  | Score   | Notes              |
| ---------- | ------- | ------------------ |
| Pain Point | 2/3     | I have meetings    |
| Market     | 1/3     | Very competitive   |
| Build      | 2/3     | Transcription + AI |
| **Total**  | **5/9** | 🟡                 |

**Concern**: Many competitors (Otter, Fireflies, etc.)

---

## 🔴 Probably Skip

### 6. JP Job Board for VN Devs

**One-liner**: Job marketplace for Vietnamese devs in Japan

| Criterion  | Score   | Notes                  |
| ---------- | ------- | ---------------------- |
| Pain Point | 1/3     | Not my main pain       |
| Market     | 2/3     | Market exists          |
| Build      | 0/3     | Marketplace is complex |
| **Total**  | **3/9** | 🔴                     |

**Reason**: Too complex for solo, not enough advantage

---

## 🚧 Currently Building

_Move ideas here when you start working on them_

<!-- Example:
### BiziJP
- Started: 2025-03-01
- Target ship: 2025-03-15
- Status: Building MVP
- Progress: 60%
-->

---

## 🚀 Shipped

_Move ideas here when launched_

<!-- Example:
### First App Name
- Shipped: 2025-02-15
- URL: https://...
- Revenue: $XX
- Users: XX
- Learnings: [what you learned]
-->

---

## 💀 Abandoned

_Move ideas here if you stop, with reason_

<!-- Example:
### Some Idea
- Abandoned: 2025-XX-XX
- Reason: No market demand
- Time spent: 2 weeks
- Learnings: [what you learned]
-->

---

## Quick Capture

_Dump raw ideas here, validate later_

-# OpenCode — The Agentic-First IDE

> **Your Agents. Your Rules. One IDE.**

---

## What is OpenCode?

OpenCode is the first IDE built from the ground up for the age of AI coding agents. Unlike traditional editors retrofitted with AI features, OpenCode puts **agentic workflows at its core** — letting you work with Claude Code, OpenAI Codex, AmpCode, or Gemini CLI through a single, unified interface.

No more switching between terminal windows. No more context fragmentation. Just seamless AI-powered development.

---

## The Problem

Today's developers face a fragmented AI coding landscape:

- 🔀 **Tool Switching**: Jump between Claude Code in one terminal, Codex in another, your IDE in a third
- 🔒 **Vendor Lock-in**: Cursor locks you into their models. Windsurf locks you into theirs.
- 💸 **Subscription Fatigue**: Already paying for Claude Pro? Too bad — pay again for Cursor's AI features
- 📦 **Bloated Apps**: Electron-based IDEs consuming 500MB+ RAM just to edit text
- 🧠 **Lost Context**: Your agent doesn't know what your other agent did

---

## The Solution

OpenCode introduces **BYOA — Bring Your Own Agent**:

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   ✦ Claude      ◉ Codex      ⚡ Amp      ✦ Gemini          │
│                                                             │
│   One click. Same workspace. Your existing subscriptions.  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Features

### 🔄 Multi-Agent Sessions

Start a session with Claude for architecture planning, switch to Codex for implementation, use Gemini for documentation — all within the same workspace, sharing the same context.

```
Session: "Auth Migration"
├── Agent: Claude (Sonnet)
├── Workspace: [main] → feature/auth-v2
└── Skills: debugging, backend-development, better-auth
```

### 🌳 Git Worktree-Powered Workspaces

Each session can operate on its own git worktree. Run multiple parallel experiments without branch-switching chaos.

```
[main]
├── codex-skill     → [main] on main
├── brainstorm      → [main] on main
└── feature-auth    → [main] on feature/auth
```

### 🛠️ Universal Skills System

Write skills once in `.claude/skills/`, and they automatically sync to `.codex/skills/` and `.gemini/skills/` when you create new sessions. Your coding standards, project context, and custom workflows — available to every agent.

**Built-in Skills:**

- `Debugging` — Systematic root cause investigation
- `Problem-Solving Techniques` — Complexity spirals, simplification cascades
- `backend-development` — Node.js, Python, Go, Rust best practices
- `better-auth` — Authentication patterns and security
- `ai-multimodal` — Vision and multimodal AI integration
- _...and create your own_

### 📋 Integrated Task Management

Agents can create, update, and complete tasks — visible in a persistent To-do panel. Watch your agent work through a feature implementation step by step.

```
To-do List  5/5                              [Task Completed]
──────────────────────────────────────────────────────────────
✓ Set up project dependencies                      COMPLETED
✓ Implement user authentication system             COMPLETED
✓ Create dashboard UI components                   COMPLETED
✓ Write unit tests for API endpoints               COMPLETED
✓ Deploy to staging environment                    COMPLETED
```

### 🔐 Approval-Based Execution

Every shell command requires explicit approval. See exactly what your agent wants to run before it runs.

```
> Bash /bin/zsh -lc 'git status -sb'              ✓ Approved
> Bash /bin/zsh -lc 'git diff --stat'             ✓ Approved
> Bash /bin/zsh -lc 'bun run typecheck'           ✓ Approved
```

### 📂 Native MCP Support

Model Context Protocol is a first-class citizen. Drop a `.mcp.json` in your project root and OpenCode handles the rest.

### 📄 Dual Configuration System

- **`AGENTS.md`** — Universal guidance for any AI agent working in your repo
- **`CLAUDE.md`** — Claude-specific instructions and workflows

---

## Why OpenCode?

| Feature                        | Cursor               | Windsurf             | OpenCode                              |
| ------------------------------ | -------------------- | -------------------- | ------------------------------------- |
| **Multi-Agent**                | ❌ Single provider   | ❌ Single provider   | ✅ Claude, Codex, Amp, Gemini         |
| **Use Existing Subscriptions** | ❌ Pay extra         | ❌ Pay extra         | ✅ Your Claude Pro/ChatGPT Plus works |
| **Built from Scratch**         | ❌ VSCode fork       | ❌ VSCode fork       | ✅ Purpose-built for agents           |
| **Lightweight**                | ❌ ~200MB, 500MB RAM | ❌ ~200MB, 500MB RAM | ✅ ~10MB, <100MB RAM                  |
| **Git Worktrees**              | ❌ Basic             | ❌ Basic             | ✅ Native session integration         |
| **Cross-Agent Skills**         | ❌ N/A               | ❌ N/A               | ✅ Write once, use everywhere         |

---

## Technical Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        OpenCode                                │
├────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Frontend (Vue.js + TypeScript)              │ │
│  │  • Session Management    • Skills Panel                  │ │
│  │  • Code Editor           • File Explorer                 │ │
│  │  • To-do Widget          • Agent Chat UI                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            ↕ IPC                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               Backend (Rust via Tauri)                   │ │
│  │  • Agent Gateway         • Process Management            │ │
│  │  • File System Ops       • Git Worktree Control          │ │
│  │  • Skills Mirroring      • Security & Permissions        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            ↕                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    Agent Gateway                         │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │ │
│  │  │ Claude  │ │ Codex   │ │   Amp   │ │ Gemini  │        │ │
│  │  │  Code   │ │   CLI   │ │  Code   │ │   CLI   │        │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

**Built with Tauri** — Rust-powered backend with native performance. No Electron bloat.

---

## Getting Started

```bash
# Install OpenCode
brew install opencode

# Or download from
https://opencode.dev/download

# Start in your project
cd your-project
opencode .
```

### Quick Setup

1. **Install your preferred agents:**

   ```bash
   npm install -g @anthropic-ai/claude-code
   npm install -g @openai/codex
   ```

2. **Login to agents (uses your existing subscriptions):**

   ```bash
   claude login
   codex login
   ```

3. **Open your project in OpenCode and start coding!**

---

## Pricing

### Free Tier

- ✅ Unlimited sessions
- ✅ All agents supported
- ✅ Full feature access
- ⚠️ You provide your own agent subscriptions/API keys

### Pro (Coming Soon) — $10/month

- ✅ Everything in Free
- ✅ Cloud workspace sync
- ✅ Team collaboration
- ✅ Priority support

### Enterprise — Contact Us

- ✅ Everything in Pro
- ✅ SSO/SAML
- ✅ Audit logs
- ✅ On-premise deployment
- ✅ Custom agent integrations

---

## Roadmap

### Now

- [x] Multi-agent support (Claude, Codex, Amp, Gemini)
- [x] Git worktree workspaces
- [x] Universal skills system
- [x] Approval-based execution
- [x] MCP support

### Next

- [ ] Extension/plugin system
- [ ] Aider integration
- [ ] Continue.dev integration
- [ ] Collaborative sessions
- [ ] Voice input mode

### Future

- [ ] Custom agent adapters (bring ANY agent)
- [ ] Mobile companion app
- [ ] AI-powered code review
- [ ] Multi-agent orchestration (agents talking to agents)

---

## FAQ

**Q: Do I need to pay for OpenCode AND my AI subscriptions?**

> OpenCode Free tier is completely free. You just need your existing Claude Pro, ChatGPT Plus, or API keys. No double-paying.

**Q: Is this just another VSCode fork?**

> No. OpenCode is built from scratch using Tauri (Rust). Zero VSCode code. Purpose-built for agentic workflows.

**Q: Can I use multiple agents in the same session?**

> Currently, each session uses one agent. But sessions share the same workspace, so you can have Claude working on backend while Codex handles frontend — simultaneously.

**Q: What if my company requires specific AI providers?**

> OpenCode supports API key configuration. Your security team can approve specific providers, and developers use only those.

**Q: Is my code sent to OpenCode servers?**

> No. Everything runs locally. Your code goes directly to your chosen AI provider — we never see it.

---

## Join the Revolution

The future of coding isn't about which AI is best — it's about using the **right AI for the right task**. OpenCode gives you that freedom.

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│           "I haven't opened a terminal for                  │
│            coding agents in weeks."                         │
│                                                             │
│                        — Early Access User                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

**[Download for macOS](https://opencode.dev/download)** | **[Join Discord](https://discord.gg/opencode)** | **[GitHub](https://github.com/opencode-ide)**

---

## _OpenCode — Your Agents. Your Rules. One IDE._

-
