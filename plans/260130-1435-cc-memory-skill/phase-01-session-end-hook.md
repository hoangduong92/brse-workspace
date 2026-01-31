# Phase 1: SessionEnd Hook - Fact Extraction

## Context Links
- Transcript parser: `.claude/hooks/lib/transcript-parser.cjs`
- Session init hook: `.claude/hooks/session-init.cjs`
- Claude projects: `~/.claude/projects/{workspace}/{session_id}.jsonl`

## Overview
- **Priority:** P0 (core feature)
- **Status:** pending
- **Effort:** 1.5h

Archive session transcripts and extract facts on session end.

## Key Insights

1. Claude Code stores transcripts at `~/.claude/projects/{encoded-workspace}/{session_id}.jsonl`
2. JSONL format with message types: user, assistant, tool_use, tool_result
3. Extraction priority: decisions, preferences, requirements, context
4. Hybrid approach: heuristics for speed, Gemini for important sessions

## Requirements

### Functional
- Trigger on session end (currently no SessionEnd hook in Claude Code)
- Archive transcript to `~/claude_client/memory/conversations/archives/`
- Extract facts using heuristics (keywords: decided, prefer, requirement, always, never)
- For sessions >20 messages, use Gemini for smart extraction
- Update facts.md with new facts

### Non-Functional
- Non-blocking (don't delay session close)
- Handle missing transcripts gracefully
- Skip very short sessions (<5 messages)

## Architecture

```
SessionEnd trigger
    ↓
session_archiver.py
    ├── Copy JSONL to archives/
    ├── Parse transcript
    ├── Count messages
    └── Update session registry
    ↓
fact_extractor.py
    ├── Heuristic extraction (keywords)
    ├── Gemini extraction (if threshold met)
    └── Deduplicate with existing facts
    ↓
facts_writer.py
    └── Append to facts.md
```

## Related Code Files

### Create
- `.claude/skills/cc-memory/scripts/session_archiver.py` - Archive transcripts
- `.claude/skills/cc-memory/scripts/fact_extractor.py` - Extract facts
- `.claude/skills/cc-memory/scripts/facts_writer.py` - Update facts.md
- `.claude/hooks/memory-session-end.cjs` - Hook entry point

### Modify
- `.claude/settings.json` - Add SessionEnd hook (when supported)

## Implementation Steps

### Step 1: Implement session_archiver.py

```python
"""Archive session transcripts to memory storage."""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from memory_store import MemoryStore, Session

class SessionArchiver:
    """Archive Claude Code session transcripts."""

    def __init__(self):
        self.store = MemoryStore()
        self.archives_dir = self.store._get_archives_dir()

    def _get_archives_dir(self) -> Path:
        from memory_db import MemoryDB
        return MemoryDB.get_memory_dir() / "conversations" / "archives"

    def _get_claude_projects_dir(self) -> Path:
        return Path.home() / ".claude" / "projects"

    def _encode_workspace(self, workspace: str) -> str:
        """Encode workspace path for Claude's directory naming."""
        # Claude uses c--Users-duongbibo-brse-workspace format
        return workspace.replace(":", "-").replace("/", "-").replace("\\", "-")

    def archive_session(
        self,
        session_id: str,
        workspace: str,
        end_time: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """Archive a session transcript.

        Returns: dict with session info or None if not found
        """
        # Find source transcript
        encoded = self._encode_workspace(workspace)
        source_path = self._get_claude_projects_dir() / encoded / f"{session_id}.jsonl"

        if not source_path.exists():
            return None

        # Create archive path
        self.archives_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        workspace_short = Path(workspace).name
        archive_name = f"{date_str}-{workspace_short}-{session_id[:8]}.jsonl"
        archive_path = self.archives_dir / archive_name

        # Copy transcript
        shutil.copy2(source_path, archive_path)

        # Parse and count messages
        message_count = 0
        start_time = None
        with open(source_path) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("type") in ("user", "assistant"):
                        message_count += 1
                    if not start_time and entry.get("timestamp"):
                        start_time = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                except json.JSONDecodeError:
                    continue

        # Record session
        session = Session(
            session_id=session_id,
            workspace=workspace,
            start_time=start_time,
            end_time=end_time or datetime.now(),
            message_count=message_count,
            archived_path=str(archive_path)
        )
        self.store.add_session(session)

        return {
            "session_id": session_id,
            "workspace": workspace,
            "message_count": message_count,
            "archived_path": str(archive_path)
        }

    def get_session_transcript(self, session_id: str) -> Optional[str]:
        """Get archived transcript content."""
        sessions = [s for s in self.store.get_recent_sessions(100)
                    if s.session_id == session_id]
        if not sessions or not sessions[0].archived_path:
            return None

        path = Path(sessions[0].archived_path)
        if path.exists():
            return path.read_text()
        return None
```

### Step 2: Implement fact_extractor.py

```python
"""Extract facts from session transcripts."""
import re
import json
from typing import List, Tuple, Optional
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from memory_store import MemoryStore, Fact
from config_manager import ConfigManager

# Heuristic patterns for fact extraction
FACT_PATTERNS = [
    (r"(?:i |we |user )(?:prefer|like|want|need)s?\s+(.+?)(?:\.|$)", "preference", 0.7),
    (r"(?:decided|decision|chose|choosing)\s+(?:to\s+)?(.+?)(?:\.|$)", "decision", 0.8),
    (r"(?:always|never|must|should)\s+(.+?)(?:\.|$)", "requirement", 0.6),
    (r"(?:important|key|critical|note):\s*(.+?)(?:\.|$)", "context", 0.7),
    (r"(?:requirement|spec|specification):\s*(.+?)(?:\.|$)", "requirement", 0.8),
]

@dataclass
class ExtractedFact:
    content: str
    category: str
    confidence: float
    source_line: str

class FactExtractor:
    """Extract facts from session transcripts."""

    def __init__(self):
        self.store = MemoryStore()
        self.config = ConfigManager()

    def extract_heuristic(self, transcript_text: str) -> List[ExtractedFact]:
        """Extract facts using keyword heuristics."""
        facts = []

        # Parse JSONL and extract user/assistant text
        lines = transcript_text.strip().split("\n")
        for line in lines:
            try:
                entry = json.loads(line)
                text = self._extract_text(entry)
                if not text:
                    continue

                for pattern, category, confidence in FACT_PATTERNS:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        # Clean and validate match
                        content = match.strip()
                        if len(content) > 10 and len(content) < 500:
                            facts.append(ExtractedFact(
                                content=content,
                                category=category,
                                confidence=confidence,
                                source_line=text[:100]
                            ))
            except json.JSONDecodeError:
                continue

        return self._deduplicate(facts)

    def extract_gemini(self, transcript_text: str, session_id: str) -> List[ExtractedFact]:
        """Extract facts using Gemini API for smarter extraction."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

            # Truncate for API limits
            max_chars = 50000
            truncated = transcript_text[:max_chars]

            prompt = f"""Analyze this Claude Code session transcript and extract key facts that should be remembered.

Focus on:
- User preferences (tools, languages, styles)
- Technical decisions made
- Project requirements mentioned
- Important context about the codebase

Return JSON array:
[{{"content": "fact text", "category": "preference|decision|requirement|context", "confidence": 0.0-1.0}}]

Transcript:
{truncated}"""

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)

            # Parse response
            text = response.text
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                items = json.loads(json_match.group())
                return [
                    ExtractedFact(
                        content=item["content"],
                        category=item.get("category", "context"),
                        confidence=item.get("confidence", 0.7),
                        source_line=f"gemini:{session_id}"
                    )
                    for item in items
                ]
        except Exception as e:
            print(f"Gemini extraction failed: {e}")

        return []

    def extract(self, transcript_text: str, session_id: str, message_count: int) -> List[ExtractedFact]:
        """Extract facts using configured method."""
        method = self.config.get("extract_method", "hybrid")
        threshold = self.config.get("gemini_threshold_messages", 20)

        if method == "heuristic":
            return self.extract_heuristic(transcript_text)
        elif method == "gemini":
            return self.extract_gemini(transcript_text, session_id)
        else:  # hybrid
            facts = self.extract_heuristic(transcript_text)
            if message_count >= threshold:
                gemini_facts = self.extract_gemini(transcript_text, session_id)
                facts.extend(gemini_facts)
            return self._deduplicate(facts)

    def save_facts(self, facts: List[ExtractedFact], session_id: str):
        """Save extracted facts to store."""
        for ef in facts:
            fact = Fact(
                id=None,  # Auto-generate
                content=ef.content,
                source_session=session_id,
                confidence=ef.confidence,
                category=ef.category
            )
            self.store.add_fact(fact)

    def _extract_text(self, entry: dict) -> Optional[str]:
        """Extract text content from JSONL entry."""
        if entry.get("type") not in ("user", "assistant"):
            return None

        message = entry.get("message", {})
        content = message.get("content", [])

        texts = []
        for block in content:
            if isinstance(block, str):
                texts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))

        return " ".join(texts)

    def _deduplicate(self, facts: List[ExtractedFact]) -> List[ExtractedFact]:
        """Remove duplicate facts based on content similarity."""
        seen = set()
        unique = []
        for fact in facts:
            key = fact.content.lower()[:50]
            if key not in seen:
                seen.add(key)
                unique.append(fact)
        return unique
```

### Step 3: Implement facts_writer.py

```python
"""Write facts to facts.md file."""
from pathlib import Path
from typing import List
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from memory_db import MemoryDB
from memory_store import Fact

class FactsWriter:
    """Manage facts.md file."""

    def __init__(self):
        self.facts_path = MemoryDB.get_memory_dir() / "facts.md"

    def load(self) -> str:
        """Load current facts.md content."""
        if self.facts_path.exists():
            return self.facts_path.read_text()
        return ""

    def append_facts(self, facts: List[Fact], session_id: str):
        """Append new facts to facts.md."""
        if not facts:
            return

        self.facts_path.parent.mkdir(parents=True, exist_ok=True)

        current = self.load()
        if not current:
            current = "# Memory Facts\n\nFacts extracted from Claude Code sessions.\n\n"

        # Group by category
        by_category = {}
        for fact in facts:
            cat = fact.category or "general"
            by_category.setdefault(cat, []).append(fact)

        # Append new section
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_section = f"\n## Session {session_id[:8]} ({timestamp})\n\n"

        for category, cat_facts in by_category.items():
            new_section += f"### {category.title()}\n"
            for fact in cat_facts:
                conf = f"[{fact.confidence:.0%}]" if fact.confidence < 1 else ""
                new_section += f"- {fact.content} {conf}\n"
            new_section += "\n"

        # Write updated content
        with open(self.facts_path, "w") as f:
            f.write(current + new_section)

    def get_facts_for_context(self, limit: int = 50) -> str:
        """Get facts formatted for Claude context injection."""
        content = self.load()
        if not content:
            return ""

        # Parse and return most recent facts
        lines = content.split("\n")
        fact_lines = [l for l in lines if l.startswith("- ")]

        if len(fact_lines) > limit:
            fact_lines = fact_lines[-limit:]

        return "\n".join(fact_lines)
```

### Step 4: Create hook entry point (memory-session-end.cjs)

```javascript
#!/usr/bin/env node
/**
 * SessionEnd Hook - Archive transcript and extract facts
 *
 * NOTE: SessionEnd hook not yet supported by Claude Code.
 * This can be triggered manually: node memory-session-end.cjs
 * Or via a wrapper script on session close.
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

async function main() {
  try {
    const stdin = fs.readFileSync(0, 'utf-8').trim();
    const data = stdin ? JSON.parse(stdin) : {};

    const sessionId = data.session_id || process.env.CK_SESSION_ID;
    const cwd = data.cwd || process.cwd();

    if (!sessionId) {
      console.log('No session ID, skipping memory archival');
      process.exit(0);
    }

    // Run Python archiver
    const venvPython = path.join(__dirname, '../skills/.venv/Scripts/python.exe');
    const script = path.join(__dirname, '../skills/cc-memory/scripts/archive_session.py');

    if (!fs.existsSync(venvPython)) {
      console.log('Python venv not found, skipping');
      process.exit(0);
    }

    if (!fs.existsSync(script)) {
      console.log('Memory skill not installed, skipping');
      process.exit(0);
    }

    const result = execSync(
      `"${venvPython}" "${script}" "${sessionId}" "${cwd}"`,
      { encoding: 'utf-8', timeout: 30000 }
    );

    console.log(result);
    process.exit(0);
  } catch (error) {
    console.error(`Memory hook error: ${error.message}`);
    process.exit(0); // Non-blocking
  }
}

main();
```

### Step 5: Create archive_session.py CLI

```python
#!/usr/bin/env python3
"""CLI for archiving session and extracting facts."""
import sys
from datetime import datetime

from session_archiver import SessionArchiver
from fact_extractor import FactExtractor
from facts_writer import FactsWriter
from config_manager import ConfigManager

def main():
    if len(sys.argv) < 3:
        print("Usage: archive_session.py <session_id> <workspace>")
        sys.exit(1)

    session_id = sys.argv[1]
    workspace = sys.argv[2]

    config = ConfigManager()
    min_messages = config.get("min_session_messages", 5)

    # Archive session
    archiver = SessionArchiver()
    result = archiver.archive_session(session_id, workspace)

    if not result:
        print(f"No transcript found for session {session_id}")
        sys.exit(0)

    print(f"Archived session: {result['message_count']} messages")

    # Skip short sessions
    if result["message_count"] < min_messages:
        print(f"Session too short ({result['message_count']} < {min_messages}), skipping extraction")
        sys.exit(0)

    # Extract facts
    transcript = archiver.get_session_transcript(session_id)
    if not transcript:
        print("Could not read transcript")
        sys.exit(0)

    extractor = FactExtractor()
    facts = extractor.extract(transcript, session_id, result["message_count"])

    if facts:
        extractor.save_facts(facts, session_id)
        writer = FactsWriter()
        writer.append_facts([
            type('Fact', (), {'content': f.content, 'category': f.category, 'confidence': f.confidence})()
            for f in facts
        ], session_id)
        print(f"Extracted {len(facts)} facts")
    else:
        print("No facts extracted")

if __name__ == "__main__":
    main()
```

## Todo List

- [ ] Implement session_archiver.py
- [ ] Implement fact_extractor.py with heuristics
- [ ] Implement fact_extractor.py Gemini integration
- [ ] Implement facts_writer.py
- [ ] Create memory-session-end.cjs hook
- [ ] Create archive_session.py CLI
- [ ] Test with real session transcript

## Success Criteria

- [ ] Session transcript copied to archives/
- [ ] Session recorded in memory_sessions table
- [ ] Facts extracted using heuristics
- [ ] Gemini extraction works for long sessions
- [ ] facts.md updated with new facts

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| SessionEnd hook not supported | High | Manual trigger, future-proof implementation |
| Large transcripts | Medium | Truncate for Gemini, stream parsing |
| Gemini API failures | Low | Fallback to heuristics only |
