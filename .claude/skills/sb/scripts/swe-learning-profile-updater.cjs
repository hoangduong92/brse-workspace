#!/usr/bin/env node
/**
 * SWE Learning - Profile Updater Module
 *
 * Handles reading/writing learner profile with session history,
 * sentiment feedback, and teaching preferences.
 */
'use strict';

const fs = require('fs');
const path = require('path');

// Max entries to keep in tables
const MAX_FEEDBACK_ENTRIES = 10;
const MAX_SESSION_ENTRIES = 10;

// Default profile path for sb skill (relative to project root)
const DEFAULT_PROFILE_PATH = 'projects/solo-builder-12months/progress/learner-profile.md';

/**
 * Get profile path with cross-platform support
 * Uses CLAUDE_PROJECT_DIR (recommended) or CLAUDE_CWD for absolute paths
 * Falls back to default path for sb skill
 * @returns {string|null} Absolute path to learner profile, or null if not found
 */
function getProfilePath() {
  // Get project root - prefer CLAUDE_PROJECT_DIR per docs best practice
  const projectDir = process.env.CLAUDE_PROJECT_DIR || process.env.CLAUDE_CWD;

  if (!projectDir) {
    console.error('[swe-learning] No project directory found (CLAUDE_PROJECT_DIR or CLAUDE_CWD)');
    return null;
  }

  // Support custom path via env var (for flexibility/reuse)
  const relativePath = process.env.LEARNER_PROFILE_PATH || DEFAULT_PROFILE_PATH;

  return path.join(projectDir, relativePath);
}

/**
 * Get default profile template
 * @returns {string} Default markdown profile
 */
function getDefaultProfile() {
  return `# Learner Profile

> Persistent memory của SWE Learning Mentor
> Auto-updated mỗi khi Stop session có learning activity

---

## 📊 Overview

| Metric | Value |
|--------|-------|
| First session | - |
| Total sessions | 0 |
| Last active | - |

---

## 🎯 Learning Journey

### Topics Learned
<!-- Format: - [date] Topic: brief description -->

### In Progress
<!-- Topics đang học dở -->

### Queued
<!-- Topics user muốn học tiếp -->

---

## 💪 Strengths
<!-- Concepts user đã master -->

---

## 🔧 Areas to Improve
<!-- Concepts user còn yếu, cần review lại -->

---

## 📝 Quiz Performance

### Recent Quizzes
<!-- Format: - [date] Topic: score/total - notes -->

### Common Mistakes
<!-- Patterns of mistakes để focus review -->

---

## 💡 Learning Insights

### Preferences
<!-- How user learns best: examples, analogies, code-first... -->

### Questions Asked
<!-- Interesting questions user đã hỏi -->

---

## 😊 Teaching Feedback

### Satisfaction Trend
<!-- Auto-captured from implicit sentiment analysis -->
| Date | Rating | Sentiment | Summary |
|------|--------|-----------|---------|

### What Works Well
<!-- Teaching approaches user responds positively to -->

### Pain Points
<!-- Teaching approaches that frustrate user -->

### Suggested Adaptations
<!-- AI-generated suggestions based on feedback patterns -->

---

## 📅 Session History
<!-- Recent 10 sessions -->

| Date | Time | Topics | Notes |
|------|------|--------|-------|
`;
}

/**
 * Read current profile or create default
 * @returns {string|null} Profile content, or null if path not configured
 */
function readProfile() {
  const profilePath = getProfilePath();

  if (!profilePath) {
    return null;
  }

  if (fs.existsSync(profilePath)) {
    return fs.readFileSync(profilePath, 'utf-8');
  }

  console.error('[swe-learning] Profile not found, using default template');
  return getDefaultProfile();
}

/**
 * Write profile to file with error handling
 * @param {string} content - Profile content to write
 * @returns {boolean} Success status
 */
function writeProfile(content) {
  const profilePath = getProfilePath();

  try {
    // Ensure directory exists
    const dir = path.dirname(profilePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(profilePath, content, 'utf-8');
    return true;
  } catch (err) {
    console.error(`[swe-learning] Failed to write profile: ${err.message}`);
    return false;
  }
}

/**
 * Update overview stats in profile
 * @param {string} profile - Current profile content
 * @param {string} dateStr - Current date string
 * @param {string} timeStr - Current time string
 * @returns {string} Updated profile
 */
function updateOverviewStats(profile, dateStr, timeStr) {
  // Update session count
  const sessionsMatch = profile.match(/Total sessions \| (\d+)/);
  const currentSessions = sessionsMatch ? parseInt(sessionsMatch[1]) : 0;
  profile = profile.replace(/Total sessions \| \d+/, `Total sessions | ${currentSessions + 1}`);

  // Update last active
  profile = profile.replace(/Last active \| .*/, `Last active | ${dateStr} ${timeStr}`);

  // Set first session if not set
  if (profile.includes('First session | -')) {
    profile = profile.replace('First session | -', `First session | ${dateStr}`);
  }

  return profile;
}

/**
 * Find the end index of a section (before next ## or ### marker)
 * @param {string[]} lines - Array of lines
 * @returns {number} Index of section end (exclusive)
 */
function findSectionEnd(lines) {
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].startsWith('##')) {
      return i;
    }
  }
  return lines.length;
}

