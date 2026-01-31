#!/usr/bin/env node
/**
 * Stop Hook - Auto-save conversation to memory periodically
 *
 * Fires: After every Claude response
 * Purpose: Periodically archive conversation and extract facts
 *
 * Strategy:
 * - Save every N responses (default: 10)
 * - Or when session has been running for X minutes
 * - Track last save time to avoid duplicates
 *
 * Input (via stdin):
 * {
 *   "session_id": "abc123",
 *   "transcript_path": "~/.claude/projects/.../chat_xxx.jsonl",
 *   "cwd": "/path/to/workspace",
 *   "stop_hook_active": true
 * }
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

// Configuration
const SAVE_INTERVAL_RESPONSES = 10;  // Save every N responses
const SAVE_INTERVAL_MINUTES = 15;    // Or every N minutes
const MIN_TRANSCRIPT_SIZE = 5000;    // Minimum 5KB to consider saving

// State file to track last save
const STATE_FILE = path.join(os.homedir(), 'claude_client', 'memory', '.autosave-state.json');

function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
    }
  } catch {}
  return {};
}

function saveState(state) {
  try {
    const dir = path.dirname(STATE_FILE);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch {}
}

function countResponses(transcriptPath) {
  try {
    const content = fs.readFileSync(transcriptPath, 'utf-8');
    // Count assistant messages
    const matches = content.match(/"role"\s*:\s*"assistant"/g);
    return matches ? matches.length : 0;
  } catch {
    return 0;
  }
}

async function main() {
  try {
    const stdin = fs.readFileSync(0, 'utf-8').trim();
    if (!stdin) {
      process.exit(0);
    }

    const data = JSON.parse(stdin);
    const { session_id, transcript_path, cwd } = data;

    // Skip if no transcript
    if (!transcript_path || !fs.existsSync(transcript_path)) {
      process.exit(0);
    }

    // Check transcript size
    const stats = fs.statSync(transcript_path);
    if (stats.size < MIN_TRANSCRIPT_SIZE) {
      process.exit(0);
    }

    // Load state
    const state = loadState();
    const sessionState = state[session_id] || {
      lastSaveTime: 0,
      lastSaveResponses: 0,
      lastSaveSize: 0
    };

    const now = Date.now();
    const responseCount = countResponses(transcript_path);
    const minutesSinceLastSave = (now - sessionState.lastSaveTime) / 60000;
    const responsesSinceLastSave = responseCount - sessionState.lastSaveResponses;

    // Check if we should save
    const shouldSave = (
      // First save for this session
      sessionState.lastSaveTime === 0 ||
      // Enough responses since last save
      responsesSinceLastSave >= SAVE_INTERVAL_RESPONSES ||
      // Enough time passed
      minutesSinceLastSave >= SAVE_INTERVAL_MINUTES
    );

    if (!shouldSave) {
      process.exit(0);
    }

    // Find Python and script
    const projectDir = process.env.CLAUDE_PROJECT_DIR || cwd;
    const pythonPath = path.join(projectDir, '.claude', 'skills', '.venv', 'Scripts', 'python.exe');
    const pythonPathUnix = path.join(projectDir, '.claude', 'skills', '.venv', 'bin', 'python3');
    const mainScript = path.join(projectDir, '.claude', 'skills', 'cc-memory', 'scripts', 'main.py');

    let python = 'python3';
    if (fs.existsSync(pythonPath)) {
      python = pythonPath;
    } else if (fs.existsSync(pythonPathUnix)) {
      python = pythonPathUnix;
    }

    if (!fs.existsSync(mainScript)) {
      process.exit(0);
    }

    // Run archive command
    const cmd = `"${python}" "${mainScript}" archive --session-id "${session_id}" --transcript "${transcript_path}" --workspace "${cwd}"`;

    try {
      execSync(cmd, {
        encoding: 'utf-8',
        timeout: 30000,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      // Update state
      state[session_id] = {
        lastSaveTime: now,
        lastSaveResponses: responseCount,
        lastSaveSize: stats.size
      };
      saveState(state);

      // Silent - don't print to avoid noise in Claude's output
      // console.log(`[Memory] Auto-saved session ${session_id.slice(0, 8)}`);
    } catch (execError) {
      // Silent fail
    }

    process.exit(0);
  } catch (error) {
    process.exit(0);
  }
}

main();
