#!/usr/bin/env node
/**
 * Memory Loader - Load user memory facts for session context injection
 * Used by SessionStart hook to inject relevant memories
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Get memory directory path
 * @returns {string}
 */
function getMemoryDir() {
  return path.join(os.homedir(), 'claude_client', 'memory');
}

/**
 * Load facts.md content for context injection
 * @param {number} maxLines - Maximum lines to load (default 50)
 * @returns {string|null} - Facts content or null if not found
 */
function loadFactsMarkdown(maxLines = 50) {
  const factsPath = path.join(getMemoryDir(), 'facts.md');

  if (!fs.existsSync(factsPath)) {
    return null;
  }

  try {
    const content = fs.readFileSync(factsPath, 'utf-8');
    const lines = content.split('\n');

    if (lines.length <= maxLines) {
      return content;
    }

    // Truncate to max lines
    return lines.slice(0, maxLines).join('\n') + '\n...(truncated)';
  } catch {
    return null;
  }
}

/**
 * Get memory status summary
 * @returns {Object} - Status object with counts
 */
function getMemoryStatus() {
  const memoryDir = getMemoryDir();
  const dbPath = path.join(memoryDir, 'vault.db');

  const status = {
    exists: fs.existsSync(memoryDir),
    dbExists: fs.existsSync(dbPath),
    factsExists: fs.existsSync(path.join(memoryDir, 'facts.md')),
    sessionCount: 0,
    factCount: 0
  };

  // Try to get counts from database (if sqlite3 is available)
  if (status.dbExists) {
    try {
      // We can't easily query SQLite from Node.js without dependencies
      // So we'll rely on facts.md for quick status
      const factsPath = path.join(memoryDir, 'facts.md');
      if (fs.existsSync(factsPath)) {
        const content = fs.readFileSync(factsPath, 'utf-8');
        // Count bullet points (facts)
        const matches = content.match(/^- /gm);
        status.factCount = matches ? matches.length : 0;
      }
    } catch {
      // Ignore errors
    }
  }

  return status;
}

/**
 * Format memory context for injection
 * @returns {string} - Formatted context string
 */
function formatMemoryContext() {
  const status = getMemoryStatus();

  if (!status.exists || !status.factsExists) {
    return '';
  }

  const facts = loadFactsMarkdown(30);  // Load top 30 lines
  if (!facts) {
    return '';
  }

  return `
## User Memory (from previous sessions)

${facts}

_Use \`/memory search <query>\` to find more context._
`;
}

module.exports = {
  getMemoryDir,
  loadFactsMarkdown,
  getMemoryStatus,
  formatMemoryContext
};
