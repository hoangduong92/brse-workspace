#!/usr/bin/env node
/**
 * SWE Learning - Sentiment Analyzer Module
 *
 * Pattern-based sentiment analysis for Vietnamese + English messages.
 * No API calls needed - fast local processing.
 */
'use strict';

// Sentiment scoring thresholds
const THRESHOLDS = {
  HIGH_POSITIVE: 3,
  HIGH_NEGATIVE: -3,
  BASE_RATING: 5,
  MAX_RATING: 10,
  MIN_RATING: 1,
  HIGH_WEIGHT: 3,
  MEDIUM_WEIGHT: 1,
};

// Sentiment patterns (Vietnamese + English)
const SENTIMENT_PATTERNS = {
  positive: {
    high: [
      /amazing|incredible|perfect|excellent|tuyệt vời|hay quá|quá đỉnh|cảm ơn nhiều/i,
      /now i (understand|get it)|giờ (tôi|mình) hiểu rồi|à ra vậy|ồ hay/i,
      /this is (great|helpful|exactly)|đúng rồi|chính xác/i,
    ],
    medium: [
      /thanks|cảm ơn|ok got it|hiểu rồi|được rồi|good|tốt/i,
      /make sense|hợp lý|clear|rõ ràng/i,
    ]
  },
  negative: {
    high: [
      /wtf|what the|confused|still (don't|không) (understand|hiểu)/i,
      /không hiểu|khó quá|phức tạp quá|chán|bực/i,
      /wrong|sai rồi|không đúng|lại lỗi/i,
      /too (fast|slow|long|complicated)|quá (nhanh|chậm|dài|phức tạp)/i,
    ],
    medium: [
      /hmm|uh|wait|chờ|nhưng mà|sao lại/i,
      /not (quite|really)|chưa rõ|hơi khó/i,
    ]
  },
  neutral: [
    /^(ok|yes|no|tiếp|continue|next)$/i,
    /^[0-9]+$/,
  ]
};

// Teaching style preference patterns
const STYLE_PATTERNS = {
  likes: {
    examples: /ví dụ (hay|tốt|rõ)|good example|clear example/i,
    analogies: /so sánh (hay|dễ hiểu)|great analogy|like the comparison/i,
    stepByStep: /step by step|từng bước|dễ theo/i,
    interactive: /quiz (hay|thích)|like the questions|câu hỏi hay/i,
  },
  dislikes: {
    tooFast: /quá nhanh|too fast|slow down|chậm lại/i,
    tooSlow: /quá chậm|too slow|biết rồi|already know/i,
    tooAbstract: /quá trừu tượng|too abstract|cần ví dụ|need example/i,
    tooDetailed: /quá chi tiết|too detailed|tóm tắt|summarize/i,
  }
};

/**
 * Analyze sentiment from user messages
 * @param {string[]} userMessages - Array of user message texts
 * @returns {Object} Sentiment analysis result
 */
function analyzeSentiment(userMessages) {
  const result = {
    rating: THRESHOLDS.BASE_RATING,
    sentiment: 'neutral',
    confidence: 0.5,
    summary: '',
    likes: [],
    dislikes: [],
  };

  let positiveScore = 0;
  let negativeScore = 0;
  let totalSignals = 0;

  for (const msg of userMessages) {
    // Check positive patterns
    for (const pattern of SENTIMENT_PATTERNS.positive.high) {
      if (pattern.test(msg)) {
        positiveScore += THRESHOLDS.HIGH_WEIGHT;
        totalSignals++;
      }
    }
    for (const pattern of SENTIMENT_PATTERNS.positive.medium) {
      if (pattern.test(msg)) {
        positiveScore += THRESHOLDS.MEDIUM_WEIGHT;
        totalSignals++;
      }
    }

    // Check negative patterns
    for (const pattern of SENTIMENT_PATTERNS.negative.high) {
      if (pattern.test(msg)) {
        negativeScore += THRESHOLDS.HIGH_WEIGHT;
        totalSignals++;
      }
    }
    for (const pattern of SENTIMENT_PATTERNS.negative.medium) {
      if (pattern.test(msg)) {
        negativeScore += THRESHOLDS.MEDIUM_WEIGHT;
        totalSignals++;
      }
    }

    // Check style preferences
    for (const [style, pattern] of Object.entries(STYLE_PATTERNS.likes)) {
      if (pattern.test(msg) && !result.likes.includes(style)) {
        result.likes.push(style);
      }
    }
    for (const [style, pattern] of Object.entries(STYLE_PATTERNS.dislikes)) {
      if (pattern.test(msg) && !result.dislikes.includes(style)) {
        result.dislikes.push(style);
      }
    }
  }

  // Calculate final sentiment
  if (totalSignals === 0) {
    result.sentiment = 'neutral';
    result.rating = THRESHOLDS.BASE_RATING;
    result.confidence = 0.3;
    result.summary = 'No clear sentiment detected';
  } else {
    const netScore = positiveScore - negativeScore;
    result.confidence = Math.min(0.9, 0.5 + (totalSignals * 0.1));

    if (netScore > THRESHOLDS.HIGH_POSITIVE) {
      result.sentiment = 'positive';
      result.rating = Math.min(THRESHOLDS.MAX_RATING, 7 + Math.floor(netScore / 2));
      result.summary = 'User seems satisfied with teaching';
    } else if (netScore < THRESHOLDS.HIGH_NEGATIVE) {
      result.sentiment = 'negative';
      result.rating = Math.max(THRESHOLDS.MIN_RATING, 4 + Math.floor(netScore / 2));
      result.summary = 'User shows signs of frustration';
    } else if (netScore > 0) {
      result.sentiment = 'positive';
      result.rating = 6;
      result.summary = 'Mild positive signals';
    } else if (netScore < 0) {
      result.sentiment = 'negative';
      result.rating = 4;
      result.summary = 'Mild negative signals';
    } else {
      result.sentiment = 'neutral';
      result.rating = THRESHOLDS.BASE_RATING;
      result.summary = 'Mixed or neutral signals';
    }
  }

  return result;
}

module.exports = {
  analyzeSentiment,
  SENTIMENT_PATTERNS,
  STYLE_PATTERNS,
  THRESHOLDS,
};
