#!/usr/bin/env node
/**
 * Content Analysis Detector Hook
 *
 * Fires on Stop event to:
 * 1. Parse transcript for content analysis activity
 * 2. Detect platform being analyzed
 * 3. Output reminder to save lessons to knowledge base
 *
 * Exit codes:
 * - 0: Success (stdout goes to context for UserPromptSubmit/SessionStart)
 * - For Stop hooks, stderr is logged, stdout is ignored
 */
'use strict';

const fs = require('fs');
const readline = require('readline');

// Patterns that indicate content analysis activity
const ANALYSIS_PATTERNS = [
  'draft vs production',
  'draft và production',
  'phân tích',
  'analyze',
  'compare',
  'so sánh',
  'rút kinh nghiệm',
  'lessons learned',
  'what worked',
  'what didn\'t work',
  'anti-pattern',
  'pattern'
];

// Platform detection patterns
const PLATFORM_PATTERNS = {
  facebook: ['facebook', 'fb', 'fb page', 'facebook page'],
  linkedin: ['linkedin', 'li'],
  twitter: ['twitter', 'x.com', 'tweet', 'thread'],
  instagram: ['instagram', 'ig', 'reel', 'carousel']
};

/**
 * Parse JSONL transcript for content analysis activity
 * @param {string} transcriptPath - Path to transcript file
 * @returns {Promise<Object>} Analysis activity summary
 */
async function parseContentAnalysis(transcriptPath) {
  const result = {
    hasAnalysisActivity: false,
    platforms: new Set(),
    patterns: [],
    messageCount: 0
  };

  if (!transcriptPath || !fs.existsSync(transcriptPath)) {
    return result;
  }

  try {
    const fileStream = fs.createReadStream(transcriptPath);
    const rl = readline.createInterface({
      input: fileStream,
      crlfDelay: Infinity
    });

    for await (const line of rl) {
      if (!line.trim()) continue;

      try {
        const entry = JSON.parse(line);
        processEntry(entry, result);
      } catch {
        // Skip malformed lines
      }
    }
  } catch (err) {
    console.error(`[content-analysis] Parse error: ${err.message}`);
  }

  return result;
}

/**
 * Process a single transcript entry
 */
function processEntry(entry, result) {
  if (!entry.message?.content) return;

  for (const block of entry.message.content) {
    if (block.type !== 'text' || typeof block.text !== 'string') continue;

    const text = block.text.toLowerCase();
    result.messageCount++;

    // Check for analysis patterns
    for (const pattern of ANALYSIS_PATTERNS) {
      if (text.includes(pattern)) {
        result.hasAnalysisActivity = true;
        if (!result.patterns.includes(pattern)) {
          result.patterns.push(pattern);
        }
      }
    }

    // Detect platforms
    for (const [platform, keywords] of Object.entries(PLATFORM_PATTERNS)) {
      if (keywords.some(k => text.includes(k))) {
        result.platforms.add(platform);
      }
    }
  }
}

/**
 * Main hook execution
 */
async function main() {
  try {
    const stdin = fs.readFileSync(0, 'utf-8').trim();
    const input = stdin ? JSON.parse(stdin) : {};

    const transcriptPath = process.env.CLAUDE_TRANSCRIPT_PATH || input.transcript_path;

    const analysis = await parseContentAnalysis(transcriptPath);

    if (analysis.hasAnalysisActivity && analysis.platforms.size > 0) {
      const platforms = Array.from(analysis.platforms);

      // Log to stderr (visible in hook output)
      console.error(`[social-content] Content analysis detected for: ${platforms.join(', ')}`);
      console.error(`[social-content] Patterns found: ${analysis.patterns.join(', ')}`);
      console.error(`[social-content] Consider saving lessons to knowledge/${platforms[0]}-lessons.md`);
    }

    process.exit(0);
  } catch (error) {
    console.error(`[social-content] Hook error: ${error.message}`);
    process.exit(0); // Don't block on errors
  }
}

main();
