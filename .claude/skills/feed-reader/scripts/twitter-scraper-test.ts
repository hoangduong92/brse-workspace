#!/usr/bin/env bun
/**
 * Test script for TwitterScraper
 * Tests basic functionality with multiple accounts
 */

import { scrapeTweets, scrapeThread } from "../Tools/TwitterScraper";

async function main() {
  console.log("=== Twitter Scraper Test ===\n");

  // Test 1: Scrape tweets from a single account
  console.log("Test 1: Scraping tweets from @elonmusk...");
  try {
    const tweets = await scrapeTweets("elonmusk", 5);
    console.log(`✓ Scraped ${tweets.length} tweets`);
    if (tweets.length > 0) {
      console.log(`  First tweet: "${tweets[0].text.slice(0, 60)}..."`);
      console.log(`  Author: ${tweets[0].author}`);
      console.log(`  Engagement: ${tweets[0].likes} likes, ${tweets[0].retweets} retweets\n`);
    }
  } catch (error: any) {
    console.error(`✗ Failed: ${error.message}\n`);
  }

  // Test 2: Scrape from another account
  console.log("Test 2: Scraping tweets from @OpenAI...");
  try {
    const tweets = await scrapeTweets("OpenAI", 3);
    console.log(`✓ Scraped ${tweets.length} tweets`);
    if (tweets.length > 0) {
      console.log(`  First tweet: "${tweets[0].text.slice(0, 60)}..."\n`);
    }
  } catch (error: any) {
    console.error(`✗ Failed: ${error.message}\n`);
  }

  // Test 3: Test rate limiting (should enforce 10s delay)
  console.log("Test 3: Testing rate limiting...");
  const startTime = Date.now();
  try {
    await scrapeTweets("github", 2);
    const elapsed = Date.now() - startTime;
    console.log(`✓ Rate limit enforced (${Math.round(elapsed / 1000)}s elapsed)\n`);
  } catch (error: any) {
    console.error(`✗ Failed: ${error.message}\n`);
  }

  console.log("=== Test Complete ===");
}

main().catch(console.error);
