#!/usr/bin/env bun
/**
 * TwitterScraper - DIY Twitter scraper using Puppeteer
 * Budget: $0 (no API), target: ~80% uptime
 *
 * Usage:
 *   scrapeTweets("elonmusk", 10) - Get latest 10 tweets
 *   scrapeThread("https://x.com/user/status/123") - Get thread
 */

import puppeteer, { Browser, Page } from "puppeteer";
import { extractTweetsLogic } from "./twitter-dom-extractor.ts";
import type { Tweet } from "./twitter-dom-extractor.ts";
import { retryWithBackoff, enforceRateLimit, handleRateLimit } from "./twitter-retry-handler.ts";

export type { Tweet };

const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36';

async function launchBrowser(): Promise<Browser> {
  return await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
    ],
  });
}

async function extractTweetsFromPage(page: Page): Promise<Tweet[]> {
  return await page.evaluate(extractTweetsLogic);
}

async function handleLoginWall(page: Page): Promise<void> {
  const loginWallExists = await page.$('[data-testid="login"]');
  if (loginWallExists) {
    console.log('Login wall detected, clearing cookies and retrying...');
    await page.deleteCookie(...(await page.cookies()));
    await page.reload({ waitUntil: 'networkidle2' });
    await page.waitForSelector('[data-testid="tweet"]', { timeout: 10000 });
  }
}

/**
 * Scrape latest N tweets from a Twitter/X user profile
 */
export async function scrapeTweets(handle: string, count = 10): Promise<Tweet[]> {
  await enforceRateLimit();

  const scrape = async (): Promise<Tweet[]> => {
    let browser: Browser | null = null;
    try {
      browser = await launchBrowser();
      const page = await browser.newPage();

      await page.setViewport({ width: 1280, height: 800 });
      await page.setUserAgent(USER_AGENT);

      const url = `https://twitter.com/${handle}`;
      console.log(`Navigating to ${url}...`);

      await page.goto(url, {
        waitUntil: 'networkidle2',
        timeout: 30000,
      });

      // Wait for tweets to load or handle login wall
      try {
        await page.waitForSelector('[data-testid="tweet"]', { timeout: 10000 });
      } catch (error) {
        await handleLoginWall(page);
      }

      const tweets = await extractTweetsFromPage(page);
      console.log(`Extracted ${tweets.length} tweets from ${handle}`);

      return tweets.slice(0, count);
    } catch (error: any) {
      console.error('Error scraping tweets:', error?.message || error);
      // Handle rate limit separately to avoid blocking browser cleanup
      try {
        await handleRateLimit(error);
      } catch {
        // handleRateLimit always throws, just re-throw original error
      }
      throw error;
    } finally {
      if (browser) {
        try {
          await browser.close();
        } catch (closeError) {
          console.error('Error closing browser:', closeError);
        }
      }
    }
  };

  try {
    return await retryWithBackoff(scrape);
  } catch (error) {
    console.error(`Failed to scrape tweets from ${handle} after retries`);
    return [];
  }
}

/**
 * Scrape a Twitter thread from a tweet URL
 */
export async function scrapeThread(tweetUrl: string): Promise<Tweet[]> {
  await enforceRateLimit();

  const scrape = async (): Promise<Tweet[]> => {
    let browser: Browser | null = null;
    try {
      browser = await launchBrowser();
      const page = await browser.newPage();

      await page.setViewport({ width: 1280, height: 800 });
      await page.setUserAgent(USER_AGENT);

      console.log(`Navigating to ${tweetUrl}...`);
      await page.goto(tweetUrl, {
        waitUntil: 'networkidle2',
        timeout: 30000,
      });

      await page.waitForSelector('[data-testid="tweet"]', { timeout: 10000 });

      const tweets = await extractTweetsFromPage(page);
      console.log(`Extracted ${tweets.length} tweets from thread`);

      return tweets;
    } catch (error: any) {
      console.error('Error scraping thread:', error?.message || error);
      // Handle rate limit separately to avoid blocking browser cleanup
      try {
        await handleRateLimit(error);
      } catch {
        // handleRateLimit always throws, just re-throw original error
      }
      throw error;
    } finally {
      if (browser) {
        try {
          await browser.close();
        } catch (closeError) {
          console.error('Error closing browser:', closeError);
        }
      }
    }
  };

  try {
    return await retryWithBackoff(scrape);
  } catch (error) {
    console.error(`Failed to scrape thread ${tweetUrl} after retries`);
    return [];
  }
}

// CLI interface
if (import.meta.main) {
  const [, , command, ...args] = process.argv;

  switch (command) {
    case "scrape":
      if (!args[0]) {
        console.error("Usage: bun run TwitterScraper.ts scrape <handle> [count]");
        process.exit(1);
      }
      const count = parseInt(args[1]) || 10;
      scrapeTweets(args[0], count)
        .then(tweets => {
          console.log(JSON.stringify(tweets, null, 2));
        })
        .catch(err => {
          console.error(err.message);
          process.exit(1);
        });
      break;

    case "thread":
      if (!args[0]) {
        console.error("Usage: bun run TwitterScraper.ts thread <tweet_url>");
        process.exit(1);
      }
      scrapeThread(args[0])
        .then(tweets => {
          console.log(JSON.stringify(tweets, null, 2));
        })
        .catch(err => {
          console.error(err.message);
          process.exit(1);
        });
      break;

    default:
      console.log(`
TwitterScraper - DIY Twitter/X scraper

Usage:
  bun run TwitterScraper.ts <command> [args]

Commands:
  scrape <handle> [count]  Scrape tweets from user profile (default: 10)
  thread <tweet_url>       Scrape a thread from tweet URL

Examples:
  bun run TwitterScraper.ts scrape karpathy 5
  bun run TwitterScraper.ts thread "https://twitter.com/user/status/123"
`);
      break;
  }
}
