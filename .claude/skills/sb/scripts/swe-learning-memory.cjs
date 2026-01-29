#!/usr/bin/env node
/**
 * SWE Learning Memory Hook
 *
 * Fires on Stop event to:
 * 1. Parse transcript for learning-related activity
 * 2. Detect implicit sentiment (satisfaction/frustration)
 * 3. Append session summary + feedback to learner profile
 *
 * Uses modular components:
 * - swe-learning-sentiment-analyzer.cjs - Sentiment analysis
 * - swe-learning-profile-updater.cjs - Profile management
 */
'use strict';

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { analyzeSentiment } = require('./swe-learning-sentiment-analyzer.cjs');
const { appendToProfile } = require('./swe-learning-profile-updater.cjs');

// Debug log file path
const DEBUG_LOG = path.join(__dirname, 'hook-debug.log');

/**
 * Parse JSONL transcript for learning activity
 * @param {string} transcriptPath - Path to transcript file
 * @returns {Promise<Object>} Learning activity summary
 */
async function parseLearningActivity(transcriptPath) {
  const result = {
    hasLearningActivity: false,
    topicsDiscussed: [],
    quizCount: 0,
    questionsAsked: [],
    skillInvoked: false,
    userMessages: [],
    // New: intelligent tracking
    quizResults: [],       // {topic, score, total, userAnswer}
    topicsLearned: [],     // Extracted topics with context
    insightfulQuestions: [], // Deep questions user asked
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
        processTranscriptEntry(entry, result);
      } catch {
        // Skip malformed lines
      }
    }
  } catch (err) {
    console.error(`[swe-learning] Transcript parse error: ${err.message}`);
  }

  return result;
}

/**
 * Process a single transcript entry
 * @param {Object} entry - Parsed JSON entry
 * @param {Object} result - Result object to update
 */
function processTranscriptEntry(entry, result) {
  // Check assistant messages for skill invocations and quiz patterns
  if (entry.message?.content && entry.message?.role === 'assistant') {
    for (const block of entry.message.content) {
      // Check for Skill tool invocation with sb skill (learn/explain commands)
      if (block.type === 'tool_use' && block.name === 'Skill') {
        const skill = block.input?.skill || '';
        const args = block.input?.args || '';

        // sb skill with learn/explain commands OR direct learn/explain skills
        const isSbLearning = skill === 'sb' && /^(learn|explain)\b/i.test(args);
        const isDirectLearning = skill === 'learn' || skill === 'explain';

        if (isSbLearning || isDirectLearning) {
          result.skillInvoked = true;
          result.hasLearningActivity = true;

          // Extract topic from args
          if (args) {
            // Remove 'learn ' or 'explain ' prefix to get actual topic
            const topic = args.replace(/^(learn|explain)\s*/i, '').trim();
            if (topic) {
              result.topicsDiscussed.push(topic);
            }
          }
        }
      }

      // Detect quiz patterns and extract quiz info from assistant text
      if (block.type === 'text' && typeof block.text === 'string') {
        const text = block.text;

        // Count quizzes
        if (text.includes('🤔') || text.includes('Quiz') || text.includes('Think About')) {
          result.quizCount++;
        }

        // Extract quiz results (✅ correct, ❌ incorrect patterns)
        // Look for patterns like "✅ Đúng rồi!" or "❌ Sai, vì..."
        const correctPatterns = text.match(/[✅✓]\s*(?:Đúng|Correct|Right|Chính xác)/gi);
        const incorrectPatterns = text.match(/[❌✗]\s*(?:Sai|Wrong|Incorrect|Chưa đúng)/gi);

        if (correctPatterns) {
          // Get topic from nearby context (look for bold text before the check)
          const topicMatch = text.match(/\*\*([^*]{3,30})\*\*.*?[✅✓]/);
          const context = topicMatch ? topicMatch[1].trim() : '';
          result.quizResults.push({ correct: true, context });
        }
        if (incorrectPatterns) {
          const topicMatch = text.match(/\*\*([^*]{3,30})\*\*.*?[❌✗]/);
          const context = topicMatch ? topicMatch[1].trim() : '';
          result.quizResults.push({ correct: false, context });
        }

        // NOTE: Topic extraction moved to skill (in-session Claude updates)
        // The Stop hook only tracks basic metrics. Intelligent topic extraction
        // requires full conversation context - handled by SKILL.md instructions.
        // See: Session Memory section in .claude/skills/sb/SKILL.md
      }
    }
  }

  // Collect user messages for sentiment analysis
  if (entry.message?.role === 'user' && entry.message?.content) {
    for (const block of entry.message.content) {
      if (block.type === 'text' && typeof block.text === 'string') {
        result.userMessages.push(block.text);

        // Detect learning-related questions
        const text = block.text.toLowerCase();
        const learningPatterns = [
          'giải thích', 'explain', 'tại sao', 'why',
          'how', 'như thế nào', 'what is', 'là gì'
        ];

        if (learningPatterns.some(p => text.includes(p))) {
          result.questionsAsked.push(block.text.slice(0, 100));
          result.hasLearningActivity = true;
        }

        // Detect insightful/deep questions (for "Questions Asked" section)
        const insightfulPatterns = [
          /bản chất|essence|fundamentally/i,
          /tại sao.{5,}lại/i,        // "tại sao X lại Y"
          /how does.{5,}work/i,
          /what.{5,}behind/i,
          /difference between/i,
          /so sánh|compare/i,
          /khi nào (dùng|cần|nên)/i, // "khi nào dùng X"
          /when (should|to use)/i,
        ];

        if (insightfulPatterns.some(p => p.test(block.text))) {
          const question = block.text.slice(0, 150).trim();
          if (!result.insightfulQuestions.includes(question)) {
            result.insightfulQuestions.push(question);
          }
        }
      }
    }
  }
}

