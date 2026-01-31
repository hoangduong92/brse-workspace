# Phase 2: SessionStart Hook - Context Loading

## Context Links
- Session init hook: `.claude/hooks/session-init.cjs`
- Hook settings: `.claude/settings.json`

## Overview
- **Priority:** P1 (enhances UX)
- **Status:** pending
- **Effort:** 0.5h

Load facts.md into Claude context on session start for immediate memory access.

## Key Insights

1. SessionStart hook already exists at `.claude/hooks/session-init.cjs`
2. Hook output appears in Claude's context
3. Keep facts injection lightweight (<2KB)
4. Prioritize recent, high-confidence facts

## Requirements

### Functional
- Load facts.md on session start
- Inject top N facts into context
- Respect config limit (default 50 facts)
- Format for Claude consumption

### Non-Functional
- <50ms added latency
- Graceful if memory not initialized
- Silent if no facts exist

## Architecture

```
SessionStart hook
    ↓
session-init.cjs (existing)
    ├── Existing project detection
    └── NEW: Memory facts injection
            ↓
        memory-context-loader.cjs
            ├── Read ~/claude_client/memory/facts.md
            ├── Parse and filter facts
            └── Format and output
```

## Related Code Files

### Create
- `.claude/hooks/lib/memory-context-loader.cjs` - Load and format facts

### Modify
- `.claude/hooks/session-init.cjs` - Add memory loading call

## Implementation Steps

### Step 1: Create memory-context-loader.cjs

```javascript
#!/usr/bin/env node
/**
 * Memory Context Loader - Load facts for session context
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

const MEMORY_DIR = path.join(os.homedir(), 'claude_client', 'memory');
const FACTS_PATH = path.join(MEMORY_DIR, 'facts.md');
const CONFIG_PATH = path.join(MEMORY_DIR, 'config.json');

const DEFAULT_CONFIG = {
  max_facts_loaded: 50,
  auto_extract: true
};

/**
 * Load memory configuration
 */
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_PATH)) {
      return { ...DEFAULT_CONFIG, ...JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8')) };
    }
  } catch (e) {
    // Ignore errors, use defaults
  }
  return DEFAULT_CONFIG;
}

/**
 * Parse facts from facts.md
 * Returns array of { content, category, confidence }
 */
function parseFacts(content, limit) {
  const facts = [];
  const lines = content.split('\n');

  let currentCategory = 'general';

  for (const line of lines) {
    // Category header
    if (line.startsWith('### ')) {
      currentCategory = line.slice(4).toLowerCase().trim();
      continue;
    }

    // Fact line
    if (line.startsWith('- ')) {
      const factText = line.slice(2).trim();

      // Extract confidence if present [85%]
      const confMatch = factText.match(/\[(\d+)%\]\s*$/);
      const confidence = confMatch ? parseInt(confMatch[1]) / 100 : 1.0;
      const content = confMatch ? factText.replace(/\[\d+%\]\s*$/, '').trim() : factText;

      if (content.length > 5) {
        facts.push({ content, category: currentCategory, confidence });
      }
    }
  }

  // Sort by confidence, take top N
  facts.sort((a, b) => b.confidence - a.confidence);
  return facts.slice(0, limit);
}

/**
 * Format facts for Claude context
 */
function formatForContext(facts) {
  if (!facts.length) return '';

  const byCategory = {};
  for (const fact of facts) {
    byCategory[fact.category] = byCategory[fact.category] || [];
    byCategory[fact.category].push(fact.content);
  }

  let output = '\n## User Memory (from previous sessions)\n';

  for (const [category, items] of Object.entries(byCategory)) {
    output += `\n**${category.charAt(0).toUpperCase() + category.slice(1)}:**\n`;
    for (const item of items) {
      output += `- ${item}\n`;
    }
  }

  return output;
}

/**
 * Load and format memory context
 * @returns {string} Formatted context or empty string
 */
function loadMemoryContext() {
  try {
    if (!fs.existsSync(FACTS_PATH)) {
      return '';
    }

    const config = loadConfig();
    const content = fs.readFileSync(FACTS_PATH, 'utf-8');
    const facts = parseFacts(content, config.max_facts_loaded);

    if (!facts.length) {
      return '';
    }

    return formatForContext(facts);
  } catch (e) {
    return ''; // Silent failure
  }
}

module.exports = {
  loadMemoryContext,
  parseFacts,
  formatForContext,
  loadConfig
};

// CLI usage
if (require.main === module) {
  const context = loadMemoryContext();
  if (context) {
    console.log(context);
  }
}
```

### Step 2: Modify session-init.cjs

Add at end of main() function, before final console.log:

```javascript
// Load memory context
const { loadMemoryContext } = require('./lib/memory-context-loader.cjs');
const memoryContext = loadMemoryContext();
if (memoryContext) {
  console.log(memoryContext);
}
```

Or safer approach - create wrapper that chains hooks:

```javascript
// In session-init.cjs, add near the end:

// Memory integration (optional, non-blocking)
try {
  const memoryLoader = path.join(__dirname, 'lib', 'memory-context-loader.cjs');
  if (fs.existsSync(memoryLoader)) {
    const { loadMemoryContext } = require(memoryLoader);
    const memoryContext = loadMemoryContext();
    if (memoryContext) {
      console.log(memoryContext);
    }
  }
} catch (e) {
  // Memory loading is optional, don't fail session init
}
```

## Todo List

- [ ] Create memory-context-loader.cjs
- [ ] Implement parseFacts() function
- [ ] Implement formatForContext() function
- [ ] Modify session-init.cjs to load memory
- [ ] Test with sample facts.md
- [ ] Verify context appears in Claude

## Success Criteria

- [ ] facts.md parsed correctly
- [ ] Top N facts selected by confidence
- [ ] Context formatted readably
- [ ] Session init not slowed (<50ms)
- [ ] Works when memory not initialized

## Security Considerations

- Read-only operation
- No sensitive data exposure
- User controls what's in facts.md
