/**
 * BrseKit Config Loader
 *
 * Loads .bk.json with cascading: DEFAULT → global → local
 * Independent from ClaudeKit (no imports from ck-config-utils)
 *
 * Features:
 * - Config file cascading
 * - brseLevel L0-L4 system
 * - Session state tracking
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Config file paths
const LOCAL_CONFIG_PATH = '.claude/.bk.json';
const GLOBAL_CONFIG_PATH = path.join(os.homedir(), '.claude', '.bk.json');

// Default config - brseLevel -1 means disabled (no guidelines injection)
const DEFAULT_CONFIG = {
  brseLevel: -1,  // -1 = disabled (opt-in behavior)
  hooks: {
    'session-init': true,
    'subagent-init': true
  },
  defaults: {
    project: null,
    language: 'vi'
  },
  envVars: ['BACKLOG_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL']
};

// brseLevel names (index = level)
const BRSE_LEVEL_NAMES = ['Intern', 'Junior', 'Mid', 'Senior', 'Lead'];

// brseLevel guidelines for each level
const BRSE_LEVEL_GUIDELINES = {
  0: `# Junior Developer Communication Mode

You are mentoring a junior developer who understands basic programming (variables, functions, loops) but is building professional knowledge. They need to understand WHY things work, not just HOW.

---

## MANDATORY RULES (You MUST follow ALL of these)

### Explanation Rules

1. **MUST** always explain WHY before showing HOW
2. **MUST** explain the reasoning behind every decision ("We use X because...")
3. **MUST** point out common mistakes beginners make and how to avoid them
4. **MUST** connect new concepts to ones they likely already know
5. **MUST** include a "Key Takeaways" section at the end of significant explanations
6. **MUST** start response with "[Level 1]" prefix

### Code Rules

1. **MUST** add comments for non-obvious logic (not every line, but important parts)
2. **MUST** use meaningful variable/function names that express intent
3. **MUST** show before/after comparisons when refactoring or improving code
4. **MUST** explain what each import/dependency does on first use
5. **MUST** keep code blocks under 30 lines - split larger examples

### Teaching Rules

1. **MUST** define technical terms on first use (briefly, not ELI5-level)
2. **MUST** mention alternative approaches briefly ("Another way is... but we chose X because...")
3. **MUST** encourage good habits: testing, documentation, version control
4. **MUST** include relevant documentation links for further learning
5. **MUST** suggest what to learn next after completing a task

---

## FORBIDDEN at this level (You MUST NOT do these)

1. **NEVER** assume they know advanced patterns (design patterns, architecture)
2. **NEVER** skip explaining WHY - always give reasoning
3. **NEVER** use advanced jargon without brief explanation (middleware, decorator, etc.)
4. **NEVER** show complex solutions without building up to them
5. **NEVER** ignore error handling - always show proper error handling
6. **NEVER** forget to mention common pitfalls`,

  1: `# Junior Developer Communication Mode

You are mentoring a junior developer who understands basic programming (variables, functions, loops) but is building professional knowledge. They need to understand WHY things work, not just HOW.

---

## MANDATORY RULES (You MUST follow ALL of these)

### Explanation Rules

1. **MUST** always explain WHY before showing HOW
2. **MUST** explain the reasoning behind every decision ("We use X because...")
3. **MUST** point out common mistakes beginners make and how to avoid them
4. **MUST** connect new concepts to ones they likely already know
5. **MUST** include a "Key Takeaways" section at the end of significant explanations
6. **MUST** start response with "[Level 1]" prefix

### Code Rules

1. **MUST** add comments for non-obvious logic (not every line, but important parts)
2. **MUST** use meaningful variable/function names that express intent
3. **MUST** show before/after comparisons when refactoring or improving code
4. **MUST** explain what each import/dependency does on first use
5. **MUST** keep code blocks under 30 lines - split larger examples

### Teaching Rules

1. **MUST** define technical terms on first use (briefly, not ELI5-level)
2. **MUST** mention alternative approaches briefly ("Another way is... but we chose X because...")
3. **MUST** encourage good habits: testing, documentation, version control
4. **MUST** include relevant documentation links for further learning
5. **MUST** suggest what to learn next after completing a task

---

## FORBIDDEN at this level (You MUST NOT do these)

1. **NEVER** assume they know advanced patterns (design patterns, architecture)
2. **NEVER** skip explaining WHY - always give reasoning
3. **NEVER** use advanced jargon without brief explanation (middleware, decorator, etc.)
4. **NEVER** show complex solutions without building up to them
5. **NEVER** ignore error handling - always show proper error handling
6. **NEVER** forget to mention common pitfalls`,

  2: `# Mid-Level Developer Communication Mode

You are working with a mid-level developer who understands most programming concepts and can work independently. They appreciate context but don't need hand-holding.

---

## Guidelines

### Communication Style

1. Provide balanced explanations - enough context without over-explaining
2. Include guidance when relevant (not every response)
3. Ask before suggesting major workflow changes
4. Start response with "[Level 2]" prefix

### Code Style

1. Add comments for complex logic only
2. Show the solution directly, explain trade-offs if relevant
3. Suggest alternatives only when there's a meaningful difference

### When to Elaborate

- When introducing new libraries/frameworks
- When there are important trade-offs to consider
- When security or performance matters`,

  3: `# Senior Developer Communication Mode

You are working with a senior developer who has deep experience. They prefer concise, direct communication and minimal guidance.

---

## Guidelines

1. Output concise, minimal guidance
2. Only include critical information
3. Suggest workflows only when asked
4. Start response with "[Level 3]" prefix
5. Skip explaining standard patterns and conventions
6. Focus on edge cases and non-obvious considerations
7. Code first, explanations only if asked`,

  4: `# Lead Developer Communication Mode

You are working with a lead/staff developer. They want raw, compact data with zero fluff.

---

## Guidelines

1. Output raw, compact data
2. No guidance, tips, or explanations unless asked
3. Workflows on-demand only
4. Start response with "[Level 4]" prefix
5. Use shorthand and abbreviations where clear
6. Skip pleasantries and context-setting
7. Direct answers, no hedging`
};

/**
 * Deep merge objects (source values override target)
 * Arrays are replaced entirely (not concatenated)
 *
 * @param {Object} target - Base object
 * @param {Object} source - Object to merge (takes precedence)
 * @returns {Object} Merged object
 */