/**
 * Main hook execution
 */
async function main() {
  // Debug: Log to file for verification
  fs.appendFileSync(DEBUG_LOG, `[${new Date().toISOString()}] Stop hook fired!\n`);
  console.error('[swe-learning] Stop hook fired!');

  try {
    const stdin = fs.readFileSync(0, 'utf-8').trim();
    const input = stdin ? JSON.parse(stdin) : {};

    // Debug: Log input received
    console.error(`[swe-learning] Input keys: ${Object.keys(input).join(', ')}`);

    const transcriptPath = process.env.CLAUDE_TRANSCRIPT_PATH || input.transcript_path;
    fs.appendFileSync(DEBUG_LOG, `  Transcript: ${transcriptPath || 'NOT FOUND'}\n`);
    console.error(`[swe-learning] Transcript path: ${transcriptPath || 'NOT FOUND'}`);

    // Parse transcript for learning activity
    const activity = await parseLearningActivity(transcriptPath);
    fs.appendFileSync(DEBUG_LOG, `  Learning activity: ${activity.hasLearningActivity}\n`);
    console.error(`[swe-learning] Learning activity detected: ${activity.hasLearningActivity}`);

    if (activity.hasLearningActivity) {
      // Analyze sentiment from user messages
      const sentiment = analyzeSentiment(activity.userMessages);

      // Update profile with activity + sentiment
      appendToProfile(activity, sentiment);

      // Log results
      console.error(`[swe-learning] Sentiment: ${sentiment.sentiment} (${sentiment.rating}/10)`);
      if (sentiment.likes.length > 0) {
        console.error(`[swe-learning] Likes: ${sentiment.likes.join(', ')}`);
      }
      if (sentiment.dislikes.length > 0) {
        console.error(`[swe-learning] Dislikes: ${sentiment.dislikes.join(', ')}`);
      }
    } else {
      console.error('[swe-learning] No learning activity detected, skipping profile update');
    }

    process.exit(0);
  } catch (error) {
    console.error(`[swe-learning] Hook error: ${error.message}`);
    process.exit(0);
  }
}

main();