/**
 * Find the last table row index within a section
 * @param {string[]} lines - Array of lines
 * @param {number} endIdx - End of section (exclusive)
 * @returns {number} Index of last table row in section
 */
function findLastTableRowInSection(lines, endIdx) {
  let lastIdx = -1;
  for (let i = 0; i < endIdx; i++) {
    if (lines[i].startsWith('|')) {
      lastIdx = i;
    }
  }
  return lastIdx;
}

/**
 * Add sentiment feedback entry to profile
 * @param {string} profile - Current profile
 * @param {Object} sentiment - Sentiment analysis result
 * @param {string} dateStr - Current date
 * @returns {string} Updated profile
 */
function addSentimentFeedback(profile, sentiment, dateStr) {
  const feedbackMarker = '### Satisfaction Trend';
  const feedbackIdx = profile.indexOf(feedbackMarker);

  if (feedbackIdx === -1) return profile;

  const afterFeedback = profile.slice(feedbackIdx);
  const lines = afterFeedback.split('\n');

  // Find section end to avoid inserting into next section
  const sectionEnd = findSectionEnd(lines);
  const insertIdx = findLastTableRowInSection(lines, sectionEnd);
  if (insertIdx === -1) return profile;

  // Create feedback entry
  const emoji = sentiment.sentiment === 'positive' ? '😊' :
                sentiment.sentiment === 'negative' ? '😔' : '😐';
  const feedbackEntry = `| ${dateStr} | ${sentiment.rating}/10 | ${emoji} ${sentiment.sentiment} | ${sentiment.summary} |`;

  lines.splice(insertIdx + 1, 0, feedbackEntry);

  // Keep only last N feedback entries (excluding header rows)
  const dataLines = lines.filter((l, i) =>
    l.startsWith('|') && !l.includes('Date') && !l.includes('---')
  );
  if (dataLines.length > MAX_FEEDBACK_ENTRIES) {
    const firstDataIdx = lines.findIndex(l =>
      l.startsWith('|') && !l.includes('Date') && !l.includes('---')
    );
    if (firstDataIdx > 0) {
      lines.splice(firstDataIdx, 1);
    }
  }

  return profile.slice(0, feedbackIdx) + lines.join('\n');
}

/**
 * Update "What Works Well" section with likes
 * @param {string} profile - Current profile
 * @param {string[]} likes - Array of liked teaching styles
 * @returns {string} Updated profile
 */
function updateLikes(profile, likes) {
  if (likes.length === 0) return profile;

  const marker = '### What Works Well';
  const markerIdx = profile.indexOf(marker);
  if (markerIdx === -1) return profile;

  const endIdx = profile.indexOf('###', markerIdx + marker.length);
  const section = profile.slice(markerIdx, endIdx);
  let newSection = section;

  for (const like of likes) {
    const likeText = `- ${like}`;
    if (!section.includes(likeText)) {
      newSection = newSection.replace(marker, `${marker}\n${likeText}`);
    }
  }

  return profile.slice(0, markerIdx) + newSection + profile.slice(endIdx);
}

/**
 * Update "Pain Points" section with dislikes
 * @param {string} profile - Current profile
 * @param {string[]} dislikes - Array of disliked teaching styles
 * @returns {string} Updated profile
 */
function updateDislikes(profile, dislikes) {
  if (dislikes.length === 0) return profile;

  const marker = '### Pain Points';
  const markerIdx = profile.indexOf(marker);
  if (markerIdx === -1) return profile;

  const endIdx = profile.indexOf('###', markerIdx + marker.length);
  const section = profile.slice(markerIdx, endIdx);
  let newSection = section;

  for (const dislike of dislikes) {
    const dislikeText = `- ${dislike}`;
    if (!section.includes(dislikeText)) {
      newSection = newSection.replace(marker, `${marker}\n${dislikeText}`);
    }
  }

  return profile.slice(0, markerIdx) + newSection + profile.slice(endIdx);
}

/**
 * Add learned topics to "Topics Learned" section
 * @param {string} profile - Current profile
 * @param {Object} activity - Learning activity data
 * @param {string} dateStr - Current date
 * @returns {string} Updated profile
 */
