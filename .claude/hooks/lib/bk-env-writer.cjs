/**
 * BrseKit Env Writer
 *
 * Writes BK_* env vars to CLAUDE_ENV_FILE
 * Independent from ClaudeKit (no imports from ck-config-utils)
 *
 * Env vars written:
 * - BK_BRSE_LEVEL: Output verbosity level (0-4, -1 = disabled)
 * - BK_PROJECTS_PATH: Projects directory path
 * - BK_ACTIVE_PROJECT: Current active project name
 * - BK_VAULT_PATH: Project vault directory
 * - BK_GLOSSARY_PATH: Project glossary file
 */

const fs = require('fs');

/**
 * Escape shell special characters for env file values
 * Handles: backslash, double quote, dollar sign, backtick
 *
 * @param {string|number} str - Value to escape
 * @returns {string} Escaped string safe for shell
 */
function escapeShellValue(str) {
  if (typeof str !== 'string') return String(str);
  return str
    .replace(/\\/g, '\\\\')   // Backslash first
    .replace(/"/g, '\\"')     // Double quotes
    .replace(/\$/g, '\\$')    // Dollar sign
    .replace(/`/g, '\\`');    // Backticks
}

/**
 * Write single env var to CLAUDE_ENV_FILE
 *
 * @param {string} key - Env var name
 * @param {string|number} value - Env var value
 * @returns {boolean} True if written, false if skipped
 */
function writeEnv(key, value) {
  const envFile = process.env.CLAUDE_ENV_FILE;

  // Skip if no env file or null/undefined value
  if (!envFile || value === null || value === undefined) {
    return false;
  }

  try {
    const escaped = escapeShellValue(String(value));
    fs.appendFileSync(envFile, `export ${key}="${escaped}"\n`);
    return true;
  } catch (e) {
    // Fail silently - don't block hook execution
    return false;
  }
}

/**
 * Write all BrseKit env vars
 *
 * @param {Object} vars - Object with var names and values
 * @returns {number} Count of vars written
 *
 * @example
 * writeBkEnvVars({
 *   BK_BRSE_LEVEL: 2,
 *   BK_ACTIVE_PROJECT: 'HB21373',
 *   BK_VAULT_PATH: 'projects/HB21373/vault/'
 * });
 */
function writeBkEnvVars(vars) {
  let count = 0;
  for (const [key, value] of Object.entries(vars)) {
    if (value !== null && value !== undefined) {
      if (writeEnv(key, value)) {
        count++;
      }
    }
  }
  return count;
}

module.exports = {
  escapeShellValue,
  writeEnv,
  writeBkEnvVars
};
