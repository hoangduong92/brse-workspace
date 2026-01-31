---
name: memory
description: User-level memory - search past conversations, recall facts across sessions. Use when searching for context from previous conversations.
argument-hint: "<search|recent|summarize|add|forget> [query] [--limit N]"
---

# cc-memory

Claude Code memory skill - persistent context across sessions like claude.ai.

## Automatic Features

- **Stop Hook (Auto-save)**: Conversations are saved every 10 responses or 15 minutes
- **SessionEnd Hook**: Final archive when you close VS Code or /clear
- **SessionStart Hook**: Relevant facts are auto-loaded into context
- **Fact Extraction**: Important facts extracted using heuristics + Gemini (if available)

## Usage

```bash
# Search past conversations semantically
/memory search "authentication decision"

# List recent sessions
/memory recent 5

# Summarize topic across all sessions
/memory summarize "database schema"

# Manually add a fact to remember
/memory add "User prefers TypeScript over JavaScript"

# Remove a fact
/memory forget <fact-id>

# Show memory status
/memory status

# Save current session to memory (manual archive)
/memory save

# Export all facts to markdown
/memory export
```

## Storage

Data stored at user level: `~/claude_client/memory/`

- `vault.db` - SQLite with embeddings
- `facts.md` - Human-readable facts (loaded on session start)
- `conversations/archives/` - Archived session transcripts

## Configuration

Edit `~/claude_client/memory/config.json`:

```json
{
  "auto_extract": true,
  "extract_method": "hybrid",
  "max_facts_loaded": 50
}
```

<command-name>memory</command-name>

<instructions>
Execute the memory command based on user input. Parse the arguments to determine the action:

1. **search <query>**: Semantic search across all stored facts and sessions
2. **recent [N]**: List N most recent sessions (default 10)
3. **summarize <topic>**: Summarize all facts related to topic using Gemini
4. **add <fact>**: Manually add a fact to remember
5. **forget <id>**: Remove a fact by ID
6. **status**: Show memory stats

Run the appropriate Python script:
```bash
.claude/skills/.venv/Scripts/python.exe .claude/skills/cc-memory/scripts/main.py <action> [args]
```

Present results clearly with session links for resuming conversations.
</instructions>