function addTopicsLearned(profile, activity, dateStr) {
  const topics = [...new Set([...activity.topicsDiscussed, ...(activity.topicsLearned || [])])];
  if (topics.length === 0) return profile;

  const marker = '### Topics Learned';
  const markerIdx = profile.indexOf(marker);
  if (markerIdx === -1) return profile;

  // Find next section
  const nextSectionIdx = profile.indexOf('###', markerIdx + marker.length);
  const sectionEnd = nextSectionIdx > -1 ? nextSectionIdx : profile.length;
  const section = profile.slice(markerIdx, sectionEnd);

  let newSection = section;
  for (const topic of topics.slice(0, 3)) { // Max 3 topics per session
    // Skip if topic already exists (check case-insensitive)
    if (section.toLowerCase().includes(topic.toLowerCase())) continue;

    // Clean topic for display
    const cleanTopic = topic.replace(/[*_`]/g, '').slice(0, 50);
    const entry = `- [${dateStr}] **${cleanTopic}**`;

    // Insert after marker line and comment line
    const insertPoint = section.indexOf('\n', section.indexOf('<!--'));
    if (insertPoint > -1) {
      const insertIdx = section.indexOf('\n', insertPoint + 1);
      newSection = section.slice(0, insertIdx + 1) + entry + '\n' + section.slice(insertIdx + 1);
    }
  }

  return profile.slice(0, markerIdx) + newSection + profile.slice(sectionEnd);
}

/**
 * Add quiz results to "Recent Quizzes" section
 * @param {string} profile - Current profile
 * @param {Object} activity - Learning activity data
 * @param {string} dateStr - Current date
 * @returns {string} Updated profile
 */
function addQuizResults(profile, activity, dateStr) {
  const quizResults = activity.quizResults || [];
  if (quizResults.length === 0) return profile;

  const marker = '### Recent Quizzes';
  const markerIdx = profile.indexOf(marker);
  if (markerIdx === -1) return profile;

  // Find next section
  const nextSectionIdx = profile.indexOf('###', markerIdx + marker.length);
  const sectionEnd = nextSectionIdx > -1 ? nextSectionIdx : profile.length;
  const section = profile.slice(markerIdx, sectionEnd);

  // Calculate score from results
  const correct = quizResults.filter(r => r.correct).length;
  const total = quizResults.length;
  const emoji = correct === total ? '✅' : correct > 0 ? '⚠️' : '❌';

  // Get topic from topicsDiscussed first (more reliable), then quiz context
  let topic = activity.topicsDiscussed[0]?.slice(0, 30) ||
              quizResults[0]?.context?.slice(0, 30) ||
              'General';
  // Clean topic
  topic = topic.replace(/^[#🎯🤔💡📝✅❌⚠️\s]+/, '').trim();

  const entry = `- [${dateStr}] ${topic}: ${correct}/${total} ${emoji}`;

  // Insert after marker and comment
  const insertPoint = section.indexOf('\n', section.indexOf('<!--'));
  if (insertPoint > -1) {
    const insertIdx = section.indexOf('\n', insertPoint + 1);
    const newSection = section.slice(0, insertIdx + 1) + entry + '\n' + section.slice(insertIdx + 1);
    return profile.slice(0, markerIdx) + newSection + profile.slice(sectionEnd);
  }

  return profile;
}

/**
 * Add insightful questions to "Questions Asked" section
 * @param {string} profile - Current profile
 * @param {Object} activity - Learning activity data
 * @returns {string} Updated profile
 */
function addInsightfulQuestions(profile, activity) {
  const questions = activity.insightfulQuestions || [];
  if (questions.length === 0) return profile;

  const marker = '### Questions Asked';
  const markerIdx = profile.indexOf(marker);
  if (markerIdx === -1) return profile;

  // Find next section
  const nextSectionIdx = profile.indexOf('---', markerIdx);
  const sectionEnd = nextSectionIdx > -1 ? nextSectionIdx : profile.length;
  const section = profile.slice(markerIdx, sectionEnd);

  let newSection = section;
  for (const question of questions.slice(0, 2)) { // Max 2 per session
    // Skip if question already exists
    const shortQ = question.slice(0, 50);
    if (section.includes(shortQ)) continue;

    // Clean and format question
    const cleanQ = question.replace(/[*_`]/g, '').slice(0, 100);
    const entry = `- "${cleanQ}"`;

    // Insert after marker and comment
    const insertPoint = section.indexOf('\n', section.indexOf('<!--'));
    if (insertPoint > -1) {
      const insertIdx = section.indexOf('\n', insertPoint + 1);
      newSection = newSection.slice(0, insertIdx + 1) + entry + '\n' + newSection.slice(insertIdx + 1);
    }
  }

  return profile.slice(0, markerIdx) + newSection + profile.slice(sectionEnd);
}

