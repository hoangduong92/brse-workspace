#!/usr/bin/env node
/**
 * SessionEnd Hook - Automatically archive conversation to cc-memory
 *
 * Fires: When a Claude Code session ends
 * Purpose: Archive transcript and extract facts to user-level memory
 *
 * Input (via stdin):
 * {
 *   "session_id": "abc123",
 *   "transcript_path": "~/.claude/projects/.../chat_xxx.jsonl",
 *   "cwd": "/path/to/workspace",
 *   "reason": "exit|clear|logout|prompt_input_exit|other"
 * }
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

async function main() {
  try {
    const stdin = fs.readFileSync(0, 'utf-8').trim();
    if (!stdin) {
      process.exit(0);
    }

    const data = JSON.parse(stdin);
    const { session_id, transcript_path, cwd, reason } = data;

    // Skip if no transcript path
    if (!transcript_path || !fs.existsSync(transcript_path)) {
      console.log('SessionEnd: No transcript to archive');
      process.exit(0);
    }

    // Check transcript size - skip very small sessions
    const stats = fs.statSync(transcript_path);
    if (stats.size < 1000) {  // Less than 1KB = probably empty or very short
      console.log('SessionEnd: Session too short to archive');
      process.exit(0);
    }

    // Find Python venv
    const projectDir = process.env.CLAUDE_PROJECT_DIR || cwd;
    const pythonPath = path.join(projectDir, '.claude', 'skills', '.venv', 'Scripts', 'python.exe');
    const pythonPathUnix = path.join(projectDir, '.claude', 'skills', '.venv', 'bin', 'python3');

    let python = 'python3';
    if (fs.existsSync(pythonPath)) {
      python = pythonPath;
    } else if (fs.existsSync(pythonPathUnix)) {
      python = pythonPathUnix;
    }

    // Find main.py
    const mainScript = path.join(projectDir, '.claude', 'skills', 'cc-memory', 'scripts', 'main.py');
    if (!fs.existsSync(mainScript)) {
      console.log('SessionEnd: cc-memory skill not found, skipping archive');
      process.exit(0);
    }

    // Run archive command
    const cmd = `"${python}" "${mainScript}" archive --session-id "${session_id}" --transcript "${transcript_path}" --workspace "${cwd}"`;

    try {
      const output = execSync(cmd, {
        encoding: 'utf-8',
        timeout: 30000,  // 30 second timeout
        stdio: ['pipe', 'pipe', 'pipe']
      });

      console.log(`SessionEnd: Archived session ${session_id.slice(0, 8)}`);
      if (output.trim()) {
        console.log(output.trim());
      }
    } catch (execError) {
      // Don't fail the hook if archive fails
      console.log(`SessionEnd: Archive warning - ${execError.message}`);
    }

    process.exit(0);
  } catch (error) {
    // Never block session end
    console.log(`SessionEnd hook error: ${error.message}`);
    process.exit(0);
  }
}

main();