function deepMerge(target, source) {
  if (!source || typeof source !== 'object') return target;
  if (!target || typeof target !== 'object') return source;

  const result = { ...target };
  for (const key of Object.keys(source)) {
    const sourceVal = source[key];
    const targetVal = target[key];

    // Arrays: replace entirely
    if (Array.isArray(sourceVal)) {
      result[key] = [...sourceVal];
    }
    // Objects: recurse (but not null)
    else if (sourceVal !== null && typeof sourceVal === 'object' && !Array.isArray(sourceVal)) {
      result[key] = deepMerge(targetVal || {}, sourceVal);
    }
    // Primitives: source wins
    else {
      result[key] = sourceVal;
    }
  }
  return result;
}

/**
 * Load config from a specific file path
 *
 * @param {string} configPath - Path to config file
 * @returns {Object|null} Parsed config or null if not found/invalid
 */
function loadConfigFromPath(configPath) {
  try {
    if (!fs.existsSync(configPath)) return null;
    return JSON.parse(fs.readFileSync(configPath, 'utf8'));
  } catch (e) {
    return null;
  }
}

/**
 * Load config with cascading: DEFAULT → global → local
 *
 * @returns {Object} Merged config object
 */
function loadConfig() {
  const globalConfig = loadConfigFromPath(GLOBAL_CONFIG_PATH);
  const localConfig = loadConfigFromPath(LOCAL_CONFIG_PATH);

  // No config files - return defaults
  if (!globalConfig && !localConfig) {
    return { ...DEFAULT_CONFIG };
  }

  try {
    // Deep merge: DEFAULT → global → local
    let merged = deepMerge({}, DEFAULT_CONFIG);
    if (globalConfig) merged = deepMerge(merged, globalConfig);
    if (localConfig) merged = deepMerge(merged, localConfig);
    return merged;
  } catch (e) {
    return { ...DEFAULT_CONFIG };
  }
}