/**
 * Add session to history table
 * @param {string} profile - Current profile
 * @param {Object} activity - Learning activity data
 * @param {Object} sentiment - Sentiment analysis result
 * @param {string} dateStr - Current date
 * @param {string} timeStr - Current time
 * @returns {string} Updated profile
 */
function addSessionHistory(profile, activity, sentiment, dateStr, timeStr) {
  const historyMarker = '## 📅 Session History';
  const historyIdx = profile.indexOf(historyMarker);

  if (historyIdx === -1) return profile;

  // Build topics string - combine both sources, clean garbage
  const garbagePattern = /^[#🎯🤔💡📝✅❌⚠️\s]+|^(Tại sao|Why|How|What|Bạn|Concept:)/i;
  const cleanTopics = [...new Set([...activity.topicsDiscussed, ...(activity.topicsLearned || [])])]
    .map(t => t.replace(garbagePattern, '').trim())
    .filter(t => t.length > 2 && t.length < 30);
  const topicsStr = cleanTopics.length > 0
    ? cleanTopics.slice(0, 2).join(', ').slice(0, 40)
    : 'general';

  // Build notes
  const notes = [];
  if (activity.skillInvoked) notes.push('/learn');
  if (activity.quizCount > 0) notes.push(`${activity.quizCount}Q`);
  // Add quiz score if available
  const quizResults = activity.quizResults || [];
  if (quizResults.length > 0) {
    const correct = quizResults.filter(r => r.correct).length;
    notes.push(`${correct}/${quizResults.length}✓`);
  }
  notes.push(`${sentiment.rating}/10`);

  const sessionEntry = `| ${dateStr} | ${timeStr} | ${topicsStr} | ${notes.join(', ')} |`;

  const afterHistory = profile.slice(historyIdx);
  const lines = afterHistory.split('\n');

  // Find section end to avoid inserting into next section
  const sectionEnd = findSectionEnd(lines);
  const insertIdx = findLastTableRowInSection(lines, sectionEnd);
  if (insertIdx === -1) return profile;

  lines.splice(insertIdx + 1, 0, sessionEntry);

  // Keep only last N sessions (header + separator + data rows)
  const tableLines = lines.filter(l => l.startsWith('|') && !l.includes('---'));
  if (tableLines.length > MAX_SESSION_ENTRIES + 1) { // +1 for header
    const firstDataIdx = lines.findIndex(l =>
      l.startsWith('|') && !l.includes('Date') && !l.includes('Time') && !l.includes('---')
    );
    if (firstDataIdx > 0) {
      lines.splice(firstDataIdx, 1);
    }
  }

  return profile.slice(0, historyIdx) + lines.join('\n');
}

/**
 * Main function to append session data to profile
 * @param {Object} activity - Learning activity from transcript
 * @param {Object} sentiment - Sentiment analysis result
 * @returns {boolean} Success status
 */
function appendToProfile(activity, sentiment) {
  if (!activity.hasLearningActivity) {
    return false;
  }

  // Check if profile path is configured
  const profilePath = getProfilePath();
  if (!profilePath) {
    return false;
  }

  const now = new Date();
  const dateStr = now.toISOString().split('T')[0];
  const timeStr = now.toTimeString().split(' ')[0].slice(0, 5);

  let profile = readProfile();
  if (!profile) {
    return false;
  }

  // Update all sections
  profile = updateOverviewStats(profile, dateStr, timeStr);
  profile = addSentimentFeedback(profile, sentiment, dateStr);
  profile = updateLikes(profile, sentiment.likes);
  profile = updateDislikes(profile, sentiment.dislikes);
  profile = addSessionHistory(profile, activity, sentiment, dateStr, timeStr);

  // NOTE: Topic/quiz/questions updates now handled by skill (in-session Claude)
  // The skill has full conversation context for intelligent updates.
  // Hook only updates: session count, last active, sentiment, session history.
  // See: Session Memory section in .claude/skills/sb/SKILL.md

  // Write updated profile
  const success = writeProfile(profile);

  if (success) {
    const sessionsMatch = profile.match(/Total sessions \| (\d+)/);
    const sessionCount = sessionsMatch ? sessionsMatch[1] : '?';
    console.log(`[swe-learning] Profile updated: session ${sessionCount}, rating ${sentiment.rating}/10`);
  }

  return success;
}

module.exports = {
  getProfilePath,
  getDefaultProfile,
  readProfile,
  writeProfile,
  appendToProfile,
};
