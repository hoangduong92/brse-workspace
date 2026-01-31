/**
 * BrseKit Utility Library for Hooks
 *
 * Provides core functions for multi-project context injection:
 * - scanProjectsDir() - List projects in projects/ directory
 * - checkEnvVars() - Check BrseKit-related env vars (boolean flags only)
 * - resolveProject() - Auto-select single project or return error for multiple
 * - formatEnvStatus() - Format env var status with ✓/✗ symbols
 *
 * Design principles:
 * - Security-first: Never expose env var values, only boolean flags
 * - Fail-safe: Always return valid data, never throw
 * - Fast: < 50ms execution, no deep file scans
 * - Independent: No dependency on ClaudeKit code
 */

const fs = require('fs');
const path = require('path');

// Environment variables to check for BrseKit functionality
const ENV_VARS = ['BACKLOG_API_KEY', 'GEMINI_API_KEY', 'SLACK_WEBHOOK_URL'];

/**
 * Scan projects/ directory for project folders
 *
 * Returns array of project folder names (not full paths).
 * Filters out hidden folders (starting with '.').
 *
 * @param {string} basePath - Base directory to scan from (default: cwd)
 * @returns {string[]} Array of project names
 *
 * @example
 * // With projects/HB21373 and projects/HB21456
 * scanProjectsDir() // ['HB21373', 'HB21456']
 *
 * // With no projects/ directory
 * scanProjectsDir() // []
 */
function scanProjectsDir(basePath = process.cwd()) {
  try {
    const projectsPath = path.join(basePath, 'projects');

    // Return empty if projects/ doesn't exist
    if (!fs.existsSync(projectsPath)) {
      return [];
    }

    return fs
      .readdirSync(projectsPath, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      // Filter out hidden folders (validation decision: ignore folders starting with '.')
      .filter((d) => !d.name.startsWith('.'))
      .map((d) => d.name);
  } catch (e) {
    // Fail-safe: return empty array on any error
    return [];
  }
}

/**
 * Check BrseKit-related environment variables
 *
 * Returns boolean flags only - NEVER exposes actual values.
 * This is a security-first design to prevent accidental key leakage.
 *
 * @returns {Object} Object with env var names as keys, boolean flags as values
 *
 * @example
 * // With BACKLOG_API_KEY set, GEMINI_API_KEY unset
 * checkEnvVars() // { BACKLOG_API_KEY: true, GEMINI_API_KEY: false, SLACK_WEBHOOK_URL: false }
 */
function checkEnvVars() {
  return Object.fromEntries(
    ENV_VARS.map((key) => [key, !!process.env[key]])
  );
}

/**
 * Resolve which project to use
 *
 * Logic:
 * 1. If explicitProject provided, use it directly
 * 2. If exactly 1 project exists, auto-select it
 * 3. If 0 projects, return error object with type 'NO_PROJECTS'
 * 4. If 2+ projects, return error object with type 'MULTIPLE_PROJECTS' and available list
 *
 * @param {string|null} explicitProject - Explicitly specified project name
 * @param {string} basePath - Base directory to scan from (default: cwd)
 * @returns {string|Object} Project name (string) or error object
 *
 * @example
 * // Single project - auto-selected
 * resolveProject(null) // 'HB21373'
 *
 * // Multiple projects - error with list
 * resolveProject(null) // { error: 'MULTIPLE_PROJECTS', available: ['HB21373', 'HB21456'] }
 *
 * // Explicit project
 * resolveProject('HB21373') // 'HB21373'
 */
function resolveProject(explicitProject, basePath = process.cwd()) {
  // If explicit project provided, use it directly
  if (explicitProject) {
    return explicitProject;
  }

  const projects = scanProjectsDir(basePath);

  // Auto-select if exactly 1 project
  if (projects.length === 1) {
    return projects[0];
  }

  // No projects found
  if (projects.length === 0) {
    return { error: 'NO_PROJECTS' };
  }

  // Multiple projects - return error with available list
  return { error: 'MULTIPLE_PROJECTS', available: projects };
}

/**
 * Format env var status for display
 *
 * Converts env var boolean flags to compact display format.
 * Uses shortened names for better readability.
 *
 * @param {Object} envVars - Object from checkEnvVars()
 * @returns {string} Formatted status string
 *
 * @example
 * formatEnvStatus({ BACKLOG_API_KEY: true, GEMINI_API_KEY: false, SLACK_WEBHOOK_URL: true })
 * // 'API_KEY: ✓ | GEMINI_KEY: ✗ | WEBHOOK_URL: ✓'
 */
function formatEnvStatus(envVars) {
  // Shorten env var names for compact display
  const shortNames = {
    BACKLOG_API_KEY: 'API_KEY',
    GEMINI_API_KEY: 'GEMINI_KEY',
    SLACK_WEBHOOK_URL: 'WEBHOOK_URL'
  };

  return Object.entries(envVars)
    .map(([key, isSet]) => {
      const name = shortNames[key] || key;
      return `${name}: ${isSet ? '✓' : '✗'}`;
    })
    .join(' | ');
}

/**
 * Get project vault path
 *
 * @param {string} projectName - Project name
 * @param {string} basePath - Base directory (default: cwd)
 * @returns {string} Relative path to vault directory
 */
function getVaultPath(projectName, basePath = process.cwd()) {
  return `projects/${projectName}/vault/`;
}

/**
 * Get project glossary path if exists
 *
 * Returns path to glossary.json if it exists, null otherwise.
 * Used by subagent hook to provide glossary path for translation.
 *
 * @param {string} projectName - Project name
 * @param {string} basePath - Base directory (default: cwd)
 * @returns {string|null} Relative path to glossary.json or null
 */
function getGlossaryPath(projectName, basePath = process.cwd()) {
  const relativePath = `projects/${projectName}/glossary.json`;
  const absolutePath = path.join(basePath, relativePath);

  if (fs.existsSync(absolutePath)) {
    return relativePath;
  }
  return null;
}

module.exports = {
  ENV_VARS,
  scanProjectsDir,
  checkEnvVars,
  resolveProject,
  formatEnvStatus,
  getVaultPath,
  getGlossaryPath
};
