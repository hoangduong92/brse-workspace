#!/usr/bin/env node
/**
 * BrseKit Session Init Hook
 *
 * Fires on: SessionStart (startup, resume, clear, compact)
 * Purpose: Display project status, write env vars, inject brseLevel guidelines
 *
 * Output format (console.log):
 * - 1 project: "BrseKit: Project X (auto-selected)" + env status
 * - N projects: List with warning to use --project
 * - 0 projects: Warning + /bk-init hint
 * - brseLevel guidelines (if level 0-4)
 *
 * Design: Fail-open (always exit 0, never block Claude startup)
 */

const fs = require('fs');
const {
  loadConfig,
  isHookEnabled,
  getBrseLevelGuidelines,
  readSessionState,
  writeSessionState
} = require('./lib/bk-config-loader.cjs');
const { writeBkEnvVars } = require('./lib/bk-env-writer.cjs');
const {
  scanProjectsDir,
  checkEnvVars,
  formatEnvStatus,
  resolveProject,
  getVaultPath,
  getGlossaryPath
} = require('./lib/bk-config-utils.cjs');

/**
 * Parse stdin for session information
 * @returns {Object|null} Parsed stdin data or null
 */
function parseStdin() {
  try {
    const stdin = fs.readFileSync(0, 'utf-8').trim();
    if (stdin) {
      return JSON.parse(stdin);
    }
  } catch (e) {
    // Ignore stdin parsing errors
  }
  return null;
}

/**
 * Main entry point
 * Wrapped in try-catch for fail-safe execution
 */
function main() {
  try {
    // Check if hook is enabled in config
    if (!isHookEnabled('session-init')) {
      process.exit(0);
    }

    // Load config
    const config = loadConfig();
    const brseLevel = config.brseLevel ?? -1;
    const defaultProject = config.defaults?.project || null;

    // Parse stdin for sessionId
    const stdinData = parseStdin();
    const sessionId = stdinData?.sessionId;

    // Check session state for lastProject suggestion
    const sessionState = readSessionState(sessionId);

    // Scan for projects and check env vars
    const projects = scanProjectsDir();
    const envVars = checkEnvVars();
    const envStatus = formatEnvStatus(envVars);

    // Resolve project (with default from config or session state)
    const projectHint = defaultProject || sessionState?.lastProject || null;
    const resolved = resolveProject(projectHint);

    // Get resolved project name (string if single, null if error)
    const activeProject = typeof resolved === 'string' ? resolved : null;

    // Build BK_* env vars to write
    const bkEnvVars = {
      BK_BRSE_LEVEL: brseLevel,
      BK_PROJECTS_PATH: 'projects',
      BK_ACTIVE_PROJECT: activeProject,
      BK_VAULT_PATH: activeProject ? getVaultPath(activeProject) : null,
      BK_GLOSSARY_PATH: activeProject ? getGlossaryPath(activeProject) : null
    };

    // Write env vars to CLAUDE_ENV_FILE
    writeBkEnvVars(bkEnvVars);

    // Output project status
    if (projects.length === 0) {
      // No projects - show warning and hint
      console.log('BrseKit: No projects in projects/');
      console.log('Run: /bk-init to create first project');
    } else if (projects.length === 1) {
      // Single project - auto-select
      console.log(`BrseKit: Project ${projects[0]} (auto-selected)`);
      console.log(`Env: ${envStatus}`);
    } else {
      // Multiple projects - show list with warning
      console.log(`BrseKit: ${projects.length} projects available`);
      projects.forEach((project, index) => {
        const isLast = index === projects.length - 1;
        const prefix = isLast ? '└──' : '├──';
        console.log(`${prefix} ${project}`);
      });
      console.log('Use --project <name> with skills');
      console.log(`Env: ${envStatus}`);
    }

    // Inject brseLevel guidelines (if level 0-4, skip if -1)
    const guidelines = getBrseLevelGuidelines(brseLevel);
    if (guidelines) {
      console.log('\n' + guidelines);
    }

    // Update session state with current project
    if (sessionId && activeProject) {
      writeSessionState(sessionId, {
        lastProject: activeProject,
        lastAccess: new Date().toISOString()
      });
    }
  } catch (error) {
    // Fail-safe: log error but don't block Claude
    console.error(`BrseKit hook error: ${error.message}`);
  }

  // Always exit successfully - never block Claude startup
  process.exit(0);
}

main();