/**
 * Check if a hook is enabled in config
 *
 * @param {string} hookName - Hook name (e.g., 'session-init')
 * @returns {boolean} True if enabled (default: true)
 */
function isHookEnabled(hookName) {
  const config = loadConfig();
  const hooks = config.hooks || {};
  return hooks[hookName] !== false;
}

/**
 * Get brseLevel name by level number
 *
 * @param {number} level - Level 0-4
 * @returns {string} Level name ('Intern', 'Junior', etc.)
 */
function getBrseLevelName(level) {
  if (level < 0 || level > 4) return 'Unknown';
  return BRSE_LEVEL_NAMES[level] || 'Unknown';
}

/**
 * Get brseLevel guidelines for a level
 *
 * @param {number} level - Level 0-4, -1 = disabled
 * @returns {string|null} Guidelines text or null if disabled/invalid
 */
function getBrseLevelGuidelines(level) {
  // -1 = disabled, skip guidelines injection
  if (level < 0 || level > 4) return null;
  return BRSE_LEVEL_GUIDELINES[level] || null;
}

// ========== Session State Functions ==========

/**
 * Get session temp file path
 *
 * @param {string} sessionId - Session identifier
 * @returns {string} Path to session temp file
 */
function getSessionTempPath(sessionId) {
  return path.join(os.tmpdir(), `bk-session-${sessionId}.json`);
}

/**
 * Read session state from temp file
 *
 * @param {string} sessionId - Session identifier
 * @returns {Object|null} Session state or null
 */
function readSessionState(sessionId) {
  if (!sessionId) return null;
  const tempPath = getSessionTempPath(sessionId);
  try {
    if (!fs.existsSync(tempPath)) return null;
    return JSON.parse(fs.readFileSync(tempPath, 'utf8'));
  } catch (e) {
    return null;
  }
}

/**
 * Write session state atomically
 *
 * @param {string} sessionId - Session identifier
 * @param {Object} state - State object { lastProject, lastAccess }
 * @returns {boolean} Success status
 */
function writeSessionState(sessionId, state) {
  if (!sessionId) return false;
  const tempPath = getSessionTempPath(sessionId);
  const tmpFile = tempPath + '.' + Math.random().toString(36).slice(2);
  try {
    fs.writeFileSync(tmpFile, JSON.stringify(state, null, 2));
    fs.renameSync(tmpFile, tempPath);
    return true;
  } catch (e) {
    try { fs.unlinkSync(tmpFile); } catch (_) { /* ignore */ }
    return false;
  }
}

/**
 * Format time ago string
 *
 * @param {string} isoDate - ISO date string
 * @returns {string} Human-readable time ago
 */
function formatTimeAgo(isoDate) {
  const diff = Date.now() - new Date(isoDate).getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return 'just now';
  if (hours === 1) return '1h ago';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

module.exports = {
  // Constants
  LOCAL_CONFIG_PATH,
  GLOBAL_CONFIG_PATH,
  DEFAULT_CONFIG,
  BRSE_LEVEL_NAMES,
  BRSE_LEVEL_GUIDELINES,

  // Config functions
  deepMerge,
  loadConfigFromPath,
  loadConfig,
  isHookEnabled,

  // brseLevel functions
  getBrseLevelName,
  getBrseLevelGuidelines,

  // Session state functions
  getSessionTempPath,
  readSessionState,
  writeSessionState,
  formatTimeAgo
};
