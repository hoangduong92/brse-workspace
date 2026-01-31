#!/usr/bin/env node
/**
 * BrseKit Subagent Init Hook
 *
 * Fires on: SubagentStart (when Task tool spawns a subagent)
 * Purpose: Inject minimal project context for spawned agents
 *
 * Resolution order (fast path first):
 * 1. Read from BK_* env vars (set by session-init, no disk scan)
 * 2. Fallback to disk scan (for direct subagent invocation)
 *
 * Output format (JSON with hookSpecificOutput wrapper):
 * - With project: vault path + glossary path
 * - Multiple projects: Warning with available list
 * - No projects: Warning message
 *
 * Target: ~40 tokens in additionalContext
 * Design: Fail-open (always exit 0, never block subagent)
 */

const fs = require('fs');
const { isHookEnabled } = require('./lib/bk-config-loader.cjs');
const {
  resolveProject,
  getVaultPath,
  getGlossaryPath
} = require('./lib/bk-config-utils.cjs');

/**
 * Output JSON response with hookSpecificOutput wrapper
 * This format is required by Claude Code for subagent hooks
 *
 * @param {string} context - Context string to inject
 */
function outputResponse(context) {
  const output = {
    hookSpecificOutput: {
      hookEventName: 'SubagentStart',
      additionalContext: context
    }
  };
  console.log(JSON.stringify(output));
}

/**
 * Main entry point
 * Wrapped in try-catch for fail-safe execution
 */
function main() {
  try {
    // Check if hook is enabled
    if (!isHookEnabled('subagent-init')) {
      process.exit(0);
    }

    // Parse stdin - early exit if empty
    let stdin = '';
    try {
      stdin = fs.readFileSync(0, 'utf-8').trim();
    } catch (e) {
      // No stdin - exit silently
      process.exit(0);
    }

    if (!stdin) {
      process.exit(0);
    }

    // Parse payload
    const payload = JSON.parse(stdin);

    // Use payload.cwd for monorepo support
    const effectiveCwd = payload.cwd?.trim() || process.cwd();

    let context;

    // Fast path: Use env vars if available (set by session-init)
    const activeProject = process.env.BK_ACTIVE_PROJECT;
    const vaultPath = process.env.BK_VAULT_PATH;
    const glossaryPath = process.env.BK_GLOSSARY_PATH;
    const brseLevel = process.env.BK_BRSE_LEVEL;

    if (activeProject && vaultPath) {
      // Use env vars (faster, no disk scan needed)
      const glossaryInfo = glossaryPath ? `glossary: ${glossaryPath}` : 'glossary: none';
      const levelInfo = brseLevel && brseLevel !== '-1' ? ` | L${brseLevel}` : '';
      context = `BrseKit: ${activeProject} | vault: ${vaultPath} | ${glossaryInfo}${levelInfo}`;
    } else {
      // Fallback: Disk scan (for direct subagent invocation without session)
      const resolved = resolveProject(null, effectiveCwd);

      if (typeof resolved === 'string') {
        // Single project resolved - provide paths
        const vault = getVaultPath(resolved, effectiveCwd);
        const glossary = getGlossaryPath(resolved, effectiveCwd);
        const glossaryInfo = glossary ? `glossary: ${glossary}` : 'glossary: none';
        context = `BrseKit: ${resolved} | vault: ${vault} | ${glossaryInfo}`;
      } else if (resolved.error === 'NO_PROJECTS') {
        context = 'BrseKit: No projects configured';
      } else {
        // Multiple projects - show available list
        context = `BrseKit: --project not specified. Available: ${resolved.available.join(', ')}`;
      }
    }

    outputResponse(context);
  } catch (error) {
    // Fail-safe: output error in expected format
    outputResponse(`BrseKit hook error: ${error.message}`);
  }

  // Always exit successfully - never block subagent
  process.exit(0);
}

main();
